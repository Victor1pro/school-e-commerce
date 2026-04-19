"""
Search Service Layer

This module contains all business logic for:
- Generating live search suggestions
- Performing full product searches
- Applying category and price filters

The service layer ensures:
- Clean separation from the router
- Reusable logic
- Easier unit testing
- Cleaner, more maintainable code
"""

from sqlalchemy.orm import Session
from app.models.product_model import Product


def get_suggestions(q: str, db: Session):
    """
    Generate Live Search Suggestions

    Fetches up to 8 product names that partially match the user's input.
    This function is optimized for autocomplete performance and returns
    only lightweight data structures.

    Args:
        q (str):
            Partial search query typed by the user.
        db (Session):
            Active SQLAlchemy database session.

    Returns:
        list[dict]:
            A list of suggestion objects:
            - id (str): Product ID
            - name (str): Product name
    """
    results = (
        db.query(Product)
        .filter(Product.name.ilike(f"%{q}%"))
        .limit(8)
        .all()
    )

    return [{"id": p.id, "name": p.name} for p in results]


def search_products_service(q, category, min_price, max_price, db: Session):
    """
    Full Product Search with Filters

    Applies keyword search, category filtering, and price range filtering.
    Only active products (is_active=True) are included in results.

    Args:
        q (str | None):
            Optional keyword to match against product names.
        category (str | None):
            Optional category ID to filter by.
        min_price (float | None):
            Optional minimum price.
        max_price (float | None):
            Optional maximum price.
        db (Session):
            Active SQLAlchemy database session.

    Returns:
        list[Product]:
            A list of Product ORM objects matching the search criteria.
    """
    query = db.query(Product).filter(Product.is_active == True)

    # Keyword search
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))

    # Category filter
    if category:
        query = query.filter(Product.category_id == category)

    # Price filters
    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    return query.all()