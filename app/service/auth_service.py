"""
Authentication Service Layer

This module contains the core business logic for:
- User registration
- User login (JWT issuance + cookie management)
- User logout

The service layer isolates domain logic from the API layer,
making the system easier to test, maintain, and extend.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from app.models.user_model import User
from app.utils.hashing import PasswordHasher
from app.utils.jwt_handler import create_access_token, create_refresh_token, verify_refresh_token
from app.service.cart_service import merge_guest_cart


# ============================================================
# REGISTER USER SERVICE
# ============================================================
def register_user_service(payload, db: Session):
    """
    Create a new user account.

    Steps:
    1. Check if email already exists
    2. Hash the incoming password
    3. Create and persist the new user
    4. Return the user object (FastAPI auto-converts to schema)

    Security:
    - Passwords are never stored in plain text
    - Hashing uses a secure algorithm (bcrypt/argon2)
    """

    # Check for duplicate email
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_pw = PasswordHasher.hash_password(payload.password)

    # Create user instance
    new_user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hashed_pw,
        role="customer",
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ============================================================
# LOGIN USER SERVICE
# ============================================================
def login_user_service(
    payload,
    db: Session,
    response: Response,
    guest_token: str | None
):
    """
    Authenticate a user and establish a secure session.

    Steps:
    1. Validate email + password
    2. Ensure account is active
    3. Merge guest cart → user cart (if guest_token exists)
    4. Issue access + refresh JWT tokens
    5. Set secure HTTP-only cookies
    6. Return LoginResponse-compatible dict

    Security:
    - Access token: short-lived (15 min)
    - Refresh token: long-lived (7 days)
    - Both stored in HTTP-only cookies to prevent XSS theft
    """

    # 1. Find user
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # 2. Check active status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # 3. Verify password
    if not PasswordHasher.verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # 4. Merge guest cart
    if guest_token:
        merge_guest_cart(db, user.id, guest_token)

    # Remove guest cookie
    response.delete_cookie(
        key="guest_token",
        path="/",
        httponly=True,
        samesite="lax",
        secure=False
    )

    # 5. Create tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    # 6. Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 15
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )

    # 7. Return LoginResponse-compatible structure
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


# ============================================================
# LOGOUT SERVICE
# ============================================================
def logout_user_service(response: Response):
    """
    Clear authentication cookies and terminate session.

    - Removes access_token and refresh_token cookies
    - Ensures client is fully logged out
    """

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="strict"
    )

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,
        samesite="strict"
    )

    return {"message": "Logged out successfully"}


def refresh_access_token_service(refresh_token: str | None, response: Response):
    """
    Issue a new access token using a valid refresh token.
    Refresh token is NOT rotated.
    """

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token"
        )

    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user_id = payload.get("sub")

    # Create new access token
    new_access_token = create_access_token(user_id)

    # Update access token cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 15
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "access_expires_in": 60 * 15
    }
