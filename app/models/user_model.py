"""
User, Settings & Address Models
==============================

This module defines the SQLAlchemy ORM models for user accounts and
their associated addresses and settings in the e-commerce system.

These models support:
- Authentication (email + hashed password)
- Role-based access control (customer)
- User profile data
- Address book for checkout
- Persistent user settings (notifications, privacy, UI preferences)
- Relationships to carts and orders

Architecture:
    User 1 → Many Addresses
    User 1 → Many Orders
    User 1 → Many Carts
    User 1 → 1 Settings

UUIDs are used for all primary keys to ensure global uniqueness.
"""

import uuid
from enum import Enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    TIMESTAMP,
    Integer,
    Index,
    CheckConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLEnum

from app.database import Base


# ============================================================
# USER ROLE ENUM
# ============================================================
class UserRole(str, Enum):
    """
    Enumerates allowed user roles.

    Currently restricted to customers only.
    This design allows future expansion (e.g. vendor, moderator).
    """
    CUSTOMER = "customer"


# ============================================================
# ADDRESS TYPE ENUM
# ============================================================
class AddressType(str, Enum):
    """
    Enumerates supported address types.
    """
    SHIPPING = "shipping"
    BILLING = "billing"


# ============================================================
# USER MODEL
# ============================================================
class User(Base):
    """
    User Model

    Represents a registered user in the system.

    Fields:
        id (str)              → UUID primary key
        name (str)            → Full name
        email (str)           → Unique email (login identifier)
        hashed_password (str) → Argon2-hashed password
        is_active (bool)      → Account status
        role (UserRole)       → Role-based access control
        email_verified (bool) → Email verification state
        last_login (datetime) → Last successful login timestamp
        password_updated_at   → Used for token/session invalidation
        created_at            → Creation timestamp
        updated_at            → Last update timestamp

    Relationships:
        addresses → Saved shipping/billing addresses
        orders    → Orders placed by the user
        carts     → Shopping carts
        settings  → Persistent account settings (1:1)
    """

    __tablename__ = "users"
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
    # Account State
    # --------------------------------------------------------
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"),
        default=UserRole.CUSTOMER,
        nullable=False,
    )

    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

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

    # Used for JWT/session invalidation after password change
    password_updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------
    addresses: Mapped[list["Address"]] = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="user",
        passive_deletes=True,
        lazy="selectin",
    )

    carts: Mapped[list["Cart"]] = relationship(
        "Cart",
        back_populates="user",
        passive_deletes=True,
        lazy="selectin",
    )

    settings: Mapped["UserSettings"] = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # --------------------------------------------------------
    # Indexes
    # --------------------------------------------------------
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<User email={self.email}>"



# ============================================================
# ADDRESS MODEL
# ============================================================
class Address(Base):
    """
    Address Model

    Represents a saved shipping or billing address.

    Ensures:
        - Each user can have only one default address
        - Addresses are deleted automatically when user is deleted
    """

    __tablename__ = "addresses"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[str | None] = mapped_column(String(255))

    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)

    phone: Mapped[str | None] = mapped_column(String(20))

    address_type: Mapped[AddressType] = mapped_column(
        SQLEnum(AddressType, name="address_type"),
        default=AddressType.SHIPPING,
        nullable=False,
    )

    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="addresses",
    )

    __table_args__ = (
        # Enforce only one default address per user
        Index(
            "ix_user_default_address",
            "user_id",
            unique=True,
            postgresql_where=(is_default.is_(True)),
        ),
    )


# ============================================================
# USER SETTINGS MODEL
# ============================================================
class UserSettings(Base):
    """
    UserSettings Model

    Stores persistent, account-level preferences.

    This table is strictly 1:1 with User.
    """

    __tablename__ = "user_settings"
    __mapper_args__ = {"eager_defaults": True}

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Notification preferences
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    order_updates: Mapped[bool] = mapped_column(Boolean, default=True)
    marketing_emails: Mapped[bool] = mapped_column(Boolean, default=False)

    # Security & privacy
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    privacy_tracking: Mapped[bool] = mapped_column(Boolean, default=False)

    # UI & localization
    preferred_theme: Mapped[str] = mapped_column(String(20), default="system")
    text_size: Mapped[int] = mapped_column(Integer, default=100)
    language: Mapped[str] = mapped_column(String(10), default="en")
    currency: Mapped[str] = mapped_column(String(10), default="GBP")
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/London")

    user: Mapped["User"] = relationship(
        "User",
        back_populates="settings",
    )

    __table_args__ = (
        CheckConstraint(
            "text_size BETWEEN 75 AND 150",
            name="ck_user_settings_text_size",
        ),
    )