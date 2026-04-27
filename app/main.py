"""
Main Application Entry Point

This module initializes the FastAPI application, configures middleware,
mounts static files, registers routers, and handles application lifespan
events such as database creation and optional auto‑seeding.

Features:
- Automatic table creation
- Safe one‑time product seeding (only if DB is empty)
- Modular router structure
- Custom middleware stack
- Static file hosting for frontend assets
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine, SessionLocal

# Import models so SQLAlchemy registers them
from app.models.user_model import User
from app.models.product_model import Product, Category
from app.models.cart_model import Cart, CartItem
from app.models.order_model import Order, OrderItem, Shipping, Tracking

# Import seeding function
from app.seed.seed_data import seed_all

# Import middleware
from app.middlewares.auth_middleware import AuthMiddleware
from app.middlewares.error_handler import ErrorHandlerMiddleware
from app.middlewares.logging_middleware import LoggingMiddleware
from app.middlewares.timing_middleware import TimingMiddleware

# Import routers
from app.routers import (
    auth_router,
    cart_router,
    checkout_router,
    order_router,
    category_router,
    payment_router,
    product_router,
    search_router,
    admin_product_router,
    admin_category_router,
    settings_router
)


# ------------------------------------------------------------
# AUTO-SEEDING FUNCTION
# ------------------------------------------------------------
def auto_seed_data():
    """
    Automatically seed categories and products ONLY if the database is empty.

    Prevents:
    - Duplicate entries
    - Overwriting existing data
    - Reseeding on every restart

    Safe for exam environments and development.
    """
    db = SessionLocal()

    product_count = db.query(Product).count()
    category_count = db.query(Category).count()

    if product_count == 0 or category_count == 0:
        print("Database empty — seeding categories and products...")
        seed_all()
    else:
        print(f"Database already seeded ({product_count} products, {category_count} categories). Skipping.")

    db.close()


# ------------------------------------------------------------
# LIFESPAN HANDLER
# ------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup:
        - Creates all database tables
        - Runs safe auto‑seeding for products

    Shutdown:
        - Prints shutdown message
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

    # Safe one-time seeding
    auto_seed_data()

    yield  # Application runs here

    print("Application shutting down.")


# ------------------------------------------------------------
# CREATE FASTAPI APP
# ------------------------------------------------------------
app = FastAPI(
    title="E‑Commerce API",
    description="A modular, scalable retail backend built with FastAPI.",
    version="1.0.0",
    lifespan=lifespan
)

# Serve frontend static files
app.mount("/public", StaticFiles(directory="public"), name="public")


# ------------------------------------------------------------
# CORS CONFIGURATION
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# MIDDLEWARE ORDER
# ------------------------------------------------------------
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(AuthMiddleware)


# ------------------------------------------------------------
# ROUTERS
# ------------------------------------------------------------
app.include_router(auth_router.router)
app.include_router(search_router.router)
app.include_router(cart_router.router)
app.include_router(checkout_router.router)
app.include_router(order_router.router)
app.include_router(category_router.router)
app.include_router(payment_router.router)
app.include_router(product_router.router)
app.include_router(admin_product_router.router)
app.include_router(admin_category_router.router)
app.include_router(settings_router.router)