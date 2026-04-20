// cart-badge.js
import { CartAPI } from "./cart-api.js";

export async function updateCartBadge() {
    try {
        const cart = await CartAPI.getCart();
        const count = cart.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;

        const badge = document.querySelector(".cart-count");
        if (badge) badge.textContent = count;

    } catch (err) {
        console.error("Cart badge update failed:", err);
    }
}

// Auto-run on page load
updateCartBadge();