from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_user
from app.schemas.order_schema import OrderResponse
from app.service.order_service import (
    get_order_by_id_service,
    get_order_history
)

router = APIRouter(prefix="/orders", tags=["Orders"])


# -------------------------
# GET SINGLE ORDER
# -------------------------
@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    response_model_exclude_none=True
)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get a single order by ID.
    Only the owner of the order can view it.
    """
    return get_order_by_id_service(db, user, order_id)


# -------------------------
# ORDER HISTORY
# -------------------------
@router.get(
    "/history",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK,
    response_model_exclude_none=True
)
def order_history(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get the authenticated user's order history.
    """
    return get_order_history(db, user)