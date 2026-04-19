"""
Authentication Router

This module exposes all authentication-related HTTP endpoints:
- User registration
- User login (JWT + cookies)
- User logout
- Renews User token after Login

The router delegates business logic to the auth_service layer,
keeping the API layer clean, declarative, and easy to test.
"""

from fastapi import APIRouter, Depends, status, Response, Cookie
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    UserLogin,
    LoginResponse
)
from app.schemas.token_schema import RefreshTokenResponse
from app.service.auth_service import (
    register_user_service,
    login_user_service,
    logout_user_service,
    refresh_access_token_service
)

router = APIRouter(
    prefix="/auth/users",
    tags=["Authentication"]
)

# ============================================================
# REGISTER USER
# ============================================================
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True
)
def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Register a new user account.

    - Validates incoming data using UserCreate schema
    - Ensures email uniqueness
    - Hashes password before storing
    - Returns a sanitized UserResponse (no password fields)

    The service layer handles:
        - hashing
        - database persistence
        - conflict detection
    """
    return register_user_service(payload, db)


# ============================================================
# LOGIN USER
# ============================================================
@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_202_ACCEPTED,
    response_model_exclude_none=True
)
def login_user(
    payload: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
    guest_token: str | None = Cookie(None)
) -> LoginResponse:
    """
    Authenticate a user and establish a session.

    Responsibilities:
    - Validate credentials
    - Merge guest cart into user cart (if guest_token exists)
    - Issue access + refresh JWT tokens
    - Set secure HTTP-only cookies
    - Return LoginResponse containing:
        * access_token
        * refresh_token
        * token_type
        * full user profile

    The service layer encapsulates:
        - password verification
        - token creation
        - cookie management
        - cart merging logic
    """
    return login_user_service(payload, db, response, guest_token)


# ============================================================
# LOGOUT USER
# ============================================================
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK
)
def logout_user(response: Response) -> dict:
    """
    Log out the current user.

    - Clears authentication cookies
    - Invalidates session on the client side
    - Returns a simple confirmation message

    The service layer handles cookie deletion.
    """
    return logout_user_service(response)


# ============================================================
# REFRESH ROUTE
# ============================================================
@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK
)
def refresh_access_token(
    response: Response,
    refresh_token: str | None = Cookie(None)
):
    return refresh_access_token_service(refresh_token, response)