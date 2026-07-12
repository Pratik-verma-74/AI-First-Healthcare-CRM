import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

import shutil

# Fetch Supabase / PostgreSQL database connection URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Check if running in Vercel or Serverless environment
IS_SERVERLESS = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))

if not DATABASE_URL:
    if IS_SERVERLESS:
        tmp_db_path = "/tmp/local_crm.db"
        bundled_db_path = os.path.join(os.path.dirname(__file__), "../local_crm.db")
        if not os.path.exists(tmp_db_path) and os.path.exists(bundled_db_path):
            try:
                shutil.copyfile(bundled_db_path, tmp_db_path)
                logger.info(f"Copied bundled SQLite database to {tmp_db_path} for serverless execution.")
            except Exception as e:
                logger.warning(f"Could not copy bundled DB to /tmp: {e}")
        DATABASE_URL = f"sqlite:///{tmp_db_path}"
        logger.warning(f"Running on Vercel serverless without DATABASE_URL. Using writable fallback: {DATABASE_URL}")
    else:
        logger.warning("DATABASE_URL not found in environment. Defaulting to local SQLite instance for local testing.")
        DATABASE_URL = "sqlite:///./local_crm.db"
elif DATABASE_URL.startswith("sqlite") and IS_SERVERLESS:
    tmp_db_path = "/tmp/local_crm.db"
    bundled_db_path = os.path.join(os.path.dirname(__file__), "../local_crm.db")
    if not os.path.exists(tmp_db_path) and os.path.exists(bundled_db_path):
        try:
            shutil.copyfile(bundled_db_path, tmp_db_path)
        except Exception as e:
            pass
    DATABASE_URL = f"sqlite:///{tmp_db_path}"

# Handle SQLAlchemy formatting quirks for PostgreSQL / Supabase URLs if user provided postgres:// instead of postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure engine depending on database dialect
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Production Supabase PostgreSQL pool configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator for injecting SQLAlchemy database sessions into FastAPI routes.
    Ensures sessions are closed automatically after route execution.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
