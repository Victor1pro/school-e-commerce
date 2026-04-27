"""
Product & Category Models (Improved)
------------------------------------
Production‑grade SQLAlchemy models for the product catalog.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    String, Integer, ForeignKey, TIMESTAMP, Float, Boolean, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base


# ============================================================
# PRODUCT MODEL
# ============================================================
class Product(Base):
    __tablename__ = "products"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    # slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(String(300), nullable=False)

    # Optional metadata
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sku: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)

    # Pricing
    price: Mapped[float] = mapped_column(Float, nullable=False)
    discount_price: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Inventory
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    # Category
    category_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
        lazy="selectin"
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
    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="product",
        passive_deletes=True,
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Product {self.name}>"


# ============================================================
# CATEGORY MODEL
# ============================================================
class Category(Base):
    __tablename__ = "categories"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )

    # slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self):
        return f"<Category {self.name}>"