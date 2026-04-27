"""
JWT Creation and Verification Utilities
=======================================

Supports:
- User & Admin JWT separation
- Access & Refresh tokens
- Token type enforcement
- JWT ID (jti) for future Redis revocation
- Strict verification with safe failure behavior
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import jwt, JWTError, ExpiredSignatureError

from app.config.settings import settings


# =========================================================
# INTERNAL HELPERS
# =========================================================
def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _base_claims(
    *,
    subject_id: str,
    subject_type: str,
    token_type: str,
    expires_delta: timedelta,
) -> dict:
    """
    Create standard JWT claims.

    subject_type: "user" | "admin"
    token_type: "access" | "refresh"
    """

    if not subject_id:
        raise ValueError("subject_id is required")

    now = _utc_now()
    issued_at = int(now.timestamp())
    expires_at = issued_at + int(expires_delta.total_seconds())

    return {
        "sub": subject_id,
        "sub_type": subject_type,   # user | admin
        "typ": token_type,          # access | refresh
        "jti": str(uuid4()),        # for Redis revocation later
        "iat": issued_at,
        "nbf": issued_at,
        "exp": expires_at,
    }


def _encode_token(payload: dict, secret_key: str) -> str:
    return jwt.encode(
        payload,
        secret_key,
        algorithm=settings.APP_JWT_ALGORITHM,
    )


def _decode_token(
    token: str,
    secret_key: str,
    expected_type: str,
    expected_subject: str,
) -> dict | None:
    """
    Shared verification logic.

    Returns decoded payload or None on failure.
    """

    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[settings.APP_JWT_ALGORITHM],
        )

        if payload.get("typ") != expected_type:
            return None

        if payload.get("sub_type") != expected_subject:
            return None

        return payload

    except ExpiredSignatureError:
        return None
    except JWTError:
        return None


# =========================================================
# USER TOKEN CREATION
# =========================================================
def create_user_access_token(user_id: str) -> str:
    payload = _base_claims(
        subject_id=user_id,
        subject_type="user",
        token_type="access",
        expires_delta=timedelta(
            minutes=settings.APP_USER_ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    )

    return _encode_token(
        payload,
        settings.APP_USER_ACCESS_TOKEN_SECRET_KEY,
    )


def create_user_refresh_token(user_id: str) -> str:
    payload = _base_claims(
        subject_id=user_id,
        subject_type="user",
        token_type="refresh",
        expires_delta=timedelta(
            days=settings.APP_USER_REFRESH_TOKEN_EXPIRE_DAYS
        ),
    )

    return _encode_token(
        payload,
        settings.APP_USER_REFRESH_TOKEN_SECRET_KEY,
    )


# =========================================================
# ADMIN TOKEN CREATION
# =========================================================
def create_admin_access_token(admin_id: str, role: str) -> str:
    payload = _base_claims(
        subject_id=admin_id,
        subject_type="admin",
        token_type="access",
        expires_delta=timedelta(
            minutes=settings.APP_ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    )

    payload["role"] = role  # embed role for quick checks

    return _encode_token(
        payload,
        settings.APP_ADMIN_ACCESS_TOKEN_SECRET_KEY,
    )


def create_admin_refresh_token(admin_id: str) -> str:
    payload = _base_claims(
        subject_id=admin_id,
        subject_type="admin",
        token_type="refresh",
        expires_delta=timedelta(
            days=settings.APP_ADMIN_REFRESH_TOKEN_EXPIRE_DAYS
        ),
    )

    return _encode_token(
        payload,
        settings.APP_ADMIN_REFRESH_TOKEN_SECRET_KEY,
    )


# =========================================================
# USER TOKEN VERIFICATION
# =========================================================
def verify_user_access_token(token: str) -> dict | None:
    return _decode_token(
        token=token,
        secret_key=settings.APP_USER_ACCESS_TOKEN_SECRET_KEY,
        expected_type="access",
        expected_subject="user",
    )


def verify_user_refresh_token(token: str) -> dict | None:
    return _decode_token(
        token=token,
        secret_key=settings.APP_USER_REFRESH_TOKEN_SECRET_KEY,
        expected_type="refresh",
        expected_subject="user",
    )


# =========================================================
# ADMIN TOKEN VERIFICATION
# =========================================================
def verify_admin_access_token(token: str) -> dict | None:
    return _decode_token(
        token=token,
        secret_key=settings.APP_ADMIN_ACCESS_TOKEN_SECRET_KEY,
        expected_type="access",
        expected_subject="admin",
    )


def verify_admin_refresh_token(token: str) -> dict | None:
    return _decode_token(
        token=token,
        secret_key=settings.APP_ADMIN_REFRESH_TOKEN_SECRET_KEY,
        expected_type="refresh",
        expected_subject="admin",
    )