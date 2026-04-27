"""
Database Configuration Module.

This module initializes the SQLAlchemy engine, session factory, and
base declarative class used across the entire application.

Responsibilities:
- Create the SQLAlchemy engine (SQLite, Postgres, MySQL, etc.)
- Provide a shared Base class for ORM models
- Provide a session factory for database interactions
- Expose a FastAPI dependency (`get_db`) that ensures safe session handling
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.pool import NullPool

from app.config.settings import settings


# =========================================================
# BASE MODEL
# =========================================================
class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    Every model in the application should inherit from this class.
    It provides metadata and mapping functionality required by SQLAlchemy.
    """
    pass


# =========================================================
# DATABASE ENGINE
# =========================================================
if settings.APP_DATABASE_URL.startswith("sqlite"):
    # SQLite (no connection pooling)
    engine = create_engine(
        settings.APP_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
        future=True,
        echo=False,
    )
else:
    # PostgreSQL / MySQL / MariaDB
    engine = create_engine(
        settings.APP_DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        future=True,
        echo=False,
    )


# =========================================================
# SESSION FACTORY
# =========================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)


# =========================================================
# FASTAPI DEPENDENCY
# =========================================================
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Yields:
        Session: A SQLAlchemy session for performing database operations.

    Ensures:
        - A new session is created per request
        - The session is always closed after the request completes
        - Prevents connection leaks and ensures safe DB usage
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()