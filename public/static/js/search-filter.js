/**
 * Search & Filter Frontend Script
 *
 * Handles:
 * - Category toggle filters
 * - Price toggle filters
 * - Live product filtering
 * - Search results page loading
 * - Live suggestions dropdown
 *
 * This script communicates with:
 *   GET /search/suggest
 *   GET /search/
 */

const API_BASE = "http://127.0.0.1:9000";   // FastAPI backend base URL


// ============================================================
// PAGE ROUTER — Detect which page we are on
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    const searchPage = document.getElementById("search-results-page");

    if (searchPage) {
        loadSearchResults();   // Load results for ?q=...
    }
});


// ============================================================
// LOAD SEARCH RESULTS PAGE
// ============================================================
async function loadSearchResults() {
    /**
     * Loads products based on the search query (?q=...)
     * and renders them in the product grid.
     */

    const params = new URLSearchParams(window.location.search);
    const q = params.get("q");

    if (!q) return;

    try {
        const res = await fetch(`${API_BASE}/search/?q=${encodeURIComponent(q)}`);
        const products = await res.json();

        renderProducts(products);

    } catch (error) {
        console.error("Error loading search results:", error);
    }
}


// ============================================================
// FILTER SIDEBAR LOGIC
// ============================================================
const categoryFilters = document.querySelectorAll(".filter-category");
const priceFilters = document.querySelectorAll(".filter-price");

categoryFilters.forEach(f => f.addEventListener("change", applyFilters));
priceFilters.forEach(f => f.addEventListener("change", applyFilters));

async function applyFilters() {
    /**
     * Collects selected filters, builds query parameters,
     * sends request to FastAPI, and updates product grid.
     */

    const selectedCategories = [...categoryFilters]
        .filter(f => f.checked)
        .map(f => f.value);

    const selectedPrices = [...priceFilters]
        .filter(f => f.checked)
        .map(f => f.value);

    const params = new URLSearchParams();

    if (selectedCategories.length === 1) {
        params.append("category", selectedCategories[0]);
    }

    if (selectedPrices.length === 1) {
        const [min, max] = selectedPrices[0].split("-");
        params.append("min_price", min);
        params.append("max_price", max);
    }

    try {
        const res = await fetch(`${API_BASE}/search/?${params.toString()}`);
        const products = await res.json();

        renderProducts(products);

    } catch (error) {
        console.error("Error applying filters:", error);
    }
}


// ============================================================
// LIVE SEARCH SUGGESTIONS
// ============================================================
const searchInput = document.getElementById("header-search-input");
const suggestionsBox = document.createElement("div");
suggestionsBox.classList.add("search-suggestions");

const searchContainer = document.querySelector(".header-search");
if (searchContainer) searchContainer.appendChild(suggestionsBox);

let debounceTimer;

if (searchInput) {
    searchInput.addEventListener("input", () => {
        const q = searchInput.value.trim();

        clearTimeout(debounceTimer);

        if (q.length < 2) {
            suggestionsBox.style.display = "none";
            return;
        }

        debounceTimer = setTimeout(() => fetchSuggestions(q), 200);
    });
}

async function fetchSuggestions(q) {
    try {
        const res = await fetch(`${API_BASE}/search/suggest?q=${encodeURIComponent(q)}`);
        const suggestions = await res.json();

        if (!suggestions.length) {
            suggestionsBox.style.display = "none";
            return;
        }

        suggestionsBox.innerHTML = suggestions
            .map(s => `<div class="suggestion-item" data-id="${s.id}">${s.name}</div>`)
            .join("");

        suggestionsBox.style.display = "block";

    } catch (error) {
        console.error("Suggestion fetch error:", error);
    }
}

suggestionsBox.addEventListener("click", (e) => {
    const item = e.target.closest(".suggestion-item");
    if (!item) return;

    const id = item.dataset.id;
    window.location.href = `/public/pages/product.html?id=${id}`;
});


// ============================================================
// OVERRIDE SEARCH FORM SUBMIT
// ============================================================
const searchForm = document.querySelector(".header-search");

if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const q = searchInput.value.trim();
        if (!q) return;

        window.location.href = `/public/pages/search.html?q=${encodeURIComponent(q)}`;
    });
}