# nutrisnap-backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import time

# Get DB URL from Docker environment variables
# During tests, use SQLite (set TESTING=1 before running pytest)
if os.getenv("TESTING") == "1":
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    print("✅ Using SQLite for testing")
else:
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/nutrisnap_db")
    # Retry logic for Docker startup timing
    while True:
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
            connection = engine.connect()
            connection.close()
            print("✅ Database connection successful!")
            break
        except Exception as e:
            print("⏳ Waiting for Database...", e)
            time.sleep(2)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()