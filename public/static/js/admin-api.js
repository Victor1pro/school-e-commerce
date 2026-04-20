// ============================================================
// ADMIN API MODULE
// - Wraps all admin-only endpoints
// - Uses global api() helper for consistency
// - Handles 401 → redirect to admin-login
// ============================================================

import { api } from "./api.js";

const BASE = "http://127.0.0.1:9000";

// ------------------------------------------------------------
// AUTO-HANDLER FOR ADMIN 401 ERRORS
// ------------------------------------------------------------
function handleAdminError(err) {
    if (err.message.includes("Authentication required")) {
        window.location.href = "/public/pages/admin/admin-login.html";
        return;
    }
    throw err;
}

// ------------------------------------------------------------
// FETCH ALL PRODUCTS
// ------------------------------------------------------------
export async function adminGetProducts() {
    try {
        return await api(`${BASE}/admin/products`, "GET");
    } catch (err) {
        handleAdminError(err);
    }
}

// ------------------------------------------------------------
// FETCH ALL CATEGORIES
// ------------------------------------------------------------
export async function adminGetCategories() {
    try {
        return await api(`${BASE}/admin/categories`, "GET");
    } catch (err) {
        handleAdminError(err);
    }
}

// ------------------------------------------------------------
// CREATE PRODUCT
// ------------------------------------------------------------
export async function adminCreateProduct(payload) {
    try {
        return await api(`${BASE}/admin/products`, "POST", payload);
    } catch (err) {
        handleAdminError(err);
    }
}

// ------------------------------------------------------------
// UPDATE PRODUCT
// ------------------------------------------------------------
export async function adminUpdateProduct(id, payload) {
    try {
        return await api(`${BASE}/admin/products/${id}`, "PATCH", payload);
    } catch (err) {
        handleAdminError(err);
    }
}

// ------------------------------------------------------------
// DELETE PRODUCT
// ------------------------------------------------------------
export async function adminDeleteProduct(id) {
    try {
        return await api(`${BASE}/admin/products/${id}`, "DELETE");
    } catch (err) {
        handleAdminError(err);
    }
}

// ------------------------------------------------------------
// IMAGE UPLOAD (multipart/form-data)
// ------------------------------------------------------------
export async function adminUploadImage(file) {
    try {
        const formData = new FormData();
        formData.append("image", file);

        const res = await fetch(`${BASE}/admin/products/upload-image`, {
            method: "POST",
            credentials: "include",
            body: formData
        });

        if (!res.ok) {
            const error = await res.json().catch(() => ({}));
            throw new Error(error.detail || "Image upload failed");
        }

        return res.json();
    } catch (err) {
        handleAdminError(err);
    }
}