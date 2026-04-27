"""
Admin Authentication Dependency Utilities
=========================================

Provides strict authentication and role-based authorization
for administrative accounts.

This module parallels the user-facing auth system but is fully
isolated to prevent privilege escalation.

Features:
- Extracts JWT tokens (shared logic with user auth)
- Validates admin-specific access tokens
- Loads admin accounts from the database
- Enforces admin roles (superadmin, manager, support)
- Provides reusable role-checking dependencies

Admins are stored in a separate table to ensure:
- Clear privilege boundaries
- Strong RBAC (Role-Based Access Control)
- Reduced attack surface
"""

from fastapi import Request, HTTPException, status, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin_user_model import Admin, AdminRole
from app.utils.jwt_handler import verify_access_token
from app.core.auth import _extract_token  # Reuse shared token extraction


# ============================================================
# STRICT ADMIN AUTHENTICATION
# ============================================================
def get_current_admin(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> Admin:
    """
    Strict authentication dependency for admin accounts.

    Requirements:
        - A valid admin access token
        - Token must contain "admin_id"
        - Admin must exist and be active

    Raises:
        HTTPException(401) → Missing/invalid token
        HTTPException(403) → Token is not an admin token
        HTTPException(404) → Admin not found
    """

    # --------------------------------------------------------
    # Extract token (header or cookie)
    # --------------------------------------------------------
    token = _extract_token(request, authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing admin authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --------------------------------------------------------
    # Validate token signature & expiration
    # --------------------------------------------------------
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --------------------------------------------------------
    # Ensure token belongs to an admin
    # --------------------------------------------------------
    admin_id = payload.get("admin_id")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token does not belong to an admin account",
        )

    # --------------------------------------------------------
    # Load admin from database
    # --------------------------------------------------------
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin account not found",
        )

    # --------------------------------------------------------
    # Ensure admin is active
    # --------------------------------------------------------
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is disabled",
        )

    return admin


# ============================================================
# ROLE-BASED AUTHORIZATION
# ============================================================
def require_admin_role(*allowed_roles: AdminRole):
    """
    Factory dependency for enforcing admin roles.

    Example:
        @router.get("/dashboard")
        def dashboard(admin = Depends(require_admin_role(AdminRole.MANAGER))):
            ...

    Raises:
        HTTPException(403) if admin role is not permitted.
    """

    def wrapper(admin: Admin = Depends(get_current_admin)) -> Admin:
        if admin.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Admin role '{admin.role}' does not have access",
            )
        return admin

    return wrapper


# ============================================================
# PREDEFINED ROLE SHORTCUTS
# ============================================================
def superadmin_required(admin: Admin = Depends(require_admin_role(AdminRole.SUPERADMIN))) -> Admin:
    """Shortcut dependency for superadmin-only routes."""
    return admin


def manager_required(admin: Admin = Depends(require_admin_role(AdminRole.MANAGER, AdminRole.SUPERADMIN))) -> Admin:
    """Shortcut dependency for manager or superadmin routes."""
    return admin


def support_required(admin: Admin = Depends(require_admin_role(AdminRole.SUPPORT, AdminRole.MANAGER, AdminRole.SUPERADMIN))) -> Admin:
    """Shortcut dependency for support-level access."""
    return admin
