"""
Product Router

This module exposes API endpoints for retrieving product data.
All product data is now served from the SQL database via the
product service layer (product_service.py).

Routes:
    GET /products/          → Return all products
    GET /products/{id}      → Return a single product by ID

Architecture:
    Router  →  Service Layer  →  Database (SQLAlchemy ORM)

This ensures:
- Clean separation of concerns
- Reusable business logic
- Consistent product data across the entire system
- Compatibility with the cart, checkout, and frontend product pages
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Database session dependency
from app.database import get_db

# Service layer functions
from app.service.product_service import (
    get_all_products,
    get_product_by_id
)

# Create router with prefix and tag
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("/")
def fetch_products(db: Session = Depends(get_db)):
    """
    GET /products/

    Retrieve all products from the database.

    Args:
        db (Session): Injected SQLAlchemy session.

    Returns:
        List[Product]: A list of all product records.

    Used by:
        - Product grid page (shop.html)
        - Admin dashboards (if implemented)
    """
    return get_all_products(db)


@router.get("/{product_id}")
def fetch_product(product_id: str, db: Session = Depends(get_db)):
    """
    GET /products/{product_id}

    Retrieve a single product by its unique ID.

    Args:
        product_id (str): The product's unique identifier.
        db (Session): Injected SQLAlchemy session.

    Returns:
        Product: The matching product record.

    Raises:
        HTTPException 404: If the product does not exist.

    Used by:
        - Single product page (product.html)
        - Cart operations (add/update/remove)
        - Checkout summary
    """
    return get_product_by_id(product_id, db)