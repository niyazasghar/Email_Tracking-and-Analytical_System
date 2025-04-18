# db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Example:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/Email_Tracking
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:niyaz.asghar@localhost/Email_Tracking")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
