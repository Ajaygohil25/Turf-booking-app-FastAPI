from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.environ.get("DATABASE_NAME")
DB_USERNAME = os.environ.get("DATABASE_USERNAME")
DB_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DB_HOST = os.environ.get("DATABASE_HOST")
DB_PORT = os.environ.get("DATABASE_PORT")
TEST_DB_NAME = os.environ.get("TEST_DATABASE_NAME")

DB_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
TEST_DB_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"

engine = create_engine(DB_URL)
test_engine = create_engine(TEST_DB_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
TestSessionLocal =  sessionmaker(bind=test_engine,autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    """ Get the database connection from session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()