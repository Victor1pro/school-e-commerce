"""
Checkout Service

Handles the full checkout workflow:
- Validates the user's cart
- Validates stock availability
- Calculates total amount
- Creates the order
- Creates order items with price snapshots
- Deducts product stock
- Creates shipping entry using frontend data
- Creates initial tracking entry
- Clears the cart
- Returns the completed order

This service is called by the checkout router.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.cart_model import Cart, CartItem
from app.models.order_model import Order, OrderItem, Shipping, Tracking
from app.models.product_model import Product
from app.schemas.checkout_schema import CheckoutRequest


def checkout_service(db: Session, user, payload: CheckoutRequest):
    """
    Convert the authenticated user's cart into a completed order.

    Args:
        db (Session): SQLAlchemy database session
        user: Authenticated user object
        payload (CheckoutRequest): Billing, shipping, and payment details

    Returns:
        Order: SQLAlchemy Order instance (Pydantic will serialize it)
    """

    # ------------------------------------------------------------
    # 1. RETRIEVE USER CART
    # ------------------------------------------------------------
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()

    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    # ------------------------------------------------------------
    # 2. VALIDATE STOCK + CALCULATE TOTAL
    # ------------------------------------------------------------
    total_amount = 0

    for item in cart.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product not found: {item.product_id}"
            )

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for {product.name}"
            )

        # Add price snapshot * quantity
        total_amount += float(item.price_at_time) * item.quantity

    # ------------------------------------------------------------
    # 3. CREATE ORDER
    # ------------------------------------------------------------
    order = Order(
        user_id=user.id,
        total_amount=total_amount,
        status="pending"
    )
    db.add(order)
    db.flush()  # ensures order.id is available

    # ------------------------------------------------------------
    # 4. CREATE ORDER ITEMS + DEDUCT STOCK
    # ------------------------------------------------------------
    for item in cart.items:
        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item.price_at_time
        )
        db.add(order_item)

        # Deduct stock
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.stock -= item.quantity

    # ------------------------------------------------------------
    # 5. CREATE SHIPPING ENTRY (FROM FRONTEND FORM)
    # ------------------------------------------------------------
    shipping = Shipping(
        order_id=order.id,
        full_name=payload.full_name,
        address_line1=payload.address,
        city=payload.city,
        postcode=payload.postcode,
        country="United Kingdom",  # You can make this dynamic later
        shipping_method="standard",
        shipping_cost=4.99,
        status="Pending"
    )
    db.add(shipping)

    # ------------------------------------------------------------
    # 6. INITIAL TRACKING ENTRY
    # ------------------------------------------------------------
    tracking = Tracking(
        order_id=order.id,
        status="processing",
        location="Warehouse"
    )
    db.add(tracking)

    # ------------------------------------------------------------
    # 7. CLEAR CART
    # ------------------------------------------------------------
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

    # ------------------------------------------------------------
    # 8. COMMIT + RETURN ORDER
    # ------------------------------------------------------------
    db.commit()
    db.refresh(order)

    return order