"""
Admin & AdminSettings Models
===========================

This module defines SQLAlchemy ORM models for admin accounts and
admin-level settings.

Admins are separated from regular users to ensure:
- Clear access boundaries
- Strong role-based authorization
- Cleaner permission logic
- Reduced risk of privilege escalation

Architecture:
    Admin 1 → 1 AdminSettings

UUIDs are used for all primary keys.
"""

import uuid
from enum import Enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    Integer,
    CheckConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLEnum

from app.database import Base


# ============================================================
# ADMIN ROLE ENUM
# ============================================================
class AdminRole(str, Enum):
    """
    Enumerates allowed admin roles.

    Roles define the scope of administrative permissions.
    """
    SUPERADMIN = "superadmin"
    MANAGER = "manager"
    SUPPORT = "support"


# ============================================================
# ADMIN MODEL
# ============================================================
class Admin(Base):
    """
    Admin Model

    Represents an administrative user with elevated privileges.

    Fields:
        id (str)              → UUID primary key
        name (str)            → Full name
        email (str)           → Unique login email
        hashed_password (str) → Secure password hash
        role (AdminRole)      → Permission level
        is_active (bool)      → Account status
        last_login            → Last successful login timestamp
        created_at            → Creation timestamp
        updated_at            → Last update timestamp

    Relationship:
        settings → AdminSettings (1:1)
    """

    __tablename__ = "admins"
    __mapper_args__ = {"eager_defaults": True}

    # --------------------------------------------------------
    # Primary Key
    # --------------------------------------------------------
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # --------------------------------------------------------
    # Identity & Authentication
    # --------------------------------------------------------
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    # --------------------------------------------------------
    # Role & Status
    # --------------------------------------------------------
    role: Mapped[AdminRole] = mapped_column(
        SQLEnum(AdminRole, name="admin_role"),
        default=AdminRole.MANAGER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    last_login: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    # --------------------------------------------------------
    # Timestamps
    # --------------------------------------------------------
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------
    settings: Mapped["AdminSettings"] = relationship(
        "AdminSettings",
        back_populates="admin",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Admin email={self.email} role={self.role}>"



# ============================================================
# ADMIN SETTINGS MODEL
# ============================================================
class AdminSettings(Base):
    """
    AdminSettings Model

    Stores persistent admin-level preferences and feature access flags.

    This table is strictly 1:1 with Admin.
    """

    __tablename__ = "admin_settings"
    __mapper_args__ = {"eager_defaults": True}

    # Primary key is also the foreign key to Admin.id
    admin_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("admins.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # --------------------------------------------------------
    # Dashboard & UI Preferences
    # --------------------------------------------------------
    dashboard_theme: Mapped[str] = mapped_column(
        String(20),
        default="dark",
    )

    items_per_page: Mapped[int] = mapped_column(
        Integer,
        default=20,
    )

    # --------------------------------------------------------
    # System Permissions
    # --------------------------------------------------------
    receive_system_alerts: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    maintenance_mode_access: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------
    admin: Mapped["Admin"] = relationship(
        "Admin",
        back_populates="settings",
    )

    # --------------------------------------------------------
    # Constraints
    # --------------------------------------------------------
    __table_args__ = (
        CheckConstraint(
            "items_per_page BETWEEN 5 AND 100",
            name="ck_admin_items_per_page",
        ),
    )