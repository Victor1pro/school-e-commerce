// ============================================================
// CATEGORY API MODULE (Clean, Minimal, Reusable)
// ============================================================

const CATEGORY_API_URL = "http://127.0.0.1:9000/categories/";

/**
 * Fetch all categories from the backend.
 * Returns an array of category objects.
 */
export async function getAllCategories() {
  try {
    const res = await fetch(CATEGORY_API_URL);
    if (!res.ok) throw new Error("Failed to load categories");
    return await res.json();
  } catch (err) {
    console.error("getAllCategories() error:", err);
    return [];
  }
}

/**
 * Fetch a single category by ID.
 * Returns a category object or null.
 */
export async function getCategoryById(id) {
  try {
    const res = await fetch(`${CATEGORY_API_URL}${id}`);
    if (!res.ok) throw new Error("Category not found");
    return await res.json();
  } catch (err) {
    console.error("getCategoryById() error:", err);
    return null;
  }
}