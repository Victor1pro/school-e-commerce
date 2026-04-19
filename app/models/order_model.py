"""
Order, OrderItem, Tracking, and Shipping Models

These SQLAlchemy ORM models represent the full order lifecycle in the
e‑commerce system. They cover:

- Orders placed by users
- Items inside each order
- Shipping details for delivery
- Tracking updates for order status

Architecture:
    User 1 → Many Orders
    Order 1 → Many OrderItems
    Order 1 → One Shipping record
    Order 1 → Many Tracking updates

UUIDs are used for all primary keys to ensure global uniqueness.
"""

import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Integer, ForeignKey, TIMESTAMP, Float, Text
)
from sqlalchemy.sql import func
from app.database import Base


# ============================================================
# ORDER MODEL
# ============================================================
class Order(Base):
    """
    Order Model

    Represents a completed or in‑progress order placed by a user.

    Fields:
        id (str)            → UUID primary key
        user_id (str|None)  → FK to User (nullable for guest checkout)
        total_amount (float)→ Total cost of the order
        status (str)        → Order status (pending, paid, shipped, etc.)
        created_at          → Timestamp when created
        updated_at          → Timestamp when last updated

    Relationships:
        user              → The user who placed the order
        items             → List of OrderItem entries
        tracking_updates  → List of Tracking updates
        shipping          → Shipping details (one‑to‑one)
    """

    __tablename__ = "orders"
    __mapper_args__ = {"eager_defaults": True}

    # Primary key (UUID)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK → User (nullable for guest orders)
    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="orders")

    # Order summary fields
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # One order → many order items
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # One order → many tracking updates
    tracking_updates: Mapped[list["Tracking"]] = relationship(
        "Tracking",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # One order → one shipping record
    shipping: Mapped["Shipping"] = relationship(
        "Shipping",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )


# ============================================================
# ORDER ITEM MODEL
# ============================================================
class OrderItem(Base):
    """
    OrderItem Model

    Represents a single product inside an order.

    Fields:
        id (str)                → UUID primary key
        order_id (str)          → FK to Order
        product_id (str|None)   → FK to Product (nullable if product deleted)
        quantity (int)          → Quantity purchased
        price_at_purchase (float) → Price at the time of purchase
        created_at              → Timestamp when created
        updated_at              → Timestamp when last updated

    Relationships:
        order   → Parent order
        product → Product purchased
    """

    __tablename__ = "order_items"
    __mapper_args__ = {"eager_defaults": True}

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK → Order
    order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True
    )

    # FK → Product (nullable if product removed from catalog)
    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Item details
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_purchase: Mapped[float] = mapped_column(Float, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


# ============================================================
# TRACKING MODEL
# ============================================================
class Tracking(Base):
    """
    Tracking Model

    Represents a tracking update for an order (e.g., shipped, out for delivery).

    Fields:
        id (str)          → UUID primary key
        order_id (str)    → FK to Order
        status (str)      → Tracking status text
        location (str)    → Optional location update
        updated_at        → Timestamp when updated

    Relationship:
        order → Parent order
    """

    __tablename__ = "tracking"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(Text, default="processing", nullable=False)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    order: Mapped["Order"] = relationship("Order", back_populates="tracking_updates")


# ============================================================
# SHIPPING MODEL
# ============================================================
class Shipping(Base):
    """
    Shipping Model

    Represents the shipping details for an order.

    Fields:
        id (str)              → UUID primary key
        order_id (str)        → FK to Order
        full_name (str)       → Recipient name
        address_line1 (str)   → Primary address line
        address_line2 (str)   → Optional secondary line
        city (str)            → City
        postcode (str)        → Postal code
        country (str)         → Country
        shipping_method (str) → Delivery method (standard, express, etc.)
        shipping_cost (float) → Cost of shipping
        tracking_number (str) → Optional tracking number
        status (str)          → Shipping status
        created_at            → Timestamp when created
        updated_at            → Timestamp when last updated

    Relationship:
        order → Parent order (one‑to‑one)
    """

    __tablename__ = "shipping"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Shipping address fields
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    address_line1: Mapped[str] = mapped_column(String(200), nullable=False)
    address_line2: Mapped[str | None] = mapped_column(String(200), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postcode: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)

    # Shipping method + cost
    shipping_method: Mapped[str] = mapped_column(String(50), nullable=False)
    shipping_cost: Mapped[float] = mapped_column(Float, nullable=False)

    # Tracking info
    tracking_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Pending")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationship back to Order
    order: Mapped["Order"] = relationship("Order", back_populates="shipping")