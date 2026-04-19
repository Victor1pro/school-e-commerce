"""
Cart Schemas

These Pydantic schemas define the structure of cart-related data exchanged
between the API and the client. They ensure consistent validation and
serialization for:

- Cart items
- Embedded product details
- Cart totals
- Full cart responses

This module uses lightweight product data (CartProduct) to avoid returning
full product objects inside cart responses.
"""

from pydantic import BaseModel, ConfigDict, UUID4, Field
from typing import Optional, List
from datetime import datetime


# ============================================================
# LIGHTWEIGHT PRODUCT SCHEMA FOR CART
# ============================================================
class CartProduct(BaseModel):
    """
    Lightweight product representation used inside cart responses.

    Includes only the fields needed for displaying cart items:
        - id: Product ID
        - name: Product name
        - image_url: Product image path
        - price: Current product price
    """
    id: UUID4
    name: str
    image_url: str
    price: float

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CART ITEM BASE SCHEMAS
# ============================================================
class CartItemBase(BaseModel):
    """
    Base schema for cart item creation and updates.

    Includes:
        - product_id: ID of the product being added
        - quantity: Number of units (must be > 0)
    """
    product_id: UUID4
    quantity: int = Field(default=1, gt=0)


class CartItemCreate(CartItemBase):
    """
    Schema used when adding a new item to the cart.
    """
    pass


class CartItemUpdate(BaseModel):
    """
    Schema used when updating the quantity of an existing cart item.
    """
    quantity: int = Field(gt=0)


# ============================================================
# CART ITEM RESPONSE
# ============================================================
class CartItemResponse(BaseModel):
    """
    Schema returned for each item inside a cart.

    Includes:
        - id: Cart item ID
        - product_id: Linked product ID
        - quantity: Number of units
        - price_at_time: Price snapshot when added
        - created_at / updated_at: Timestamps
        - product: Embedded lightweight product details
    """
    id: UUID4
    product_id: UUID4
    quantity: int
    price_at_time: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    product: Optional[CartProduct] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CART TOTALS
# ============================================================
class CartTotals(BaseModel):
    """
    Summary of cart totals.

    Includes:
        - subtotal: Total cost of all items
        - item_count: Total number of items
    """
    subtotal: float
    item_count: int


# ============================================================
# FULL CART RESPONSE
# ============================================================
class CartResponse(BaseModel):
    """
    Full cart response returned to the client.

    Includes:
        - id: Cart ID
        - user_id: Linked user (if logged in)
        - guest_token: Token for guest carts
        - created_at / updated_at: Timestamps
        - items: List of cart items
        - totals: Calculated totals (optional)
    """
    id: UUID4
    user_id: Optional[UUID4] = None
    guest_token: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    items: List[CartItemResponse]
    totals: Optional[CartTotals] = None

    model_config = ConfigDict(from_attributes=True)