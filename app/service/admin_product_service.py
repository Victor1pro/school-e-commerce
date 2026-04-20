"""
Admin Product Service Layer

Handles CRUD operations for products from the admin dashboard.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from uuid import uuid4
import shutil
from app.models.product_model import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate


def get_all_products(db: Session):
    return db.query(Product).all()


def get_product_by_id(product_id: str, db: Session):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


def create_product(data: ProductCreate, db: Session):
    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        stock=data.stock,
        image_url=data.image_url,
        category_id=data.category_id,
        is_active=data.is_active
    )

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(product_id: str, data: ProductUpdate, db: Session):
    product = get_product_by_id(product_id, db)

    for field, value in data.dict(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(product_id: str, db: Session):
    product = get_product_by_id(product_id, db)

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}


def upload_image(file: UploadFile):
    """
    Save uploaded image to /static/uploads and return URL.
    """
    ext = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{ext}"
    filepath = f"public/uploads/{filename}"

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"url": f"/public/uploads/{filename}"}