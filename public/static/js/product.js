// IMPORT CART API
import { CartAPI } from "./cart-api.js";
import { updateCartBadge } from "./cart.js";

const API_URL = "http://127.0.0.1:9000/products/";


// ============================================================
// PAGE ROUTER — Detect which page we are on
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    const grid = document.getElementById("product-grid");
    const single = document.getElementById("product-page");

    if (grid) loadProducts();       // Product listing page
    if (single) loadProduct();      // Single product page
});


// ============================================================
// LOAD ALL PRODUCTS (GRID PAGE)
// ============================================================
async function loadProducts() {
    try {
        const res = await fetch(API_URL);
        const products = await res.json();

        const grid = document.getElementById("product-grid");
        grid.innerHTML = "";

        products.forEach(product => {
            const card = document.createElement("section");
            card.className = "product-card";

            card.innerHTML = `
                <figure class="product-image">
                    <img src="${product.image_url}" alt="${product.name}">
                </figure>

                <div class="product-info">
                    <h3 class="product-name">${product.name}</h3>
                    <p class="product-description">${product.description}</p>
                    <p class="product-price">£${product.price.toFixed(2)}</p>
                </div>

                <div class="product-actions">
                    <button class="add-to-cart-btn" data-id="${product.id}">
                        <i class="fa-solid fa-cart-plus"></i> Add to Cart
                    </button>
                </div>
            `;

            // Fade-in image
            const img = card.querySelector("img");
            img.onload = () => img.classList.add("loaded");

            // Click card → go to single product page
            card.addEventListener("click", (e) => {
                if (!e.target.closest(".add-to-cart-btn")) {
                    window.location.href = `product.html?id=${product.id}`;
                }
            });

            // Add to cart
            card.querySelector(".add-to-cart-btn").addEventListener("click", async (e) => {
                e.stopPropagation();
                await CartAPI.addItem(product.id, 1);
                updateCartBadge();
                showCartToast("Added to cart");
            });

            grid.appendChild(card);
        });

    } catch (error) {
        console.error("Error loading products:", error);
    }
}


// ============================================================
// LOAD SINGLE PRODUCT PAGE
// ============================================================
async function loadProduct() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");

    if (!id) return;

    const res = await fetch(`${API_URL}${id}`);
    const product = await res.json();

    // Fill content
    document.getElementById("product-image").src = product.image_url;
    document.getElementById("product-name").textContent = product.name;
    document.getElementById("product-description").textContent = product.description;
    document.getElementById("product-price").textContent = `£${product.price.toFixed(2)}`;
    document.getElementById("product-caption").textContent = product.name;

    // Fade-in image
    const img = document.getElementById("product-image");
    img.onload = () => img.classList.add("loaded");

    // Quantity selector
    const qtyInput = document.getElementById("qty");
    document.getElementById("qty-inc").onclick = () => qtyInput.value = Number(qtyInput.value) + 1;
    document.getElementById("qty-dec").onclick = () => qtyInput.value = Math.max(1, Number(qtyInput.value) - 1);

    // Add to cart
    document.getElementById("add-to-cart-btn").onclick = async () => {
        await CartAPI.addItem(product.id, Number(qtyInput.value));
        updateCartBadge();
        showCartToast("Added to cart");
    };
}


// ============================================================
// CART TOAST
// ============================================================
function showCartToast(message) {
    const toast = document.getElementById("cart-toast");
    if (!toast) return;

    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 1500);
}