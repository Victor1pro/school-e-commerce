"""
Product Service Layer

This module provides all business logic for interacting with product data.
It acts as an abstraction between the API router and the database layer.

Responsibilities:
- Retrieve all products
- Retrieve a single product by ID
- Raise meaningful HTTP errors when products are missing

Architecture:
    Router → Service → Database (SQLAlchemy ORM)

This separation keeps the code modular, testable, and scalable.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product_model import Product


def get_all_products(db: Session):
    """
    Retrieve all products from the database.

    Args:
        db (Session): Active SQLAlchemy database session.

    Returns:
        List[Product]: A list of all product records.

    Notes:
        - Used by the product grid (shop page).
        - Ensures consistent product data across the system.
    """
    return db.query(Product).all()


def get_product_by_id(product_id: str, db: Session):
    """
    Retrieve a single product by its unique ID.

    Args:
        product_id (str): The product's unique identifier.
        db (Session): Active SQLAlchemy database session.

    Returns:
        Product: The matching product record.

    Raises:
        HTTPException (404): If the product does not exist.

    Notes:
        - Used by the single product page.
        - Used by cart operations (add/update/remove).
        - Ensures the cart always references valid products.
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product