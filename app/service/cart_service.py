import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.cart_model import Cart, CartItem
from app.schemas.cart_schema import CartItemCreate, CartItemUpdate
from app.models.product_model import Product


# -----------------------------
# Automatic cart selection
# -----------------------------
def get_or_create_cart(db: Session, user=None, guest_token=None):
    # 1. Logged-in user → always use their cart
    if user:
        cart = db.query(Cart).filter(Cart.user_id == user.id).first()
        if cart:
            return cart

        # Create a new cart for the user
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart

    # 2. Guest with existing token → load their cart
    if guest_token:
        cart = db.query(Cart).filter(Cart.guest_token == guest_token).first()
        if cart:
            return cart

    # 3. No user and no valid guest token → create new guest cart
    new_token = str(uuid.uuid4())
    cart = Cart(guest_token=new_token)
    db.add(cart)
    db.commit()
    db.refresh(cart)

    # Attach token so router can set cookie
    cart.new_guest_token = new_token

    return cart


# -----------------------------
# Get cart
# -----------------------------
def get_cart(db: Session, user=None, guest_token=None):
    cart = get_or_create_cart(db, user, guest_token)
    return cart


# -----------------------------
# Add item to cart
# -----------------------------
def add_to_cart(db: Session, user, guest_token, item: CartItemCreate):
    cart = get_or_create_cart(db, user, guest_token)

    """CONVERTS UUID TO STRINGS FOR SQLITE"""
    product_id = str(item.product_id)
    cart_id = str(cart.id)


    # FETCH PRODUCT TO GET PRICE
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Product not found")


    # CHECK IF ITEM ALREADY EXISTS
    existing = (
        db.query(CartItem)
        .filter(CartItem.cart_id == str(cart.id), CartItem.product_id == str(item.product_id))
        .first()
    )

    if existing:
        existing.quantity += item.quantity
        db.commit()
        db.refresh(existing)
        return existing, cart

    # CREATE NEW ITEM
    new_item = CartItem(
        id = str(uuid.uuid4()),
        cart_id = str(cart.id),
        product_id = str(item.product_id),
        quantity = item.quantity,
        price_at_time = product.price
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item, cart


# -----------------------------
# Update cart item
# -----------------------------
def update_cart_item(db: Session, user, guest_token, item_id: str, data: CartItemUpdate):
    cart = get_or_create_cart(db, user, guest_token)

    item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.cart_id == cart.id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    item.quantity = data.quantity
    db.commit()
    db.refresh(item)
    return item


# -----------------------------
# Remove item
# -----------------------------
def remove_item(db: Session, user, guest_token, item_id: str):
    cart = get_or_create_cart(db, user, guest_token)

    item = (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.cart_id == cart.id)
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(item)
    db.commit()


# -----------------------------
# Clear cart
# -----------------------------
def clear_cart(db: Session, user, guest_token):
    cart = get_or_create_cart(db, user, guest_token)

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()


# -----------------------------
# MERGE CART
# -----------------------------
def merge_guest_cart(db: Session, user_id: str, guest_token: str):
    guest_cart = db.query(Cart).filter(Cart.guest_token == guest_token).first()
    user_cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not guest_cart:
        return

    # If user has no cart yet, convert guest cart into user cart
    if not user_cart:
        guest_cart.user_id = user_id
        guest_cart.guest_token = None
        db.commit()
        return

    # Merge items
    for item in guest_cart.items:
        existing = db.query(CartItem).filter(
            CartItem.cart_id == user_cart.id,
            CartItem.product_id == item.product_id
        ).first()

        if existing:
            existing.quantity += item.quantity
        else:
            item.cart_id = user_cart.id

    # Remove old guest cart
    db.delete(guest_cart)
    db.commit()
