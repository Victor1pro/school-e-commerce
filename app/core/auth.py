# app/core/auth.py
"""
Authentication Dependency Utilities
-----------------------------------
Provides strict and optional authentication dependencies for FastAPI.

Features:
- Extracts JWT tokens from Authorization header or cookies
- Validates access tokens
- Loads authenticated user from the database
- Supports strict (required) and optional (soft) authentication flows
"""

from fastapi import Request, HTTPException, status, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.utils.jwt_handler import verify_user_access_token


# ============================================================
# TOKEN EXTRACTION
# ============================================================
def _extract_token(request: Request, authorization: str | None) -> str | None:
    """
    Extract a Bearer token from:
        1. Authorization header (preferred)
        2. access_token cookie (fallback)
    """

    # 1. Authorization header: "Bearer <token>"
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and token:
            return token.strip()

    # 2. Cookie fallback
    return request.cookies.get("access_token")


# ============================================================
# USER LOADER
# ============================================================
def _load_user(db: Session, user_id: str) -> User | None:
    """Fetch a user by ID, returning None if not found."""
    return db.query(User).filter(User.id == user_id).first()


# ============================================================
# STRICT AUTHENTICATION (REQUIRED)
# ============================================================
def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    """
    Strict authentication dependency.

    Requires:
        - A valid access token
        - A valid user ID inside the token
        - A matching user in the database

    Raises:
        HTTPException(401) if authentication fails.
    """

    # Extract token
    token = _extract_token(request, authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate token
    payload = verify_user_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Load user
    user = _load_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# ============================================================
# OPTIONAL AUTHENTICATION (SOFT)
# ============================================================
def optional_user(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Optional authentication dependency.

    Behaves like get_current_user, but:
        - Never raises an exception
        - Returns None if authentication fails

    Useful for:
        - Public endpoints with optional personalization
        - Pages that behave differently when logged in
    """

    token = _extract_token(request, authorization)
    if not token:
        return None

    payload = verify_user_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    return _load_user(db, user_id)