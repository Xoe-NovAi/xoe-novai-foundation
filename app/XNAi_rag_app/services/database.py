"""Database session management for agent services."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os
from typing import Generator

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/xnai")

# Create engine with connection pooling
engine_args = {
    "poolclass": StaticPool,
    "pool_pre_ping": True,
    "pool_recycle": 3600
}

# Only SQLite supports/needs check_same_thread
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    engine_args["connect_args"] = {"application_name": "omega-agent-bus"}

engine = create_engine(DATABASE_URL, **engine_args)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Provide database session with proper cleanup."""
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
    Base.metadata.create_all(bind=engine)


def get_db_session() -> Session:
    """Get a database session for direct use."""
    return SessionLocal()


# Event listeners for connection management
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance (if using SQLite)."""
    if 'sqlite' in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()