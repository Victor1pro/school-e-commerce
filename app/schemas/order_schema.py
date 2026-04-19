"""
Order Schemas

These Pydantic schemas define the structure of order-related data exchanged
between the API and the client. They ensure consistent validation and
serialization for:

- Order items
- Embedded product details
- Tracking updates
- Shipping information
- Full order responses

This module uses lightweight product data (OrderProduct) to avoid returning
full product objects inside order responses.
"""

from pydantic import BaseModel, ConfigDict, UUID4, Field
from datetime import datetime
from typing import Optional, List


# ============================================================
# LIGHTWEIGHT PRODUCT SCHEMA FOR ORDER ITEMS
# ============================================================
class OrderProduct(BaseModel):
    """
    Lightweight product representation used inside order item responses.

    Includes only the fields needed for displaying purchased items:
        - id: Product ID
        - name: Product name
        - image_url: Product image path
        - price: Price at the time of purchase
    """
    id: UUID4
    name: str
    image_url: str
    price: float

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# ORDER ITEM RESPONSE
# ============================================================
class OrderItemResponse(BaseModel):
    """
    Schema returned for each item inside an order.

    Includes:
        - id: Order item ID
        - product_id: Linked product ID
        - quantity: Number of units purchased
        - price_at_purchase: Price snapshot at purchase time
        - created_at / updated_at: Timestamps
        - product: Embedded lightweight product details
    """
    id: UUID4
    product_id: UUID4
    quantity: int = Field(gt=0)
    price_at_purchase: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    product: Optional[OrderProduct] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# TRACKING RESPONSE
# ============================================================
class TrackingResponse(BaseModel):
    """
    Schema representing a tracking update for an order.

    Includes:
        - id: Tracking entry ID
        - status: Current tracking status
        - location: Optional location update
        - updated_at: Timestamp of the update
    """
    id: UUID4
    status: str
    location: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# SHIPPING RESPONSE
# ============================================================
class ShippingResponse(BaseModel):
    """
    Schema representing shipping information for an order.

    Includes:
        - full_name: Recipient name
        - address fields: Full delivery address
        - shipping_method: Delivery method (standard, express, etc.)
        - shipping_cost: Cost of shipping
        - tracking_number: Optional tracking number
        - status: Shipping status
        - created_at / updated_at: Timestamps
    """
    id: UUID4
    full_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    postcode: str
    country: str
    shipping_method: str
    shipping_cost: float
    tracking_number: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# FULL ORDER RESPONSE
# ============================================================
class OrderResponse(BaseModel):
    """
    Full order response returned to the client.

    Includes:
        - id: Order ID
        - user_id: ID of the user who placed the order
        - total_amount: Total cost of the order
        - status: Order status (pending, paid, shipped, etc.)
        - created_at / updated_at: Timestamps
        - items: List of purchased items
        - tracking_updates: List of tracking entries
        - shipping: Shipping details (optional)
    """
    id: UUID4
    user_id: UUID4
    total_amount: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    items: List[OrderItemResponse]
    tracking_updates: List[TrackingResponse]
    shipping: Optional[ShippingResponse] = None

    model_config = ConfigDict(from_attributes=True)