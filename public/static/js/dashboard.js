/* ============================================================
   IMPORTS
============================================================ */
import {
    adminGetProducts,
    adminGetCategories,
    adminCreateProduct,
    adminUpdateProduct,
    adminDeleteProduct,
    adminUploadImage
} from "./admin-api.js";

/* ============================================================
   SIDEBAR TOGGLE (Mobile)
============================================================ */
const sidebar = document.getElementById("sidebar");
const menuBtn = document.getElementById("menu-btn");

menuBtn.addEventListener("click", () => {
    sidebar.classList.toggle("open");
});

/* ============================================================
   ACTIVE NAV ITEM HIGHLIGHT
============================================================ */
document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", () => {
        document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
        item.classList.add("active");
    });
});

/* ============================================================
   MODAL ELEMENTS
============================================================ */
const modal = document.getElementById("productModal");
const overlay = document.getElementById("modalOverlay");
const addBtn = document.getElementById("addProductBtn");
const closeModalBtn = document.getElementById("closeModal");
const cancelModalBtn = document.getElementById("cancelModal");
const form = document.getElementById("productForm");

const idField = document.getElementById("productId");
const nameField = document.getElementById("productName");
const descField = document.getElementById("productDescription");
const priceField = document.getElementById("productPrice");
const stockField = document.getElementById("productStock");
const categoryField = document.getElementById("productCategory");
const imageHiddenField = document.getElementById("productImage");

const imageFileInput = document.getElementById("productImageFile");
const uploadImageBtn = document.getElementById("uploadImageBtn");
const imagePreview = document.getElementById("imagePreview");

let lastFocusedElement = null;

/* ============================================================
   INITIAL LOAD
============================================================ */
document.addEventListener("DOMContentLoaded", async () => {
    await loadCategories();
    await loadProducts();
});

/* ============================================================
   LOAD CATEGORIES
============================================================ */
async function loadCategories() {
    const categories = await adminGetCategories();
    categoryField.innerHTML = "";

    categories.forEach(cat => {
        const option = document.createElement("option");
        option.value = cat.id;
        option.textContent = cat.name;
        categoryField.appendChild(option);
    });
}

/* ============================================================
   LOAD PRODUCTS
============================================================ */
async function loadProducts() {
    const products = await adminGetProducts();
    renderTable(products);
}

/* ============================================================
   RENDER TABLE
============================================================ */
function renderTable(products) {
    const tbody = document.getElementById("productTableBody");
    tbody.innerHTML = "";

    products.forEach(p => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td><img src="${p.image_url}" alt="${p.name}" style="width:50px;border-radius:6px;"></td>
            <td>${p.name}</td>
            <td>£${Number(p.price).toFixed(2)}</td>
            <td>${p.stock}</td>
            <td>${p.category_id}</td>
            <td>
                <button class="btn-secondary" data-id="${p.id}" data-action="edit">
                    <i class="la la-edit"></i> Edit
                </button>
                <button class="btn-primary" style="background:var(--color-accent-orange);" data-id="${p.id}" data-action="delete">
                    <i class="la la-trash"></i> Delete
                </button>
            </td>
        `;

        tbody.appendChild(row);
    });

    tbody.onclick = handleTableClick;
}

/* ============================================================
   TABLE ACTION HANDLER
============================================================ */
function handleTableClick(e) {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;

    const id = btn.dataset.id;
    const action = btn.dataset.action;

    if (action === "edit") openEdit(id);
    if (action === "delete") deleteProduct(id);
}

/* ============================================================
   MODAL OPEN/CLOSE
============================================================ */
function openModal() {
    lastFocusedElement = document.activeElement;

    modal.classList.add("active");
    overlay.classList.add("active");
    nameField.focus();

    document.addEventListener("keydown", handleKeydown);
}

function closeModal() {
    modal.classList.remove("active");
    overlay.classList.remove("active");

    document.removeEventListener("keydown", handleKeydown);

    if (lastFocusedElement) lastFocusedElement.focus();
}

function handleKeydown(e) {
    if (e.key === "Escape") closeModal();
}

addBtn.onclick = () => {
    form.reset();
    idField.value = "";
    imagePreview.style.display = "none";
    document.getElementById("modalTitle").innerText = "Add Product";
    openModal();
};

closeModalBtn.onclick = closeModal;
cancelModalBtn.onclick = closeModal;
overlay.onclick = closeModal;

/* ============================================================
   EDIT PRODUCT
============================================================ */
async function openEdit(id) {
    const p = await adminGetProducts().then(list => list.find(x => x.id === id));

    idField.value = p.id;
    nameField.value = p.name;
    descField.value = p.description;
    priceField.value = p.price;
    stockField.value = p.stock;
    categoryField.value = p.category_id;

    imagePreview.src = p.image_url;
    imagePreview.style.display = "block";
    imageHiddenField.value = p.image_url;

    document.getElementById("modalTitle").innerText = "Edit Product";
    openModal();
}

/* ============================================================
   IMAGE PREVIEW
============================================================ */
imageFileInput.addEventListener("change", () => {
    const file = imageFileInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = e => {
        imagePreview.src = e.target.result;
        imagePreview.style.display = "block";
    };
    reader.readAsDataURL(file);
});

/* ============================================================
   IMAGE UPLOAD
============================================================ */
uploadImageBtn.onclick = async () => {
    const file = imageFileInput.files[0];
    if (!file) return alert("Choose an image first.");

    const data = await adminUploadImage(file);
    imageHiddenField.value = data.url;

    alert("Image uploaded successfully.");
};

/* ============================================================
   FORM SUBMIT (ADD/UPDATE)
============================================================ */
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const product = {
        name: nameField.value.trim(),
        description: descField.value.trim(),
        price: parseFloat(priceField.value),
        stock: parseInt(stockField.value, 10),
        category_id: categoryField.value,
        image_url: imageHiddenField.value
    };

    const id = idField.value;

    if (id) {
        await adminUpdateProduct(id, product);
    } else {
        await adminCreateProduct(product);
    }

    closeModal();
    loadProducts();
});

/* ============================================================
   DELETE PRODUCT
============================================================ */
async function deleteProduct(id) {
    if (!confirm("Delete this product?")) return;
    await adminDeleteProduct(id);
    loadProducts();
}