"""
Admin Product Management Models
-------------------------------
These models represent the admin-side product management system.

They extend the customer-facing product models with:
- Admin actions (price changes, stock updates, activation/deactivation)
- Internal admin notes
- Stock adjustment logs
- Category change logs
- Full audit logging

Architecture:
    Admin 1 → Many AdminProductActions
    Admin 1 → Many AdminProductNotes
    Admin 1 → Many AdminStockLogs
    Admin 1 → Many AdminCategoryActions
    Product 1 → Many AdminProductActions
    Product 1 → Many AdminProductNotes
    Product 1 → Many AdminStockLogs
    Product 1 → Many AdminProductAudit entries
    Category 1 → Many AdminCategoryActions
"""

import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, TIMESTAMP, Text, Integer
from sqlalchemy.sql import func
from app.database import Base


# ============================================================
# BASE MIXIN
# ============================================================
class BaseLogMixin:
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        index=True
    )


# ============================================================
# ADMIN PRODUCT ACTION
# ============================================================
class AdminProductAction(Base, BaseLogMixin):
    __tablename__ = "admin_product_actions"
    __mapper_args__ = {"eager_defaults": True}

    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True
    )

    admin_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    action_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    product = relationship(
        "Product",
        back_populates="admin_actions",
        passive_deletes=True,
        lazy="selectin"
    )

    admin = relationship(
        "Admin",
        back_populates="product_actions",
        passive_deletes=True,
        lazy="selectin"
    )

    def __repr__(self):
        return f"<AdminProductAction id={self.id} action={self.action_type}>"


# ============================================================
# ADMIN PRODUCT NOTE
# ============================================================
class AdminProductNote(Base, BaseLogMixin):
    __tablename__ = "admin_product_notes"
    __mapper_args__ = {"eager_defaults": True}

    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True
    )

    admin_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    note: Mapped[str] = mapped_column(Text, nullable=False)

    product = relationship(
        "Product",
        back_populates="admin_notes",
        passive_deletes=True,
        lazy="selectin"
    )

    admin = relationship(
        "Admin",
        back_populates="product_notes",
        passive_deletes=True,
        lazy="selectin"
    )

    def __repr__(self):
        return f"<AdminProductNote id={self.id}>"


# ============================================================
# ADMIN STOCK LOG
# ============================================================
class AdminStockLog(Base, BaseLogMixin):
    __tablename__ = "admin_stock_logs"
    __mapper_args__ = {"eager_defaults": True}

    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True
    )

    admin_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    stock_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_stock: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_stock: Mapped[int | None] = mapped_column(Integer, nullable=True)

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    product = relationship(
        "Product",
        back_populates="stock_logs",
        passive_deletes=True,
        lazy="selectin"
    )

    admin = relationship(
        "Admin",
        back_populates="stock_logs",
        passive_deletes=True,
        lazy="selectin"
    )

    def __repr__(self):
        return f"<AdminStockLog id={self.id} delta={self.stock_delta}>"


# ============================================================
# ADMIN PRODUCT AUDIT LOG
# ============================================================
class AdminProductAudit(Base, BaseLogMixin):
    __tablename__ = "admin_product_audit"
    __mapper_args__ = {"eager_defaults": True}

    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True
    )

    admin_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    field_changed: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)

    product = relationship(
        "Product",
        back_populates="audit_logs",
        passive_deletes=True,
        lazy="selectin"
    )

    admin = relationship(
        "Admin",
        back_populates="product_audit_logs",
        passive_deletes=True,
        lazy="selectin"
    )

    def __repr__(self):
        return f"<AdminProductAudit id={self.id} field={self.field_changed}>"


# ============================================================
# ADMIN CATEGORY ACTION
# ============================================================
class AdminCategoryAction(Base, BaseLogMixin):
    __tablename__ = "admin_category_actions"
    __mapper_args__ = {"eager_defaults": True}

    category_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("categories.id", ondelete="CASCADE"),
        index=True
    )

    admin_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    action_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    category = relationship(
        "Category",
        back_populates="admin_actions",
        passive_deletes=True,
        lazy="selectin"
    )

    admin = relationship(
        "Admin",
        back_populates="category_actions",
        passive_deletes=True,
        lazy="selectin"
    )

    def __repr__(self):
        return f"<AdminCategoryAction id={self.id} action={self.action_type}>"