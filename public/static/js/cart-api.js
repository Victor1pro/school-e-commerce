// cart-api.js
import { api } from "./api.js";

const BASE = "http://127.0.0.1:9000/cart";

export const CartAPI = {
    getCart: () => api(`${BASE}/`),

    addItem: (productId, quantity = 1) =>
        api(`${BASE}/items`, "POST", {
        product_id: productId,
        quantity
    }),

    updateItem: (itemId, quantity) =>
        api(`${BASE}/items/${itemId}`, "PATCH", { quantity }),

    removeItem: (itemId) =>
        api(`${BASE}/items/${itemId}`, "DELETE"),

    clearCart: () =>
        api(`${BASE}/clear`, "DELETE"),

    mergeCart: (userId, guestToken) =>
        api(`${BASE}/merge`, "POST", { user_id: userId, guest_token: guestToken })
};
