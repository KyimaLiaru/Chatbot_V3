from time import sleep

import time

from Chatbot.Common.DetectLanguage import detectlanguage
from Chatbot.Common.CallLLM import queryLLM
from Chatbot.LLM.LLMRunner import (
    queryCategory,
    queryManual,
    queryApi,
    queryGeneral
)


def main():
    sleep(1)  # 깔끔하게 출력시키기 위한 sleep
    print("Chat.ONE | FIRE.One Chatbot (RAG + Mistral + Language Aware)")
    while True:
        query = input("👤 Type your question (or 'exit' to quit): ")
        if query.lower() == "exit":
            print("Chat.ONE | Exiting chatbot. Goodbye!")
            break

        start = time.time()

        # Step 0: Detect language
        lang = detectlanguage(query)
        print(f"Chat.ONE | Detected Language: {lang}")

        # Step 1: Detect Category
        category = queryCategory(query)
        print(f"Chat.ONE | Category Detected: {category}")

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

        # Step 3: Generate response via Ollama LLM
        # response = queryLLM(query=query, context=context, lang=lang)

        # Step 4: Display final response
        print(f"Chat.ONE | Bot: {response}\n")

        end = time.time()
        print(f"Chat.ONE | 실행 시간: {end - start:.4f}초")


if __name__ == "__main__":
    main()