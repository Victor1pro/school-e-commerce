"""
Authentication Dependency Utilities.

This module provides strict and optional authentication dependencies
used across the FastAPI application. It handles:

- Extracting Bearer tokens from headers or cookies
- Validating access tokens
- Loading the authenticated user from the database
- Supporting both strict (required) and soft (optional) authentication flows
"""

from fastapi import Request, HTTPException, status, Depends, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.utils.jwt_handler import verify_access_token


# =========================================================
# TOKEN EXTRACTION HELPER
# =========================================================
def _extract_token(request: Request, authorization: str | None) -> str | None:
    """
    Extracts a Bearer token from the incoming request.

    Token lookup order:
        1. Authorization header (preferred)
        2. access_token cookie (fallback)

    Args:
        request (Request): Incoming FastAPI request object.
        authorization (str | None): Raw Authorization header value.

    Returns:
        str | None: Extracted token string, or None if not found.
    """

    # 1. Attempt to extract from Authorization header
    if authorization:
        parts = authorization.split(" ")
        # Expected format: "Bearer <token>"
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]

    # 2. Fallback to cookie-based authentication
    return request.cookies.get("access_token")


# =========================================================
# STRICT AUTHENTICATION DEPENDENCY
# =========================================================
def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> User:
    """
    Strict authentication dependency.

    Requires:
        - A valid access token (header or cookie)
        - A valid user ID inside the token payload
        - A matching user in the database

    Raises:
        HTTPException: If token is missing, invalid, expired, or user not found.

    Returns:
        User: The authenticated SQLAlchemy User model instance.
    """

    # Extract token from header or cookie
    token = _extract_token(request, authorization)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token"
        )

    # Validate token and decode payload
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # Extract user ID from token payload
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID"
        )

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# =========================================================
# OPTIONAL AUTHENTICATION DEPENDENCY
# =========================================================
def optional_user(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> User | None:
    """
    Soft authentication dependency.

    Behaves like get_current_user, but:
        - Never raises an HTTPException
        - Returns None if authentication fails

    Useful for:
        - Public endpoints that behave differently when a user is logged in
        - Optional personalization features

    Returns:
        User | None: Authenticated user or None if not authenticated.
    """

    # Extract token (header or cookie)
    token = _extract_token(request, authorization)
    if not token:
        return None

    # Validate token
    payload = verify_access_token(token)
    if not payload:
        return None

    # Extract user ID
    user_id = payload.get("sub")
    if not user_id:
        return None

    # Return user if found, otherwise None
    return db.query(User).filter(User.id == user_id).first()