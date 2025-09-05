# ─────────────────────────────────────────────────────────────────────────────
#    - Prompt for categorizing the user input into product/policy/general -
# ─────────────────────────────────────────────────────────────────────────────
def general_prompt(query, lang):
    return f"""
    You are a professional cybersecurity AI assistant. Answer the user's general security question below.
    Answer in {'Korean' if lang == 'ko' else 'English'}.

    ### Output Format
    {{
        "response": Your response here
    }}

    ### User Question
    Now process this user question.
    {query}    
    """


# ─────────────────────────────────────────────────────────────────────────────
#    - Prompt for categorizing the user input into product/policy/general -
# ─────────────────────────────────────────────────────────────────────────────
def category_prompt(query: str) -> str:
    return f"""
    You are an intent classification assistant. Classify the user's question into one of the following three categories based on its purpose and content.

    ### Categories:
    Case 1. product: Questions about how to use BreezeWay FIRE.One. This includes:
        - Explanations of menu, functions, or screens
        - Location of pages with specific features or information
        These are about **how the system works**, not what data it contains.
    Case 2. policy: Questions that involve interactions with the database. This includes:
        - Listing, searching, or querying firewall or security policies
        - Asking for policy details or approval status
        - Creating or modifying application or approval requests
        - Asking for application info, account, user, or specific values
        - Modifying configurations
        - Or asking you to do any of the tasks above
        These actions are **data-oriented questions** and usually require database or system queries.
    Case 3. general: Other questions related to cybersecurity concepts, not specific to the product or its data. Return general if and only if the user input can not be categorized to case 1 or case 2.

    ### Output Format:
    Provide your answer in this JSON format:
    {{
        "category": (One of [product, policy, general]),
        "explanation": (Your answer goes here.) 
    }}

    ### Example:
    Here are some examples for classifying the user's intent:
        **Example 1**
        Question: "Where can I see the list of firewall policy requests?"
        -> Output:
        {{
          "category": "product",
          "explanation": "The user is asking where to locate the page or menu that shows firewall policies, not requesting the data itself."
        }}

        **Example 2**
        Question: "Can you give me the list of firewall policy requests?"
        -> Output:
        {{
          "category": "policy",
          "explanation": "The user is directly requesting system data (a list of firewall policies)."
        }}

        **Example 3**
        Question: "What is a firewall?"
        -> Output:
        {{
          "category": "general",
          "explanation": "This is a general cybersecurity question unrelated to the system."
        }}

    Now classify this question:
    {query}
    """


# ─────────────────────────────────────────────────────────────────────────────
#      - Prompt for generating an answer for product related questions -
# ─────────────────────────────────────────────────────────────────────────────

def product_prompt(context: str, query: str, lang: str) -> str:
    return f"""You are Fire.ONE product assistant. Based on the following product documentation, answer the user's question below.
    If the product documentation does not include any related information about user question, do not make up the answer and tell them you don't know about it. 
    Answer in {'Korean' if lang == 'ko' else 'English'}.

    ### Product Documentation
    {context}

    ### Output Format
    {{
        "response": Your response here
    }}

    ### User Question
    Now process this user question.
    \"\"\"{query}\"\"\"
    """


# ─────────────────────────────────────────────────────────────────────────────
#   - Prompt for extracting the intent and keywords from the user question -
#           The result will be saved in a database for offline use.
# ─────────────────────────────────────────────────────────────────────────────

