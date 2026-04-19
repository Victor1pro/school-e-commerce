"""
Data Seeding Module

This module seeds BOTH categories.json and products.json into the database.
It is designed for exam environments, development setups, and automated
initialization workflows.

Key Features:
- Safe duplicate prevention (idempotent seeding)
- Clear console logging for verification
- File existence checks for debugging
- Correct seeding order (categories → products)
- Preserves category_id relationships from JSON

Usage:
    Called automatically from main.py during application startup.
"""

import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.product_model import Product, Category


# ------------------------------------------------------------
# JSON FILE PATHS
# ------------------------------------------------------------
CATEGORIES_PATH = Path("app/seed/categories.json")
PRODUCTS_PATH = Path("app/seed/products.json")


# ------------------------------------------------------------
# CATEGORY SEEDER
# ------------------------------------------------------------
def seed_categories(db: Session):
    """
    Seed categories.json into the database.

    Steps:
        1. Verify categories.json exists
        2. Load JSON data
        3. Insert categories only if they do not already exist
        4. Print detailed logs for exam demonstration

    Args:
        db (Session): Active SQLAlchemy database session.
    """
    print("\n[SEED] Checking categories.json...")

    # Ensure file exists
    if not CATEGORIES_PATH.exists():
        print("[ERROR] categories.json NOT FOUND!")
        return

    print("[OK] categories.json found.")

    # Load JSON
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        categories = json.load(f)

    print(f"[SEED] Loading {len(categories)} categories...")

    # Insert categories
    for c in categories:
        exists = db.query(Category).filter(Category.id == c["id"]).first()

        if exists:
            print(f" - Skipped (already exists): {c['id']}")
            continue

        category = Category(
            id=c["id"],
            name=c["name"],
            description=c["description"]
        )

        db.add(category)
        print(f" + Inserted category: {c['id']}")

    print("[DONE] Categories seeded.\n")


# ------------------------------------------------------------
# PRODUCT SEEDER
# ------------------------------------------------------------
def seed_products(db: Session):
    """
    Seed products.json into the database.

    Steps:
        1. Verify products.json exists
        2. Load JSON data
        3. Insert products only if they do not already exist
        4. Preserve category_id from JSON
        5. Print detailed logs for exam demonstration

    Args:
        db (Session): Active SQLAlchemy database session.
    """
    print("[SEED] Checking products.json...")

    # Ensure file exists
    if not PRODUCTS_PATH.exists():
        print("[ERROR] products.json NOT FOUND!")
        return

    print("[OK] products.json found.")

    # Load JSON
    with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
        products = json.load(f)

    print(f"[SEED] Loading {len(products)} products...")

    # Insert products
    for p in products:
        exists = db.query(Product).filter(Product.id == p["id"]).first()

        if exists:
            print(f" - Skipped (already exists): {p['name']}")
            continue

        product = Product(
            id=p["id"],
            name=p["name"],
            description=p["description"],
            image_url=p["image_url"],
            price=p["price"],
            stock=p.get("stock", 0),      # Default stock if missing
            is_active=True,
            category_id=p.get("category_id")  # IMPORTANT: preserve category
        )

        db.add(product)
        print(f" + Inserted product: {p['name']}")

    print("[DONE] Products seeded.\n")


# ------------------------------------------------------------
# MASTER SEEDER
# ------------------------------------------------------------
def seed_all():
    """
    Run all seeders in the correct order.

    Order:
        1. Categories (must exist first)
        2. Products (depend on category_id)

    This function is called from main.py during application startup.
    """
    print("\n========== DATABASE SEEDING START ==========")

    db: Session = SessionLocal()

    seed_categories(db)
    seed_products(db)

    db.commit()
    db.close()

    print("========== DATABASE SEEDING COMPLETE ==========\n")