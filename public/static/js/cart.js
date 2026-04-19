// cart.js
import { CartAPI } from "./cart-api.js";

const itemsContainer = document.getElementById("cart-items");
const subtotalEl = document.getElementById("cart-subtotal");
const checkoutBtn = document.querySelector(".checkout-btn");

loadCart();


// ============================================================
// LOAD CART
// ============================================================
async function loadCart() {
    try {
        const cart = await CartAPI.getCart();

        if (!cart.items || cart.items.length === 0) {
            renderEmptyCart();
            return;
        }

        itemsContainer.innerHTML = "";
        cart.items.forEach(item => {
            itemsContainer.innerHTML += renderCartItem(item);
        });

        updateTotals(cart);
        attachListeners();

    } catch (err) {
        console.error("Failed to load cart:", err);
    }
}


// ============================================================
// RENDER CART ITEM
// ============================================================
function renderCartItem(item) {
    return `
        <div class="cart-item" data-id="${item.id}">
            
            <figure class="cart-item-image">
                <img src="${item.product.image_url}" alt="${item.product.name}">
            </figure>

            <div class="cart-item-info">
                <p class="cart-item-name">${item.product.name}</p>
                <p class="cart-item-price">£${item.product.price.toFixed(2)}</p>

                <div class="cart-qty">
                    <button class="qty-btn" data-action="dec" data-id="${item.id}">−</button>
                    <input class="qty-input" type="number" value="${item.quantity}" data-id="${item.id}">
                    <button class="qty-btn" data-action="inc" data-id="${item.id}">+</button>
                </div>

                <button class="remove-btn" data-id="${item.id}">Remove</button>
            </div>

        </div>
    `;
}


// ============================================================
// EMPTY CART STATE
// ============================================================
function renderEmptyCart() {
    itemsContainer.innerHTML = `
        <div class="empty-cart">
            <i class="la la-shopping-cart" style="font-size: 3rem; opacity: 0.6;"></i>
            <p>Your cart is empty</p>
            <a href="shop.html" class="checkout-btn" style="text-align:center;">
                Browse Products
            </a>
        </div>
    `;

    subtotalEl.textContent = "£0.00";
}


// ============================================================
// UPDATE TOTALS
// ============================================================
function updateTotals(cart) {
    const subtotal = cart.items.reduce(
        (sum, item) => sum + item.product.price * item.quantity,
        0
    );

    subtotalEl.textContent = `£${subtotal.toFixed(2)}`;
}


// ============================================================
// EVENT LISTENERS
// ============================================================
function attachListeners() {

    // Quantity buttons
    document.querySelectorAll(".qty-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.id;
            const action = btn.dataset.action;

            const input = document.querySelector(`.qty-input[data-id="${id}"]`);
            let qty = parseInt(input.value);

            qty = action === "inc" ? qty + 1 : Math.max(1, qty - 1);
            input.value = qty;

            await CartAPI.updateItem(id, qty);
            loadCart();
            updateCartBadge();
        });
    });

    // Manual quantity input
    document.querySelectorAll(".qty-input").forEach(input => {
        input.addEventListener("change", async () => {
            const id = input.dataset.id;
            const qty = Math.max(1, parseInt(input.value));

            await CartAPI.updateItem(id, qty);
            loadCart();
            updateCartBadge();
        });
    });

    // Remove item
    document.querySelectorAll(".remove-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.id;
            await CartAPI.removeItem(id);
            loadCart();
            updateCartBadge();
        });
    });
}


// ============================================================
// CART BADGE (TOP NAV)
// ============================================================
export async function updateCartBadge() {
    try {
        const cart = await CartAPI.getCart();
        const count = cart.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;

        const badge = document.querySelector(".cart-count");
        if (badge) badge.textContent = count;

    } catch (err) {
        console.error("Badge update failed:", err);
    }
}


// ============================================================
// CHECKOUT BUTTON
// ============================================================
if (checkoutBtn) {
    checkoutBtn.addEventListener("click", () => {
        window.location.href = "checkout.html";
    });
}
