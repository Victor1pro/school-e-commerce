"""
Category Router

Public + Admin endpoints for category management.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.product_schema import CategoryCreate, CategoryResponse
from app.service.category_service import (
    get_all_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# ---------------- PUBLIC ----------------
@router.get("/", response_model=list[CategoryResponse])
def fetch_categories(db: Session = Depends(get_db)):
    return get_all_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
def fetch_category(category_id: str, db: Session = Depends(get_db)):
    return get_category_by_id(category_id, db)


# ---------------- ADMIN ----------------
@router.post("/admin", response_model=CategoryResponse)
def admin_create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(data, db)


@router.put("/admin/{category_id}", response_model=CategoryResponse)
def admin_update_category(category_id: str, data: CategoryCreate, db: Session = Depends(get_db)):
    return update_category(category_id, data, db)


@router.delete("/admin/{category_id}")
def admin_delete_category(category_id: str, db: Session = Depends(get_db)):
    return delete_category(category_id, db)