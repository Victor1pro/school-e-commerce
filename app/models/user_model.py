"""
User, Settings & Address Models

This module defines the SQLAlchemy ORM models for user accounts and
their associated addresses in the e‑commerce system.

These models support:
- Authentication (email + hashed password)
- User roles (customer, admin, etc.)
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
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, TIMESTAMP, Integer
from sqlalchemy.sql import func
from app.database import Base


# ============================================================
# USER MODEL
# ============================================================
class User(Base):
    """
    User Model

    Represents a registered user in the system.

    Fields:
        id (str)              → UUID primary key
        name (str)            → Full name of the user
        email (str)           → Unique email address (used for login)
        hashed_password (str) → Securely hashed password
        is_active (bool)      → Whether the account is active
        role (str)            → User role (e.g., "customer", "admin")
        created_at            → Timestamp when created
        updated_at            → Timestamp when last updated

    Relationships:
        addresses → List of saved addresses
        orders    → List of orders placed by the user
        carts     → List of carts (guest carts merge into user carts)
        settings  → Persistent user settings (1:1)
    """

    __tablename__ = "users"
    __mapper_args__ = {"eager_defaults": True}

    # Primary key (UUID stored as string)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Basic user info
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Unique email for login
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    # Hashed password (never store plain text)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Role-based access control
    role: Mapped[str] = mapped_column(String(50), default="customer")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # One user → many addresses
    addresses: Mapped[list["Address"]] = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # One user → many orders
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="user",
        passive_deletes=True
    )

    # One user → many carts
    carts: Mapped[list["Cart"]] = relationship(
        "Cart",
        back_populates="user",
        passive_deletes=True
    )

    # One user → one settings row
    settings: Mapped["UserSettings"] = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )



# ============================================================
# ADDRESS MODEL
# ============================================================
class Address(Base):
    """
    Address Model

    Represents a saved address for a user.

    Fields:
        id (str)          → UUID primary key
        user_id (str)     → Foreign key to User
        line1 (str)       → Primary address line
        line2 (str|None)  → Optional secondary line
        city (str)        → City name
        postal_code (str) → Postal/ZIP code
        country (str)     → Country name
        phone (str|None)  → Optional phone number
        created_at        → Timestamp when created
        updated_at        → Timestamp when last updated

    Relationships:
        user → The user who owns this address
    """

    __tablename__ = "addresses"
    __mapper_args__ = {"eager_defaults": True}

    # Primary key (UUID stored as string)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Foreign key → User
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )

    # Address fields
    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[str | None] = mapped_column(String(255), nullable=True)

    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)

    # Optional phone number
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="addresses")



# ============================================================
# USER SETTINGS MODEL
# ============================================================
class UserSettings(Base):
    """
    UserSettings Model

    Stores persistent, account-level settings for each user.
    This includes notification preferences, privacy settings,
    and optional UI preferences that should sync across devices.

    Fields:
        user_id (str)          → Primary key + FK to User
        email_notifications    → Receive email alerts
        order_updates          → Receive order status updates
        marketing_emails       → Receive promotional emails
        two_factor_enabled     → Whether 2FA is enabled
        privacy_tracking       → Allow personalized tracking
        preferred_theme        → "light", "dark", or "system"
        text_size              → UI text scaling percentage

    Relationship:
        user → The user who owns these settings (1:1)
    """

    __tablename__ = "user_settings"
    __mapper_args__ = {"eager_defaults": True}

    # Primary key is also the foreign key to User.id
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    # Notification preferences
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    order_updates: Mapped[bool] = mapped_column(Boolean, default=True)
    marketing_emails: Mapped[bool] = mapped_column(Boolean, default=False)

    # Security & privacy
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    privacy_tracking: Mapped[bool] = mapped_column(Boolean, default=False)

    # Optional UI preferences synced across devices
    preferred_theme: Mapped[str] = mapped_column(String(20), default="system")
    text_size: Mapped[int] = mapped_column(Integer, default=100)

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="settings")