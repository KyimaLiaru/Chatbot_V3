from typing import Dict

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from Chatbot.Data.database import get_argos_db
from Chatbot.Data.schema import ChatObject, ModuleObject

argos_db = Depends(get_argos_db)

def getPatternMap(db: Session):
    query = """
        SELECT
            id,
            pattern_name,
            pattern_regex,
            pattern_description_en,
            pattern_description_ko
        FROM argos_chatbot.chatbot_pattern_map
        ORDER BY id ASC
        """
    result = db.execute(text(query)).mappings().all()
    return [dict(r) for r in result]

def getIntentList(db: Session) -> list[str]:
    query = """
        SELECT intent
        FROM argos_chatbot.chatbot_dictionary
        """
    result = db.execute(text(query)).scalars().all()
    return result

def getDictionary(db: Session=argos_db):
    query ="""
        SELECT intent, dictionary
        FROM argos_chatbot.chatbot_dictionary
        """
    result = db.execute(text(query)).mappings().all()
    return [dict(r) for r in result]

def updateDictionary(db: Session, intent, keywords, threshold=9):
    query = """
        SELECT dictionary
        FROM argos_chatbot.chatbot_dictionary
        WHERE intent=:intent
    """
    result = db.execute(text(query), {"intent":intent}).scalar().split(" ")

    for word in keywords.split(" "):
        if result.count(word) < threshold:
            result.append(word)

    dictionary = " ".join(result)
    # print(dictionary)

    query = """
        UPDATE argos_chatbot.chatbot_dictionary
        SET dictionary=:keywords
        WHERE intent=:intent
        """
    result = db.execute(text(query), {"intent":intent, "keywords":dictionary})
    # db.commit()
    return result.rowcount

def getMessageHistory(db: Session, empno) -> list[ChatObject]:
    query = """
        SELECT empno, sender, message, sent_at, intent
        FROM argos_chatbot.chatbot_message_history
        WHERE empno=:empno
        """
    result = db.execute(text(query), {"empno":empno}).mappings().all()
    return [ChatObject.model_validate(r) for r in result]

def insertMessageHistory(db: Session, request: ChatObject):
    query = """
        INSERT INTO argos_chatbot.chatbot_message_history (empno, sender, message, sent_at, intent)
        VALUES (:empno, :sender, :message, COALESCE(:sent_at, clock_timestamp()), :intent)
        """
    result = db.execute(text(query), request.model_dump())
    # db.commit()
    return result.rowcount

def getModuleInfo(db: Session) -> Dict[str, ModuleObject]:
    query = """
    SELECT product_code, product_url_http, product_port
    FROM argos_common.admin_api_setting
    """
    result = db.execute(text(query)).mappings().all()

    moduleDict: Dict[str, ModuleObject] = {}
    for r in result:
        moduleDict[r["product_code"]] = ModuleObject(
            product_code=r["product_code"],
            product_url_http=r["product_url_http"],
            product_port=r["product_port"],
        )
    return moduleDict