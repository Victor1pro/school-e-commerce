// shop.js
import { CartAPI } from "./cart-api.js";
import { updateCartBadge } from "./cart-badge.js";

const grid = document.getElementById("product-grid");

// Load products + badge on page load
document.addEventListener("DOMContentLoaded", () => {
    loadProducts();
    updateCartBadge();
});

/* ============================================================
   LOAD PRODUCTS FROM BACKEND
============================================================ */
async function loadProducts() {
    try {
        const res = await fetch("http://127.0.0.1:9000/products/");
        const products = await res.json();

        renderProducts(products);

    } catch (err) {
        console.error("Failed to load products:", err);
        grid.innerHTML = `<p style="padding:20px;">Failed to load products.</p>`;
    }
}

/* ============================================================
   RENDER PRODUCT CARDS
============================================================ */
function renderProducts(products) {
    grid.innerHTML = products.map(p => `
        <div class="product-card">
            <figure class="product-image">
                <img src="${p.image_url}" alt="${p.name}">
            </figure>

            <div class="product-info">
                <h3>${p.name}</h3>
                <p class="price">£${p.price.toFixed(2)}</p>

                <button class="btn-primary add-to-cart" data-id="${p.id}">
                    <i class="la la-cart-plus"></i> Add to Cart
                </button>
            </div>
        </div>
    `).join("");

    attachAddToCartListeners();
}

/* ============================================================
   ADD TO CART BUTTONS
============================================================ */
function attachAddToCartListeners() {
    document.querySelectorAll(".add-to-cart").forEach(btn => {
        btn.addEventListener("click", async () => {
            const productId = btn.dataset.id;

            try {
                await CartAPI.addItem(productId, 1);
                await updateCartBadge();

                // Temporary success state
                btn.innerHTML = `<i class="la la-check"></i> Added`;
                btn.disabled = true;

                setTimeout(() => {
                    btn.innerHTML = `<i class="la la-cart-plus"></i> Add to Cart`;
                    btn.disabled = false;
                }, 1200);

            } catch (err) {
                console.error("Add to cart failed:", err);
            }
        });
    });
}