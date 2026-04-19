"""
Cart & CartItem Models

These SQLAlchemy ORM models represent the shopping cart system used in the
e‑commerce platform. The cart supports both:

- Authenticated users (linked via user_id)
- Guest users (identified via guest_token stored in browser cookies)

Architecture:
    Cart 1 → Many CartItems
    CartItem → References Product
    User 1 → Many Carts (guest carts can merge into user carts)

UUIDs are used for all primary keys to ensure global uniqueness.
"""

import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String, ForeignKey, TIMESTAMP, Integer, Float, UniqueConstraint
)
from sqlalchemy.sql import func
from app.database import Base


# ============================================================
# CART MODEL
# ============================================================
class Cart(Base):
    """
    Cart Model

    Represents a shopping cart belonging to either:
    - a logged‑in user (user_id)
    - a guest user (guest_token)

    Fields:
        id (str)              → UUID primary key
        user_id (str|None)    → FK to User (nullable for guests)
        guest_token (str)     → Unique token for guest carts
        created_at            → Timestamp when created
        updated_at            → Timestamp when last updated

    Relationships:
        items → List of CartItem objects
        user  → The user who owns the cart (if logged in)
    """

    __tablename__ = "carts"

    # Primary key (UUID stored as string)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK → User (nullable for guest carts)
    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Guest carts use a browser-stored token instead of user_id
    guest_token: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True
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

    # One cart → many cart items
    items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="carts")


# ============================================================
# CART ITEM MODEL
# ============================================================
class CartItem(Base):
    """
    CartItem Model

    Represents a single product inside a cart.

    Fields:
        id (str)              → UUID primary key
        cart_id (str)         → FK to Cart
        product_id (str)      → FK to Product
        quantity (int)        → Quantity of the product
        price_at_time (float) → Price snapshot when added to cart
        created_at            → Timestamp when created
        updated_at            → Timestamp when last updated

    Constraints:
        - UniqueConstraint(cart_id, product_id)
          Ensures the same product cannot appear twice in the same cart.

    Relationships:
        cart    → Parent cart
        product → Product being purchased
    """

    __tablename__ = "cart_items"

    # Prevent duplicate product entries in the same cart
    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
    )

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # FK → Cart
    cart_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("carts.id", ondelete="CASCADE"),
        index=True
    )

    # FK → Product
    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True
    )

    # Quantity of the product
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )

    # Price snapshot at the time the item was added
    price_at_time: Mapped[float] = mapped_column(
        Float, nullable=False
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

    # Relationships
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")