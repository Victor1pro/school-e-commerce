"""
Search & Filtering Router

This module defines the HTTP endpoints responsible for:
- Live product name suggestions (used by the search bar dropdown)
- Full product search with optional filters (category, price range, keyword)

The router delegates all business logic to the service layer to maintain
clean separation of concerns and ensure testability.

Endpoints:
    GET /search/suggest  → Lightweight suggestions for autocomplete
    GET /search          → Full search results with filters applied
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.service.search_service import (
    get_suggestions,
    search_products_service
)

router = APIRouter(
    prefix="/search",
    tags=["Search & Filtering"]
)


@router.get("/suggest")
async def suggest_products(q: str, db: Session = Depends(get_db)):
    """
    Live Search Suggestions

    Provides lightweight product name suggestions based on the user's
    partial input. This endpoint is optimized for speed and returns
    only the minimal fields required for the autocomplete dropdown.

    Args:
        q (str):
            The partial search query typed by the user.
        db (Session):
            SQLAlchemy database session dependency.

    Returns:
        list[dict]:
            A list of up to 8 suggestion objects, each containing:
            - id (str): Product ID
            - name (str): Product name
    """
    return get_suggestions(q, db)


@router.get("/")
async def search_products(
    q: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    db: Session = Depends(get_db)
):
    """
    Full Product Search + Filtering

    Performs a complete product search with optional filters. This endpoint
    powers the main search results page and the filter sidebar.

    Supported filters:
        - Keyword search (q)
        - Category filtering
        - Price range filtering (min_price, max_price)

    Args:
        q (str | None):
            Optional keyword to match against product names.
        category (str | None):
            Optional category ID (e.g., "fruit", "dairy").
        min_price (float | None):
            Optional minimum price filter.
        max_price (float | None):
            Optional maximum price filter.
        db (Session):
            SQLAlchemy database session dependency.

    Returns:
        list[Product]:
            A list of Product ORM objects matching the filters.
    """
    return search_products_service(q, category, min_price, max_price, db)