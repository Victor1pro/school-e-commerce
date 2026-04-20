"""
Admin Category Router

Provides full CRUD operations for category management
from the admin dashboard.

Architecture:
    Router → Service → Database (SQLAlchemy ORM)

This router uses:
    - CategoryCreate (for create + update)
    - CategoryResponse (for output)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product_schema import CategoryCreate, CategoryResponse
from app.service.admin_category_service import (
    admin_get_all_categories,
    admin_get_category_by_id,
    admin_create_category,
    admin_update_category,
    admin_delete_category
)

router = APIRouter(
    prefix="/admin/categories",
    tags=["Admin Categories"]
)


# ============================================================
# GET ALL CATEGORIES (ADMIN)
# ============================================================
@router.get("/", response_model=list[CategoryResponse])
def admin_fetch_categories(db: Session = Depends(get_db)):
    """
    Retrieve all categories for admin dashboard.
    """
    return admin_get_all_categories(db)


# ============================================================
# GET SINGLE CATEGORY (ADMIN)
# ============================================================
@router.get("/{category_id}", response_model=CategoryResponse)
def admin_fetch_category(category_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a single category by ID.
    """
    return admin_get_category_by_id(category_id, db)


# ============================================================
# CREATE CATEGORY (ADMIN)
# ============================================================
@router.post("/", response_model=CategoryResponse)
def admin_create_new_category(data: CategoryCreate, db: Session = Depends(get_db)):
    """
    Create a new category.
    """
    return admin_create_category(data, db)


# ============================================================
# UPDATE CATEGORY (ADMIN)
# ============================================================
@router.put("/{category_id}", response_model=CategoryResponse)
def admin_update_existing_category(category_id: str, data: CategoryCreate, db: Session = Depends(get_db)):
    """
    Update an existing category.
    """
    return admin_update_category(category_id, data, db)


# ============================================================
# DELETE CATEGORY (ADMIN)
# ============================================================
@router.delete("/{category_id}")
def admin_remove_category(category_id: str, db: Session = Depends(get_db)):
    """
    Delete a category.
    Automatically cascades to products because of the model relationship.
    """
    return admin_delete_category(category_id, db)