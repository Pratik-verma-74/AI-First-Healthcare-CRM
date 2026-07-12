import os
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Fetch Supabase / PostgreSQL database connection URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.warning("DATABASE_URL not found in environment. Defaulting to local SQLite instance for local testing.")
    DATABASE_URL = "sqlite:///./local_crm.db"

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
