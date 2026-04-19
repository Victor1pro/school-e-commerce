# app/routers/checkout_router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_user
from app.schemas.order_schema import OrderResponse
from app.schemas.checkout_schema import CheckoutRequest
from app.service.checkout_service import checkout_service


router = APIRouter(prefix="/checkout", tags=["Checkout"])


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True
)
def checkout(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Checkout endpoint that accepts billing, shipping, and payment details.
    """
    return checkout_service(db, user, payload)
