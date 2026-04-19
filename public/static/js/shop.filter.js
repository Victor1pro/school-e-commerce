/* ============================================================
   DYNAMIC FILTER ENGINE
   - Watches category + price toggles
   - Builds query params
   - Fetches filtered products
   - Renders product grid
============================================================ */

document.addEventListener("DOMContentLoaded", () => {

    const categoryFilters = document.querySelectorAll(".filter-category");
    const priceFilters = document.querySelectorAll(".filter-price");
    const productGrid = document.getElementById("product-grid");

    const API_URL = "http://127.0.0.1:9000/products"; // your FastAPI endpoint


    /* ============================================================
       BUILD FILTER QUERY
    ============================================================= */
    const buildQuery = () => {
        const categories = [...categoryFilters]
            .filter(c => c.checked)
            .map(c => c.value);

        const prices = [...priceFilters]
            .filter(p => p.checked)
            .map(p => p.value);

        const params = new URLSearchParams();

        if (categories.length > 0) {
            params.append("categories", categories.join(","));
        }

        if (prices.length > 0) {
            params.append("prices", prices.join(","));
        }

        return params.toString();
    };


    /* ============================================================
       FETCH FILTERED PRODUCTS
    ============================================================= */
    const fetchProducts = async () => {
        const query = buildQuery();
        const url = query ? `${API_URL}?${query}` : API_URL;

        try {
            const res = await fetch(url);
            const data = await res.json();
            renderProducts(data);
        } catch (err) {
            console.error("Failed to load products:", err);
        }
    };


    /* ============================================================
       RENDER PRODUCTS
       (Uses your existing product card renderer)
    ============================================================= */
    const renderProducts = (products) => {
        productGrid.innerHTML = "";

        if (!products || products.length === 0) {
            productGrid.innerHTML = `<p>No products found.</p>`;
            return;
        }

        products.forEach(product => {
            const card = `
                <div class="product-card">
                    <img src="${product.image_url}" alt="${product.name}">
                    <h3>${product.name}</h3>
                    <p>${product.description}</p>
                    <span class="price">£${product.price}</span>
                    <button class="btn-primary" onclick="addToCart('${product.id}')">
                        Add to Cart
                    </button>
                </div>
            `;
            productGrid.insertAdjacentHTML("beforeend", card);
        });
    };


    /* ============================================================
       WATCH FILTERS
    ============================================================= */
    [...categoryFilters, ...priceFilters].forEach(filter => {
        filter.addEventListener("change", fetchProducts);
    });


    /* ============================================================
       INITIAL LOAD
    ============================================================= */
    fetchProducts();
});