def policy_intent_prompt(context, query: str) -> str:
    # {context}
    #

    return f"""
    You are an intelligent assistant that analyzes user messages and classifies their intent.

    ### Here is a list of known intents:
    {str(context)}

    ### Your job:
    Case 1: If the user's message is semantically close to one of the known intents, return the most relevant intent name from the list as-is.  
        - The match does not need to be exact.  
        - If the message can reasonably be understood as a subtype or sub-topic of an existing intent, return that existing intent.
        - Do NOT choose a general one if a more accurate subtype intent exists.

    Case 2: If the message does not meaningfully relate to any known intent, generate a new intent name in snake_case format.
        - Only create a new intent when the message introduces a clearly different purpose or topic not covered by the known intents.
        - The name must describe the message's intent clearly, but not over specific.
        - The name must be clear and consistent with the known intent naming style.
        - Use relevant English keywords extracted from the message.
        - IMPORTANT: Extract important keywords or phrases only from the message that represent the intent, and do not make up any keywords.
            - Return the keywords as a single lowercase line separated by **one whitespace only** (no commas, no quotes).
            - Remove stopwords like "can", "please", "I", etc.
            - IMPORTANT: Replace any detailed or specific data into capitalized token tags surrounded by < and > using the following rules:
                - `<IPP>` — IP address with port (e.g. 192.168.0.1:443)
                - `<IP>` — IP address only
                - `<Port>` — numeric port only
                - `<FIQ>`, `<BWAY>`, `<R>` — Application number with type code followed by a 17-digit timestamp (e.g. FIQ20250704134526432)
                - `<URL>` — Any form of URL (e.g. https://..., www..., google.com/...)

    ### Output Format:
    In case 1, only return the intent name.
    In case 2, return the result in the following JSON format:
    {{
      "intent": "<intent_name>",
      "keywords": "<keyword1> <keyword2> <keyword3> ..."
    }}

    ### Example
    Here are some examples for case 2:
        - User Message: "Can you give me a list of blacklist policies?"
        -> Output:
        {{
          "intent": "search_blacklist_policy",
          "keywords": "list blacklist policies"
        }}

        - User Message: "Can you give me a detailed information about FIQ20250708115117463?"
        -> Output:
        {{
          "intent": "search_firewall_policy_detail",
          "keywords": "detailed information <FIQ>"
        }}

        - User Message: "Can you tell me the duration of FIQ20250708115117463?"
        -> Output:
        {{
          "intent": "search_firewall_policy_detail",
          "keywords": "duration <FIQ>"
        }}

    Now process this user message. Make sure to always return the result in JSON format. Do not add any additional explanations.
    \"\"\"{query}\"\"\"
    """


# ─────────────────────────────────────────────────────────────────────────────
#              - Prompt for mapping intent to appropriate APIs -
# ─────────────────────────────────────────────────────────────────────────────

def policy_api_mapping_prompt(context: str, query: str) -> str:
    return f"""You are a helpful assistant. Based on the following Fire.ONE API Reference information, select the best API that matches the intent.\n


    ### Fire.ONE API Reference
    {str(context)}

    ### Output Format:
    - Refer to the parameters.type field in the API Reference documentation, and correctly label each parameter to their corresponding section in the result.
    - After selecting the top matching API reference, always keep the list of required parameters as it is stated in the reference even though the required field is labeled as "false".
    - If there are no "body" or "param" parameters required, simply return an empty Array.
    - DO NOT invent any body fields or parameters.
    - Return the result in the following JSON format according to appropriate cases, without additional explanations.

    -> Output (Replace the parentheses in body and param fields with actual data.):
    {{
        "name": "(full api_name_en)",
        "url": "(API Url)",
        "method": "(HTTP Method)",
        "body: [{{"key":, "datatype": , "required": , "description": , "field": "[{{(List of parameters, if exists.)}}]"}}]
        "param": [{{"key": , "required": , "description": }}]
    }}

    Now process user message. Do NOT add any additional explanations.
    \"\"\"{query}\"\"\"
    """


# ─────────────────────────────────────────────────────────────────────────────
#           - Prompt for finding missing required parameters -
# ─────────────────────────────────────────────────────────────────────────────

