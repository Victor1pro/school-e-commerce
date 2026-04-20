"""
Admin Category Service Layer

Provides full CRUD operations for category management
from the admin dashboard.

Architecture:
    Router → Service → Database (SQLAlchemy ORM)

This layer contains all business logic and ensures:
- Clean separation from API routes
- Reusable logic for admin operations
- Consistent error handling
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product_model import Category
from app.schemas.product_schema import CategoryCreate


def admin_get_all_categories(db: Session):
    """
    Retrieve all categories (admin view).
    """
    return db.query(Category).all()


def admin_get_category_by_id(category_id: str, db: Session):
    """
    Retrieve a single category by ID.
    """
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


def admin_create_category(data: CategoryCreate, db: Session):
    """
    Create a new category.

    Validates:
        - Unique category name
    """
    exists = db.query(Category).filter(Category.name == data.name).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    category = Category(
        name=data.name,
        description=data.description
    )

    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def admin_update_category(category_id: str, data: CategoryCreate, db: Session):
    """
    Update an existing category.

    Fields updated:
        - name
        - description
    """
    category = admin_get_category_by_id(category_id, db)

    category.name = data.name
    category.description = data.description

    db.commit()
    db.refresh(category)
    return category


def admin_delete_category(category_id: str, db: Session):
    """
    Delete a category.

    Automatically cascades to products because of:
        cascade="all, delete-orphan"
    """
    category = admin_get_category_by_id(category_id, db)

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}