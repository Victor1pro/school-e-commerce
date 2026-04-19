from fastapi import APIRouter, Depends, Cookie, Response, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.cart_schema import (
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse,
    CartResponse
)
from app.service import cart_service
from app.core.auth import optional_user
from pydantic import BaseModel, UUID4


router = APIRouter(prefix="/cart", tags=["Cart"])


# -------------------------
# MERGE CART REQUEST SCHEMA
# -------------------------
class MergeCartRequest(BaseModel):
    user_id: UUID4
    guest_token: str


# -------------------------
# GET OR CREATE CART
# -------------------------
@router.get(
    "/",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    response_model_exclude_none=True
)
def get_cart(
    db: Session = Depends(get_db),
    user=Depends(optional_user),
    guest_token: str | None = Cookie(default=None)
) -> CartResponse | JSONResponse:
    """
    Get the current cart for the user or guest.
    Creates a new cart if none exists.
    """
    cart = cart_service.get_cart(db, user, guest_token)
    response = CartResponse.model_validate(cart)

    # If a new guest token was generated, set it in the cookie
    if hasattr(cart, "new_guest_token"):
        res = JSONResponse(content=jsonable_encoder(response))
        res.set_cookie(
            key="guest_token",
            value=cart.new_guest_token,
            httponly=True,
            samesite="lax",
            secure=False,
            path="/"
        )
        return res

    return response


# -------------------------
# ADD ITEM TO CART
# -------------------------
@router.post(
    "/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_200_OK,
    response_model_exclude_none=True
)
def add_item(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    user=Depends(optional_user),
    guest_token: str | None = Cookie(default=None)
) -> CartItemResponse | JSONResponse:
    """
    Add an item to the cart.
    Creates a cart if none exists.
    """
    cart_item, cart = cart_service.add_to_cart(db, user, guest_token, item)
    response = CartItemResponse.model_validate(cart_item)

    if hasattr(cart, "new_guest_token"):
        res = JSONResponse(content=jsonable_encoder(response))
        res.set_cookie(
            key="guest_token",
            value=cart.new_guest_token,
            httponly=True,
            samesite="lax",
            secure=False,
            path="/"
        )
        return res

    return response


# -------------------------
# UPDATE CART ITEM
# -------------------------
@router.patch(
    "/items/{item_id}",
    response_model=CartItemResponse,
    response_model_exclude_none=True
)
def update_item(
    item_id: str,
    data: CartItemUpdate,
    db: Session = Depends(get_db),
    user=Depends(optional_user),
    guest_token: str | None = Cookie(default=None)
) -> CartItemResponse:
    """
    Update the quantity of a cart item.
    """
    return cart_service.update_cart_item(db, user, guest_token, item_id, data)


# -------------------------
# DELETE CART ITEM
# -------------------------
@router.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
def remove_item(
    item_id: str,
    db: Session = Depends(get_db),
    user=Depends(optional_user),
    guest_token: str | None = Cookie(default=None)
) -> dict:
    """
    Remove an item from the cart.
    """
    cart_service.remove_item(db, user, guest_token, item_id)
    return {"message": "Item removed"}


# -------------------------
# CLEAR CART
# -------------------------
@router.delete("/clear", status_code=status.HTTP_200_OK)
def clear_cart(
    db: Session = Depends(get_db),
    user=Depends(optional_user),
    guest_token: str | None = Cookie(default=None)
) -> dict:
    """
    Remove all items from the cart.
    """
    cart_service.clear_cart(db, user, guest_token)
    return {"message": "Cart cleared"}


# -------------------------
# MERGE GUEST CART INTO USER CART
# -------------------------
@router.post("/merge", status_code=status.HTTP_200_OK)
def merge_cart(
    data: MergeCartRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    Merge a guest cart into a user's cart after login.
    """
    cart_service.merge_guest_cart(db, data.user_id, data.guest_token)
    return {"message": "Guest cart merged"}