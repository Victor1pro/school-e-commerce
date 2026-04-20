"""
Admin Product Router

Full CRUD for products + image upload.
"""

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.service.admin_product_service import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
    upload_image
)

router = APIRouter(
    prefix="/admin/products",
    tags=["Admin Products"]
)


@router.get("/", response_model=list[ProductResponse])
def admin_fetch_products(db: Session = Depends(get_db)):
    return get_all_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
def admin_fetch_product(product_id: str, db: Session = Depends(get_db)):
    return get_product_by_id(product_id, db)


@router.post("/", response_model=ProductResponse)
def admin_create_product(data: ProductCreate, db: Session = Depends(get_db)):
    return create_product(data, db)


@router.put("/{product_id}", response_model=ProductResponse)
def admin_update_product(product_id: str, data: ProductUpdate, db: Session = Depends(get_db)):
    return update_product(product_id, data, db)


@router.delete("/{product_id}")
def admin_delete_product(product_id: str, db: Session = Depends(get_db)):
    return delete_product(product_id, db)


@router.post("/upload-image")
def admin_upload_image(file: UploadFile = File(...)):
    return upload_image(file)