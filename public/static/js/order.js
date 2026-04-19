/* ============================================================
   POPUP HANDLER (same system used in checkout.js)
============================================================ */
function showPopup(message, type = "info") {
  const popup = document.getElementById("popup");
  const msg = document.getElementById("popup-message");
  const icon = document.getElementById("popup-icon");

  popup.classList.remove("success", "error", "info");
  popup.classList.add(type);

  if (type === "success") icon.className = "la la-check-circle popup-icon";
  else if (type === "error") icon.className = "la la-times-circle popup-icon";
  else icon.className = "la la-info-circle popup-icon";

  msg.textContent = message;
  popup.classList.add("show");

  document.getElementById("popup-close").onclick = () => {
    popup.classList.remove("show");
  };
}


/* ============================================================
   GET ORDER ID FROM URL
============================================================ */
function getOrderIdFromURL() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}


/* ============================================================
   POPULATE ORDER PAGE
============================================================ */
function renderOrder(order) {
  // Header
  document.getElementById("order-id").textContent = order.id;
  document.getElementById("order-date").textContent = new Date(order.created_at).toLocaleDateString();
  document.getElementById("order-status").textContent = order.status;

  // Items container
  const itemsContainer = document.getElementById("order-items");
  itemsContainer.innerHTML = "";

  order.items.forEach(item => {
    const div = document.createElement("div");
    div.className = "order-item";

    div.innerHTML = `
      <div>
        <div class="order-item-name">${item.product.name}</div>
        <div class="order-item-qty">Qty: ${item.quantity}</div>
      </div>
      <div class="order-item-price">£${(item.price_at_purchase * item.quantity).toFixed(2)}</div>
    `;

    itemsContainer.appendChild(div);
  });

  // Total
  document.getElementById("order-total").textContent = `£${order.total_amount.toFixed(2)}`;

  // Shipping
  if (order.shipping) {
    document.getElementById("ship-name").textContent = order.shipping.full_name;
    document.getElementById("ship-address").textContent = order.shipping.address_line1;
    document.getElementById("ship-city").textContent = order.shipping.city;
    document.getElementById("ship-postcode").textContent = order.shipping.postcode;
    document.getElementById("ship-method").textContent = order.shipping.shipping_method;
  }

  // Tracking
  const trackingContainer = document.getElementById("order-tracking");
  trackingContainer.innerHTML = "";

  order.tracking_updates.forEach(update => {
    const div = document.createElement("div");
    div.className = "tracking-item";

    div.innerHTML = `
      <div class="tracking-status"><i class="la la-map-marker"></i> ${update.status}</div>
      <div class="tracking-location">${update.location || "—"}</div>
      <div class="tracking-date">${new Date(update.updated_at).toLocaleString()}</div>
    `;

    trackingContainer.appendChild(div);
  });
}


/* ============================================================
   FETCH ORDER FROM BACKEND
============================================================ */
async function loadOrder() {
  const orderId = getOrderIdFromURL();

  if (!orderId) {
    showPopup("No order ID provided.", "error");
    return;
  }

  try {
    const res = await fetch(`http://127.0.0.1:9000/orders/${orderId}`, {
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      }
    });

    if (!res.ok) {
      const err = await res.json();
      showPopup(err.detail || "Unable to load order.", "error");
      return;
    }

    const order = await res.json();
    renderOrder(order);

  } catch (error) {
    showPopup("Network error. Please try again.", "error");
  }
}


/* ============================================================
   INIT
============================================================ */
document.addEventListener("DOMContentLoaded", loadOrder);