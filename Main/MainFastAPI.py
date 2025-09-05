import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel

from Common.DetectLanguage import detectlanguage
from Common.CallLLM import queryLLM
from LLM.LLMRunner import (
    queryCategory,
    queryManual,
    queryApi,
    queryGeneral
)

app = FastAPI()


class Question(BaseModel):
    prompt: str


@app.post("/chat")
def chat(question: Question):
    query = question.prompt.strip()

    print("👤 You: " + query)

    if query.lower() == "exit":
        print("👋 Exiting chatbot. Goodbye!")
        return

    # Step 0: Detect language
    lang = detectlanguage(query)
    print(f"🌐 Detected Language: {lang}")

    # Step 1: Detect Category
    category = queryCategory(query)
    print(f"🔍 Category Detected: {category}")

    # Step 2: Route based on category to extract intent
    if category == "product":
        response = queryManual(query, lang)
    elif category == "policy":
        response = queryApi(query, lang)
    elif category == "general":
        response = queryGeneral(query, lang)
    else:
        prompt = f"""You are a professional translator for software applications.
                Translate the given text into Korean, ensuring it sounds natural for a Korean software/system message.

                Rules:
                - Use polite but concise formal tone, common in enterprise apps.
                - Prefer "죄송합니다" for "Sorry," not awkward forms like "양해 바랍니다."
                - Keep the phrasing natural, short, and clear.
                - Do not add explanations or rephrase meaning. Just translate.

                Text: Sorry, this type of question is not supported yet.
                """

        response = queryLLM(prompt).get("response")

    # Step 4: Display final response
    print(f"\n🤖 Bot: {response}\n")

    return response


# 현재 파일을 직접 실행 시 1번 안 해도 됨.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8199)

# 1. FastAPI 실행 (기존 python3 'Chatbot rag.py' 대신 실행)
# uvicorn run_chatbot:app --reload

# 2. Chatbot AI 테스트 방법
# 기존 방식처럼 Terminal 을 통해 메세지 입력하는 방식 대신
# Postman 과 같은 프로그램을 통해 요청 전송 가능
#
# API 호출 정보:
#   Chatbot AI 테스트 url
#     127.0.0.1:8000/chat
#
#   Request format
#     a. Content-Type: application/json
#     b. Method: POST
#     c. JSON content
#       {
#         "prompt": (message)
#       }