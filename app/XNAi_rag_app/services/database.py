"""Database session management for agent services."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os
import logging
from typing import Generator

# Database configuration
logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """Get database URL with container-aware host check."""
    base_url = os.getenv("DATABASE_URL")
    if base_url:
        return base_url
    
    # Check for container environment
    host = "postgres" if os.path.exists("/.dockerenv") else "localhost"
    return f"postgresql://postgres:postgres@{host}:5432/xnai"

# Lazy-load engine
_engine = None
_SessionLocal = None

def get_engine():
    """Get or create database engine (lazy-load)."""
    global _engine
    if _engine is None:
        db_url = get_database_url()
        logger.info(f"Initializing database engine: {db_url}")
        
        # Engine configuration
        engine_args = {
            "pool_pre_ping": True,
            "pool_recycle": 3600
        }

        # Only SQLite supports/needs check_same_thread
        if db_url.startswith("sqlite"):
            engine_args["connect_args"] = {"check_same_thread": False}
            engine_args["poolclass"] = StaticPool
        else:
            engine_args["connect_args"] = {"application_name": "omega-agent-bus"}

        _engine = create_engine(db_url, **engine_args)
        
    return _engine

def get_session_factory():
    """Get or create session factory (lazy-load)."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Provide database session with proper cleanup."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from app.XNAi_rag_app.models.agent_models import Base
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def get_db_session() -> Session:
    """Get a database session for direct use."""
    SessionLocal = get_session_factory()
    return SessionLocal()


# Event listeners for connection management
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance (if using SQLite)."""
    db_url = get_database_url()
    if 'sqlite' in db_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()