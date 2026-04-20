"""
Category Service Layer

Handles all business logic for category operations.
Router → Service → Database (SQLAlchemy ORM)
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product_model import Category
from app.schemas.product_schema import CategoryCreate


def get_all_categories(db: Session):
    """
    Retrieve all categories.
    """
    return db.query(Category).all()


def get_category_by_id(category_id: str, db: Session):
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


def create_category(data: CategoryCreate, db: Session):
    """
    Create a new category.
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


def update_category(category_id: str, data: CategoryCreate, db: Session):
    """
    Update an existing category.
    """
    category = get_category_by_id(category_id, db)

    category.name = data.name
    category.description = data.description

    db.commit()
    db.refresh(category)
    return category


def delete_category(category_id: str, db: Session):
    """
    Delete a category.
    """
    category = get_category_by_id(category_id, db)

    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}