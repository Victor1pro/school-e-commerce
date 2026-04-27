"""
Admin Order Management Models
-----------------------------
These models represent the admin-side order management system.

They extend the customer-facing order models with:
- Admin actions (status changes, cancellations, manual edits)
- Internal admin notes
- Refund processing
- Staff assignment
- Full audit logging

Architecture:
    Admin 1 → Many AdminOrderActions
    Admin 1 → Many AdminOrderNotes
    Admin 1 → Many AdminRefunds
    Admin 1 → Many AdminOrderAssignments
    Order 1 → Many AdminOrderActions
    Order 1 → Many AdminOrderNotes
    Order 1 → Many AdminRefunds
    Order 1 → Many AdminOrderAssignments
    Order 1 → Many AdminOrderAudit entries
"""

import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, TIMESTAMP, Text, Float
from sqlalchemy.sql import func
from app.database import Base


# ============================================================
# ADMIN ORDER ACTION
# ============================================================
class AdminOrderAction(Base):
    """
    Logs admin actions performed on an order.

    Examples:
        - Status changed from "pending" → "paid"
        - Tracking number updated
        - Shipping method changed
        - Manual price adjustment
        - Order cancelled
    """

    __tablename__ = "admin_order_actions"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True
    )

    admin_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    # Relationships
    order = relationship("Order", back_populates="admin_actions")
    admin = relationship("Admin", back_populates="order_actions")


# ============================================================
# ADMIN ORDER NOTE
# ============================================================
class AdminOrderNote(Base):
    """
    Internal notes added by admins.

    Examples:
        - "Customer requested gift wrapping"
        - "Suspicious billing address"
        - "High-value order, verify manually"
    """

    __tablename__ = "admin_order_notes"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True
    )

    admin_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    note: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    order = relationship("Order", back_populates="admin_notes")
    admin = relationship("Admin", back_populates="order_notes")


# ============================================================
# ADMIN REFUND MODEL
# ============================================================
class AdminRefund(Base):
    """
    Represents a refund request and its admin processing.

    Fields:
        - refund_amount
        - reason
        - approved (bool)
        - processed_at
    """

    __tablename__ = "admin_refunds"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True
    )

    admin_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True
    )

    refund_amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    processed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    order = relationship("Order", back_populates="refunds")
    admin = relationship("Admin", back_populates="refunds")


# ============================================================
# ADMIN ORDER ASSIGNMENT
# ============================================================
class AdminOrderAssignment(Base):
    """
    Assigns an order to a specific admin/staff member.

    Examples:
        - Assigned to warehouse staff
        - Assigned to support agent
        - Assigned to fraud review team
    """

    __tablename__ = "admin_order_assignments"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True
    )

    admin_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True
    )

    assigned_role: Mapped[str] = mapped_column(String(50), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    order = relationship("Order", back_populates="assignments")
    admin = relationship("Admin", back_populates="assignments")


# ============================================================
# ADMIN ORDER AUDIT LOG
# ============================================================
class AdminOrderAudit(Base):
    """
    Full audit trail for compliance and debugging.

    Logs:
        - What changed
        - Old value
        - New value
        - Which admin changed it
        - When it changed
    """

    __tablename__ = "admin_order_audit"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    order_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True
    )

    admin_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True
    )

    field_changed: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    order = relationship("Order", back_populates="audit_logs")
    admin = relationship("Admin", back_populates="audit_logs")