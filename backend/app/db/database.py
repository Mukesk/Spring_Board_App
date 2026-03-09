import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# We will read this from the `.env` file, with a localhost default
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://mukeshkanna@localhost/quiz_poc")

# Postgres doesn't need "check_same_thread"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
