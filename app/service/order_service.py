"""
Order Service

Handles:
- Fetching a user's order history
- Fetching a single order (with ownership check)
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.order_model import Order


# -------------------------
# GET ORDER HISTORY
# -------------------------
def get_order_history(db: Session, user):
    """
    Return all orders belonging to the authenticated user,
    sorted by newest first.
    """
    return (
        db.query(Order)
        .filter(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
        .all()
    )


# -------------------------
# GET SINGLE ORDER
# -------------------------
def get_order_by_id_service(db: Session, user, order_id: str):
    """
    Return a single order if it belongs to the authenticated user.
    """
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == user.id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return order
