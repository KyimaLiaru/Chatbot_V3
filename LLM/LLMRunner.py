from lib2to3.pygram import pattern_grammar

from attr.validators import instance_of
from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sqlalchemy.dialects.postgresql import psycopg2
from sqlalchemy.orm import Session

import json
import re

from Common.CallREST import sendRequest
from Common.GetErrorMessage import GetErrorMessage
from Common.FormatJSON import extractJsonKeys, formatJson
from Common.CallLLM import queryLLM
from Common.DetectLanguage import detectlanguage

import Data.ChatbotDB as repo

from LLM.RAGBuilder import loadManual, loadApiSpecs
from LLM.Prompt import (
    category_prompt,
    product_prompt,
    general_prompt,
    policy_intent_prompt,
    policy_api_mapping_prompt,
    policy_parameter_prompt,
    policy_result_keys_format_prompt,
    policy_additional_messages,
    translate_sentences
)



manualVectorstore = loadManual()
apiSpecsVectorstore = loadApiSpecs()

# ─────────────────────────────────────────────────────────────────────────────

def queryCategory(db: Session, query: str):
    intent_list = repo.getIntentList(db)

    prompt = category_prompt(intent_list, query)
    category_result = queryLLM(prompt)

    category = category_result.get("category", "")
    intent = category_result.get("intent", "")

    return intent, category

    # if category.find("product") == 0:
    #     return intent, "product"
    # elif category.find("policy") == 0:
    #     return intent, "policy"
    # else:
    #     return intent, "general"

# ─────────────────────────────────────────────────────────────────────────────

def queryManual(query: str, lang: str):
    docs = manualVectorstore.similarity_search(query, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = product_prompt(context, query, lang)
    # TODO: intent 수정 필요
    return queryLLM(prompt).get("response")

# ─────────────────────────────────────────────────────────────────────────────

def queryApi(db: Session, query: str, intent: str, lang: str):
    # ------------ STEP 1 ------------
    # Find the most suitable API information to call from the list
    # --------------------------------
    print("Chat.ONE | ==== STEP 1 ====")
    # Fetch top 10 matching API from the ChromaDB

    search = re.sub(r'[_\-]+', ' ', intent).strip()

    api_list_docs = apiSpecsVectorstore.similarity_search(search, k=10)
    api_list_context = "\n\n".join([doc.page_content for doc in api_list_docs])

    # Select the best API to call
    second_prompt = policy_api_mapping_prompt(api_list_context, intent)
    selected_api_output = queryLLM(second_prompt)

    # Extract API Information
    url = selected_api_output.get("url", "")
    method = selected_api_output.get("method", "")
    parameters = selected_api_output.get("param", [])
    body = selected_api_output.get("body", [])

    print(f"Chat.ONE | Selected API Info: url = {url}, method = {method}, parameters = {parameters}, body = {body}")

    # ------------ STEP 2 ------------
    # Check for missing required parameters
    # --------------------------------
    print("Chat.ONE | ==== STEP 2 ====")
    # Get Pattern RegEx from DB
    pattern_map = repo.getPatternMap(db)

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
            api_call_result = sendRequest(url, method, body if body else None)
        except Exception as e:
            # If any form of exception is raised, return the error message
            return GetErrorMessage(e)[1]
    # If some required parameters are missing, return message looking for additional parameters or clarifications, if not send error message
    else:
        param_check_message = param_check.get("message", "")
        if param_check_message == "":
            return "Chat.ONE | Internal server error occurred, please try again."
        return param_check_message


    # ------------ STEP 3 ------------
    # Format the Fire.ONE API output for easy readability
    # --------------------------------
    print("Chat.ONE | ==== STEP 3 ====")
    # api_call_result_json = json.dumps(api_call_result, ensure_ascii=False, indent=2)
    json_keys_list = extractJsonKeys(api_call_result)
    print(f"JSON KEYS = {json_keys_list}")

    # Re-format the api result JSON keys into easily understandable word phrases
    api_name_context = selected_api_output.get('name', '')
    fourth_prompt = policy_result_keys_format_prompt(api_name_context, json_keys_list, "")
    reformated_json_keys = queryLLM(fourth_prompt)

    reformatted_keys_list = extractJsonKeys(reformated_json_keys)

    # Format the final JSON based on the API Result and Word Phrases.
    reformatted_result = "\n".join(formatJson(api_call_result, reformatted_keys_list))

    # ------------ STEP 4 ------------
    # Add starting/closing messages in front of/after the API result.
    # --------------------------------
    print("Chat.ONE | ==== STEP  4====")
    message_result = ["Here is the detail for your request:", reformatted_result, "Feel free to ask me any other questions."]

    fifth_prompt = policy_additional_messages(query, reformatted_result, lang)
    # message_result = queryLLM(fifth_prompt)
    message_result = queryLLM(fifth_prompt).get("result")
    message_result[1] = reformatted_result


    result = "\n\n".join(message_result)
    # return message_result
    return result


# ─────────────────────────────────────────────────────────────────────────────

def queryGeneral(query: str, lang: str):
    prompt = general_prompt(query, lang)
    return queryLLM(prompt).get("response")

# ─────────────────────────────────────────────────────────────────────────────

def translateSentence(query, lang):
    prompt = translate_sentences(query, lang)
    result = queryLLM(prompt).get("response")
    return result