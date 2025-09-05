from attr.validators import instance_of
from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sqlalchemy.dialects.postgresql import psycopg2

import json

from Common.CallREST import send_request
from Common.GetErrorMessage import GetErrorMessage
from Common.FormatJSON import format_json
from Common.CallLLM import queryLLM
from Common.DetectLanguage import detectlanguage

from Prompt import (
    category_prompt,
    product_prompt,
    general_prompt,
    policy_intent_prompt,
    policy_api_mapping_prompt,
    policy_parameter_prompt,
    policy_result_keys_format_prompt,
    policy_additional_messages
)

from RAGBuilder import loadManual, loadApiSpecs

manualVectorstore = loadManual()
apiSpecsVectorstore = loadApiSpecs()

# ─────────────────────────────────────────────────────────────────────────────

def queryManual(query: str, lang: str) -> str:
    docs = manualVectorstore.similarity_search(query, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = product_prompt(context, query, lang)
    return queryLLM(prompt).get("response")

# ─────────────────────────────────────────────────────────────────────────────


def queryApi(query: str, lang: str) -> str:
    # ------------ STEP 1 ------------
    # Get the list of known intents
    # --------------------------------
    """
    임시 주석처리 -- start
    """
    # try:
    #     api_response = call_api.get_call("ARGOS_CHATBOT/admin/getIntentList")
    #     intent_list = []
    #     for item in api_response.get("data", []):
    #         intent_list.append(item["intent"])
    # except Exception as e:
    #     return get_error_message(e)

    intent_list = ['search_blacklist_policy', 'test_intent', 'search_firewall_policy', 'search_firewall_policy_detail', 'change_password', 'create_firewall_policy', 'get_admin_setting']

    # Analyze the intent and extract keywords
    first_prompt = policy_intent_prompt(intent_list, query)
    dictionary_output = queryLLM(first_prompt)

    print(dictionary_output)

    # Keep the output for saving dictionary info into DB later
    # TODO: Save the extracted keywords to the Database

    intent = dictionary_output.get("intent", "")
    dictionary = dictionary_output.get("keywords", "")

    print(f"✅ Intent Detected: {intent}")
    """
    임시 주석처리 -- end
    """
    # ------------ STEP 2 ------------
    # Find the most suitable API information to call from the list
    # --------------------------------

    # Fetch top 10 matching API from the ChromaDB
    api_list_docs = api_vectorstore.similarity_search(query, k=10)
    api_list_context = "\n\n".join([doc.page_content for doc in api_list_docs])

    # Select the best API to call
    second_prompt = policy_api_mapping_prompt(api_list_context, intent)
    selected_api_output = queryLLM(second_prompt)

    # Extract API Information
    url = selected_api_output.get("url", "")
    method = selected_api_output.get("method", "")
    parameters = selected_api_output.get("param", [])
    body = selected_api_output.get("body", [])

    print(f"📌 Selected API Info: url = {url}, method = {method}, parameters = {parameters}, body = {body}")

    # ------------ STEP 3 ------------
    # Check for missing required parameters
    # --------------------------------

    # Get Pattern RegEx from Chat.ONE API
    try:
        pattern_map = call_api.send_request("ARGOS_CHATBOT/admin/getPatternMap", "Get")
        # print(json.dumps(pattern_map, ensure_ascii=False, indent=2))
    except Exception as e:
        return get_error_message(e)

    # Check if any required parameters are missing
    third_prompt = policy_parameter_prompt(selected_api_output, query, pattern_map, lang)
    param_check = queryLLM(third_prompt)

    # If all required parameters are provided, continue to fetch information from Fire.ONE API
    param_check_result = param_check.get("result")
    api_call_result = ""
    if param_check_result:
        try:
            # Try GET Request first
            url += param_check.get("param", "")
            body = param_check.get("body", "")
            api_call_result = send_request(url, method, body if body else None)
        except Exception as e:
            # If any form of exception is raised, return the error message
            return get_error_message(e)[1]
    # If some required parameters are missing, return message looking for additional parameters or clarifications, if not send error message
    else:
        param_check_message = param_check.get("message", "")
        if param_check_message == "":
            return "❌ Internal server error occurred, please try again."
        return param_check_message


    # ------------ STEP 4 ------------
    # Format the Fire.ONE API output for easy readability
    # --------------------------------

    # api_call_result_json = json.dumps(api_call_result, ensure_ascii=False, indent=2)
    json_keys_list = extract_json_keys(api_call_result)

    # Re-format the api result JSON keys into easily understandable word phrases
    api_name_context = selected_api_output.get('name', '')
    fourth_prompt = policy_result_keys_format_prompt(api_name_context, json_keys_list, "")
    reformated_json_keys = queryLLM(fourth_prompt)

    # Format the final JSON based on the API Result and Word Phrases.
    reformatted_result = "\n".join(format_json(api_call_result, reformated_json_keys))

    # ------------ STEP 5 ------------
    # Add starting/closing messages in front of/after the API result.
    # --------------------------------

    message_result = ["Here is the detail for your request:", reformatted_result, "Feel free to ask me any other questions."]

    fifth_prompt = policy_additional_messages(query, reformatted_result, lang)
    # message_result = queryLLM(fifth_prompt)
    message_result = queryLLM(fifth_prompt).get("result")
    message_result[1] = reformatted_result

    # return message_result
    return "\n\n".join(message_result)


# ─────────────────────────────────────────────────────────────────────────────

def queryGeneral(query: str, lang: str) -> str:
    prompt = general_prompt(query, lang)
    return queryLLM(prompt).get("response")

# ─────────────────────────────────────────────────────────────────────────────

def queryCategory(query: str) -> str:
    """Uses Mistral via Ollama to classify the user's intent"""
    docs = manualVectorstore.similarity_search(query, k=5)
    context = "\n".join([doc.page_content for doc in docs])
    # print("🔍 Category: ", context)

    prompt = category_prompt(query)

    result = queryLLM(prompt)
    # print(result)
    category = result.get("category", "")

    if category.find("product") == 0:
        return "product"
    elif category.find("policy") == 0:
        return "policy"
    else:
        return "general"