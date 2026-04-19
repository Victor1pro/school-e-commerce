"""
JWT Creation and Verification Utilities.

This module handles:
- Creating signed JWT access and refresh tokens
- Embedding standard JWT claims (sub, iat, nbf, exp)
- Verifying and decoding tokens
- Handling expiration and invalid token errors

It uses python-jose for cryptographic signing and decoding.
"""

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from app.config.settings import settings


# =========================================================
# TOKEN CREATION (GENERIC)
# =========================================================
def create_token(data: dict, expires_delta: timedelta, secret_key: str) -> str:
    """
    Create a signed JWT token with standard claims.

    Args:
        data (dict): Payload data. Must include "sub" (subject/user ID).
        expires_delta (timedelta): Token lifetime.
        secret_key (str): Secret key used to sign the token.

    Standard Claims Added:
        - sub: User ID
        - iat: Issued at (UTC)
        - nbf: Not valid before (UTC)
        - exp: Expiration time (UTC)

    Returns:
        str: Encoded JWT token.
    """

    now = datetime.now(timezone.utc)

    # Base claims required for all tokens
    to_encode = {
        "sub": data["sub"],
        "iat": now,
        "nbf": now,
        "exp": now + expires_delta,
    }

    # Add any additional custom claims
    for key, value in data.items():
        if key != "sub":
            to_encode[key] = value

    return jwt.encode(
        to_encode,
        secret_key,
        algorithm=settings.APP_ALGORITHM
    )


# =========================================================
# ACCESS TOKEN CREATION
# =========================================================
def create_access_token(user_id: str) -> str:
    """
    Create a short‑lived access token.

    Args:
        user_id (str): The authenticated user's ID.

    Returns:
        str: Signed JWT access token.
    """
    return create_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=settings.APP_ACCESS_TOKEN_EXPIRE_MINUTES),
        secret_key=settings.APP_ACCESS_TOKEN_SECRET_KEY
    )


# =========================================================
# REFRESH TOKEN CREATION
# =========================================================
def create_refresh_token(user_id: str) -> str:
    """
    Create a long‑lived refresh token.

    Args:
        user_id (str): The authenticated user's ID.

    Returns:
        str: Signed JWT refresh token.
    """
    return create_token(
        data={"sub": user_id},
        expires_delta=timedelta(days=settings.APP_REFRESH_TOKEN_EXPIRE_DAYS),
        secret_key=settings.APP_REFRESH_TOKEN_SECRET_KEY
    )


# =========================================================
# ACCESS TOKEN VERIFICATION
# =========================================================
def verify_access_token(token: str) -> dict | None:
    """
    Verify and decode an access token.

    Args:
        token (str): JWT access token.

    Returns:
        dict | None: Decoded payload if valid, otherwise None.

    Notes:
        - Returns None if token is expired.
        - Returns None if token signature is invalid.
    """
    try:
        return jwt.decode(
            token,
            settings.APP_ACCESS_TOKEN_SECRET_KEY,
            algorithms=[settings.APP_ALGORITHM]
        )
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


# =========================================================
# REFRESH TOKEN VERIFICATION
# =========================================================
def verify_refresh_token(token: str) -> dict | None:
    """
    Verify and decode a refresh token.

    Args:
        token (str): JWT refresh token.

    Returns:
        dict | None: Decoded payload if valid, otherwise None.

    Notes:
        - Refresh tokens use a different secret key.
        - Returns None for expired or invalid tokens.
    """
    try:
        return jwt.decode(
            token,
            settings.APP_REFRESH_TOKEN_SECRET_KEY,
            algorithms=[settings.APP_ALGORITHM]
        )
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None