def policy_parameter_prompt(context, query: str, pattern_map: str, lang: str) -> str:
    return f"""You will be given a list of information about body fields and parameters required for creating a Http Request to the API.\n
    Your job is to:
    1) analyze the API information to find out the required parameters,
    2) check whether all \"required\" fields are provided in the user message.
    2-1) The name of the parameter provided by the user does not need to be exactly the same to the required parameter name. Try to match similar parameters based on the API information provided. 
    2-2) If any required fields are missing, ask the user clearly which specific parameter(s) are needed.
    2-3) If any part of the user's input is ambiguous or difficult to match, ask the user for clarification.

    ### !!IMPORTANT!!
    - User might not mention the exact same parameter names. Try to expand the "key name" provided in the list of parameters into meaningful full words and see if it matches the user input.
    - You MUST check the **description** of each parameter to identify if there are any matching phrases in the user message. 
    - Keep in mind that there can be some parameters which are nested objects including more parameters.
    - When the parameter field in the API information is empty, follow the rules in Output Format Example 1.

    ### Fire.ONE API Parameters Requirements:
    Look for key names in both body and param dictionaries. Key names can be one of the following label, and corresponding value data are required as stated below.   
    - "true" -> required
    - "false" -> optional
    - "one" -> at least one required among the group

    ### Special Token Regular Expressions 
    - There are some specific rules for special parameters, and here is the Regular Expressions you should refer to 
    List of special parameters:
    {pattern_map}

    ### API Information
    {context if context else "No Parameters, No Body Required"}

    ### Output Format Guidelines:
    There are five types of analysis result you need to return. Here are the rules:

    1-1. "result": true
    Label "result" as true when:
    - there are no parameters and body required based on the API information
    - all required parameters and body are provided in the user message
    1-2 "result": false
    Label "result" as false when:    
    - When there are any required parameters or body fields missing
    - When it is ambiguous to determine what the provided parameters are

    2-1 "param": ""
    - When there are no field of "parameter" type required based on the API information
    2-2. "param": "?(Parameter Field Key Name)=(Parameter Field Value)"
    - When there is a field of "parameter" type required and when it is provided in the user message, return a string value in following format with parenthesis replaced with its corresponding value.
        - Example:
        User Message -> "Can you give me a detailed information about FIQ20250813131441048?"
        Return -> "?reqIdx=FIQ20250813131441048"

    3-1. "body": ""
    - When there are no field of "body" type required based on the API information
    3-2. "body": [{{(Body Field Key Name): (Body Field Value)}}] 
    - When there is one or more fields of "body" type required and when it is provided in the user message, return a string value in following format with parenthesis replaced with its corresponding value.
        - Example:
        User Message -> "Can you give me the list of pending firewall policy requests made during July?"
        Return -> "body": {{"pendingRequestDate":"2025/07/01", "pendingEndDate":"2025/07/31"}}
    3-3. "body": [{{(Body Field Key Name): [{{(Inner Body Field Key Name): (Inner Body Field Value)}}]}}]
    - When there is a nested object inside the body field
        - Example:
        User Message -> "Can you change my profile picture to [image.png] file?"
        Return -> "body": {{"fileDetail": [{{"file_name":"image.png", "file_type":"img/png", "file_size":"3.15MB", "file_data":"base64......"}}]}}

    4. "message": "(Message to be sent to the user.)"
    Create this field only:
    - When there are one or more missing required parameters or body fields.
    - When it is ambiguous to determine which parameters the provided information should be mapped to. 

    5-1. "explanation": "(Explanation)"
    - Always provide an explanation on why you classified the result as true or false.

    Combine the above results based on the following rules and return as one JSON object:
    - When "result": true -> return result, param, body, and explanation.
    -> {{"result":, "param":, "body":, "explanation":}}
    - When "result": false -> return result, message, and explanation.
    -> {{"result":, "message":, "explanation":}} 

    ### User Message
    Can you give me the list of firewall policy requests?Now analyze this user message. Make sure to always return the result in JSON format. Do not add any additional explanations outside the JSON object.
    \"\"\"{query}\"\"\"
    """


# ─────────────────────────────────────────────────────────────────────────────
#               - Prompt for expanding abbreviated JSON keys -
# ─────────────────────────────────────────────────────────────────────────────
def policy_result_keys_format_prompt(context: str, query: str, lang: str):
    return f"""I will give you a list of abbreviated words, and I want you to expand it into meaningful full words.
    Capitalize the first letter of each word if the result is in English.

    You MUST only return the result without any additional explanations. Always output the result in Array format. Do not add any additional explanations.

    ### Example:
    Word List: ["empno", "reqIdx", "created_at"]
    -> Output: ["Employee Number", "Request ID", "Date of Creation"]

    ### Important:
    - The following words have specific meanings. Always refer to the following words:
        - idx or id = ID
        - sledge = Security Pledge
        - auth = Authority
        - mo_date = Modified Date

    Now, process these words based on this context: {context}.
    Word List: {query}
    """


# ─────────────────────────────────────────────────────────────────────────────
#              - Prompt for adding opening and closing messages -
# ─────────────────────────────────────────────────────────────────────────────
def policy_additional_messages(query, response, lang: str):
    return f"""You are a friendly assistant that ONLY returns strict JSON in the exact schema below.

    ### Task
    Given:
    - User Message: {query}
    - Original Chatbot Response: {response}

    Generate:
    - A starting message that smoothly connects the user message to the chatbot response.
    - Optionally, a short closing message that invites next actions.

    ### Output Rules (VERY IMPORTANT)
    - Output **only** a single JSON object. No prose, no code fences. Do not add any additional explanations outside of the JSON object.
    - Use this exact structure and order:
    {{"result": [(Starting Message), (Original Response), (Closing Message)]}}
    - Keep the original chatbot response unchanged in the middle element.
    - If you choose not to add a closing message, still include an empty string "" as the third element.
    - Do not add any detailed information in any messages.
    """