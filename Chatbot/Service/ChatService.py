from Chatbot.Common.DetectLanguage import detectlanguage

from Chatbot.Data.schema import ChatObject
import Chatbot.Data.ChatbotDB as repo
import Chatbot.LLM.LLMRunner as llm

def chat(request: ChatObject, db):
    # if query.lower() == "exit":
    #     print("Chat.ONE | Exiting chatbot. Goodbye!")
    #     return

    query = request.message.strip()
    print(f"Chat.ONE | {request.empno}: {query}")

    temp = repo.insertMessageHistory(db, request)

    # Step 0: Detect language
    lang = detectlanguage(query)
    print(f"Chat.ONE | Detected Language: {lang}")

    # Step 1: Detect Category
    intent, category = llm.queryCategory(db, query)
    print(f"Chat.ONE | Category Detected: {category}")
    print(f"Chat.ONE | Intent Detected: {intent}")

    # Step 2: Route based on category to extract intent
    if category == "product":
        message = llm.queryManual(query, lang)
    elif category == "policy":
        message = "Sorry, this type of question is not supported yet."
        if lang != "English":
            message = llm.translateSentence(message, lang)
        intent = ""
        # 나중에 API 완료 되면 주석 해제하기...............
        # message = llm.queryApi(db, query, intent, lang)
    elif category == "general":
        message = llm.queryGeneral(query, lang)
        intent = None
    else:
        message = "Sorry, I could not understand what that means. Could you please rephrase your message?"
        if lang != "English":
            message = llm.translateSentence(message, lang)
        intent = ""

    # Step 4: Display final response
    print(f"Chat.ONE | Bot: {message}\n")

    response = ChatObject(
        empno=request.empno,
        sender="chatbot",
        message=message,
        intent=intent
    )

    repo.insertMessageHistory(db, response)
    db.commit()

    return message


def getMessageHistory(db, empno) -> list[ChatObject]:
    return repo.getMessageHistory(db, empno)