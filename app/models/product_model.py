"""
Product & Category Models

This module defines the SQLAlchemy ORM models for the Product and Category
tables used in the e‑commerce system.

These models represent the core catalog structure:
- Products belong to categories.
- Products can appear in carts and orders.
- Categories can contain multiple products.

The models include:
- UUID primary keys
- Timestamps
- Relationships to CartItem and OrderItem
- SQLite‑safe price and stock fields
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    String, Integer, ForeignKey, TIMESTAMP, Float
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


# ============================================================
# PRODUCT MODEL
# ============================================================
class Product(Base):
    """
    Product Model

    Represents a single product in the store catalog.

    Fields:
        id (str)            → UUID primary key
        name (str)          → Product name (indexed for search)
        slug (str)          → SEO‑friendly URL identifier
        description (str)   → Product description text
        image_url (str)     → Path to product image in /static/images/
        price (float)       → Product price (SQLite‑safe float)
        stock (int)         → Inventory count
        is_active (bool)    → Whether product is visible in the store
        category_id (str)   → Foreign key to Category
        created_at          → Timestamp when created
        updated_at          → Timestamp when last updated

    Relationships:
        category     → Parent category
        cart_items   → Items referencing this product in carts
        order_items  → Items referencing this product in orders
    """

    __tablename__ = "products"
    __mapper_args__ = {"eager_defaults": True}

    # Primary key (UUID stored as string)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Basic product info
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    image_url: Mapped[str] = mapped_column(String(300), nullable=False)

    # Price stored as float (SQLite does not support Decimal)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    # Inventory and visibility
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Category relationship (nullable)
    category_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # ORM relationship to Category model
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products"
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

    # Relationship to cart items
    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # Relationship to order items
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="product",
        passive_deletes=True
    )


# ============================================================
# CATEGORY MODEL
# ============================================================
class Category(Base):
    """
    Category Model

    Represents a product category (e.g., "Electronics", "Groceries").

    Fields:
        id (str)            → UUID primary key
        name (str)          → Category name
        slug (str)          → SEO‑friendly identifier
        description (str)   → Category description
        created_at          → Timestamp when created
        updated_at          → Timestamp when last updated

    Relationships:
        products → List of products belonging to this category
    """

    __tablename__ = "categories"
    __mapper_args__ = {"eager_defaults": True}

    # Primary key (UUID stored as string)
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Basic category info
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )

    description: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationship to Product model
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan",
        passive_deletes=True
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