from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

import database

argos_db = Depends(database.get_db)

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

def insertMessageHistory(db: Session, empno, sender, message):
    query = """
        INSERT INTO argos_chatbot.chatbot_message_history (empno, sender, message)
        VALUES (:empno, :sender, :message)
        """
    result = db.execute(text(query), {"empno":empno, "sender":sender, "message":message}).scalar_one()
    # db.commit()
    return result.rowcount
