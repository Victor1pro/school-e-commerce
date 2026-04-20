"""
Product & Category Pydantic Schemas

These schemas define the structure of data sent to and returned from the API.
They ensure consistent validation and serialization between SQLAlchemy models
and API responses.

Category schemas:
    - CategoryBase: Shared fields for creation and response
    - CategoryCreate: Fields required when creating a category
    - CategoryResponse: Fields returned to the client

Product schemas:
    - ProductBase: Shared fields for creation and response
    - ProductCreate: Fields required when creating a product
    - ProductUpdate: Optional fields for updating a product
    - ProductResponse: Fields returned to the client
"""

from pydantic import BaseModel, ConfigDict, UUID4, Field
from typing import Optional
from datetime import datetime


# ============================================================
# CATEGORY SCHEMAS
# ============================================================
class CategoryBase(BaseModel):
    """
    Base schema for category data.

    Includes fields shared between creation and response models.
    """
    name: str
    description: str


class CategoryCreate(CategoryBase):
    """
    Schema used when creating a new category.
    """
    pass


class CategoryResponse(CategoryBase):
    """
    Schema returned when reading category data.

    Includes:
        - id: Unique identifier
        - created_at: Timestamp of creation
        - updated_at: Timestamp of last update
    """
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# PRODUCT SCHEMAS
# ============================================================
class ProductBase(BaseModel):
    """
    Base schema for product data.

    Includes fields shared between creation and response models.
    """
    name: str
    description: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    image_url: str
    category_id: str


class ProductCreate(ProductBase):
    """
    Schema used when creating a new product.

    Includes:
        - is_active: Whether the product is visible in the store
    """
    is_active: bool = True


class ProductUpdate(BaseModel):
    """
    Schema used for updating product fields.

    All fields are optional to allow partial updates.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = None
    category_id: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """
    Schema returned when reading product data.

    Includes:
        - id: Unique identifier
        - is_active: Whether the product is visible
        - created_at: Timestamp of creation
        - updated_at: Timestamp of last update
        - category: Nested category response (optional)
    """
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Nested category response
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)
