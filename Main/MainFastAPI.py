import uvicorn
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session

from Chatbot.Common.GetErrorMessage import GetErrorMessage
from Chatbot.Common.LoadInitData import ModuleInfo, PatternInfo
from Chatbot.Data.schema import ChatObject
from Chatbot.Data.ChatbotDB import getModuleInfo, getPatternMap
from Chatbot.Data.database import SessionLocal, get_argos_db
import Chatbot.Service.ChatService as ChatService

app = FastAPI()

@app.on_event("startup")
def init_module_registry():
    with SessionLocal() as db:
        try:
            ModuleInfo.set_map(getModuleInfo(db))
            print("Chat.ONE | Fire.ONE modules successfully loaded.")
        except Exception as e:
            print("Chat.ONE | Failed to load Fire.ONE modules, Please restart the project.")

        try:
            PatternInfo.set_list(getPatternMap(db))
            print("Chat.ONE | Chat.ONE pattern map successfully loaded.")
        except Exception as e:
            print("Chat.ONE | Failed to load Chat.ONE pattern map, Please restart the project.")


@app.post("/chat")
def chat(request: ChatObject, db: Session=(Depends(get_argos_db))):
    return ChatService.chat(request, db)

@app.get("/getMessageHistory", response_model=list[ChatObject])
def getMessageHistory(empno: str, db: Session=(Depends(get_argos_db))):
    return ChatService.getMessageHistory(db, empno)

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