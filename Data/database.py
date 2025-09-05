from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define DB URL
DB_URL = f"postgresql://argosuser:Fridaynight1!@192.168.7.178:5432/argosdb"

# Create DB Engine
engine = create_engine(DB_URL, pool_pre_ping=True, future=True, connect_args={"options": "-c search_path=argos_chatbot"})

# Create a SessionLocal class to create session instances
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 연결 테스트용
if __name__ == "__main__":
    from ChatbotDB import updateDictionary

    try:
        with engine.begin() as conn:
            print("Count = ", conn.execute(text("SELECT COUNT(*) FROM chatbot_pattern_map")).scalar())
    except Exception as e:
        import traceback
        print("DB 테스트 실패:", e)
        traceback.print_exc()