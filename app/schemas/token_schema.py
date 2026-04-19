"""
Token and Authentication Response Schemas.

This module defines all Pydantic models related to:
- Access & refresh token responses
- Login responses including embedded user data
- Token refresh responses

These schemas are used across authentication endpoints to ensure
consistent, secure, and well‑structured API responses.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.user_schema import UserResponse


# =========================================================
# TOKEN RESPONSE (GENERAL)
# =========================================================
class TokenResponse(BaseModel):
    """
    General-purpose token response schema.

    Used for endpoints that issue both access and refresh tokens,
    such as registration or generic authentication flows.

    Fields:
        access_token (str): Short-lived JWT used for authenticated requests.
        refresh_token (str): Long-lived token used to obtain new access tokens.
        token_type (str): Usually 'bearer', defines how the token is used.
        access_expires_in (Optional[int]): Optional expiry time (seconds) for access token.
        refresh_expires_in (Optional[int]): Optional expiry time (seconds) for refresh token.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    access_expires_in: Optional[int] = None
    refresh_expires_in: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# LOGIN RESPONSE
# =========================================================
class LoginResponse(BaseModel):
    """
    Response schema returned after a successful login.

    Includes:
        - Access and refresh tokens
        - Optional expiry metadata
        - Embedded user profile information

    This schema is typically returned by the `/auth/login` endpoint.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    access_expires_in: Optional[int] = None
    refresh_expires_in: Optional[int] = None

    # Nested user details for convenience
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# REFRESH TOKEN RESPONSE
# =========================================================
class RefreshTokenResponse(BaseModel):
    """
    Response schema returned when refreshing an access token.

    Contains:
        - A new access token
        - Optional expiry metadata
        - No refresh token (refresh tokens are not rotated here unless implemented)

    Used by endpoints such as `/auth/refresh`.
    """
    access_token: str
    token_type: str = "bearer"
    access_expires_in: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)