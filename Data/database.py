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

def get_argos_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()