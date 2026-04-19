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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
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
# SQLite requires special connection arguments when used with FastAPI
if settings.APP_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.APP_DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite threading
        future=True,                                # Use SQLAlchemy 2.0 style
        echo=False,                                 # Disable SQL logging
        pool_pre_ping=True                          # Detect stale connections
    )
else:
    # For PostgreSQL, MySQL, MariaDB, etc.
    engine = create_engine(
        settings.APP_DATABASE_URL,
        future=True,
        echo=False,
        pool_pre_ping=True
    )


# =========================================================
# SESSION FACTORY
# =========================================================
SessionLocal = sessionmaker(
    autocommit=False,          # Manual commit control
    autoflush=False,           # Prevent automatic flushes
    expire_on_commit=False,    # Keep objects usable after commit (important for FastAPI)
    bind=engine
)


# =========================================================
# FASTAPI DEPENDENCY
# =========================================================
def get_db():
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