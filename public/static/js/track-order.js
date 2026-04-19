/* ============================================================
   POPUP HANDLER
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
   RENDER ORDER SUMMARY
============================================================ */
function renderSummary(order) {
  const container = document.getElementById("track-order-summary");

  container.innerHTML = `
    <div><strong>Order ID:</strong> ${order.id}</div>
    <div><strong>Date:</strong> ${new Date(order.created_at).toLocaleDateString()}</div>
    <div><strong>Status:</strong> ${order.status}</div>
    <div><strong>Total:</strong> £${order.total_amount.toFixed(2)}</div>
  `;
}


/* ============================================================
   RENDER SHIPPING INFO
============================================================ */
function renderShipping(order) {
  const ship = order.shipping;
  const container = document.getElementById("track-shipping");

  container.innerHTML = `
    <div><strong>Name:</strong> ${ship.full_name}</div>
    <div><strong>Address:</strong> ${ship.address_line1}</div>
    <div><strong>City:</strong> ${ship.city}</div>
    <div><strong>Postcode:</strong> ${ship.postcode}</div>
    <div><strong>Method:</strong> ${ship.shipping_method}</div>
  `;
}


/* ============================================================
   ICON MAP
============================================================ */
const statusIcons = {
  processing: "la-cog",
  packed: "la-box",
  shipped: "la-truck",
  out_for_delivery: "la-shipping-fast",
  delivered: "la-check-circle",
  delayed: "la-clock",
  cancelled: "la-times-circle"
};


/* ============================================================
   RENDER TIMELINE WITH ICONS
============================================================ */
function renderTimeline(order) {
  const container = document.getElementById("track-timeline");
  container.innerHTML = "";

  order.tracking_updates.forEach((update, index) => {
    const iconClass = statusIcons[update.status] || "la-info-circle";
    const color = statusColors[update.status] || "var(--color-primary)";

    const div = document.createElement("div");
    div.className = "timeline-item";

    // Mark active item
    if (index === order.tracking_updates.length - 1) {
      div.classList.add("active");
    }

    div.innerHTML = `
      <div class="timeline-icon" style="background:${color}">
        <i class="la ${iconClass}"></i>
      </div>

      <div class="timeline-status" style="color:${color}">
        ${update.status.replace(/_/g, " ")}
      </div>

      <div class="timeline-date">${new Date(update.updated_at).toLocaleString()}</div>
      <div class="timeline-location">${update.location || "—"}</div>
    `;

    container.appendChild(div);
  });

  updateProgressBar(order);
}


/* ============================================================
   FETCH ORDER
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

    renderSummary(order);
    renderShipping(order);
    renderTimeline(order);

  } catch (error) {
    showPopup("Network error. Please try again.", "error");
  }
}


function updateProgressBar(order) {
  const bar = document.querySelector(".progress-bar");

  const statuses = [
    "processing",
    "packed",
    "shipped",
    "out_for_delivery",
    "delivered"
  ];

  const currentIndex = statuses.indexOf(order.status);
  const progressPercent = ((currentIndex + 1) / statuses.length) * 100;

  bar.style.width = `${progressPercent}%`;
  bar.style.background = statusColors[order.status] || "var(--color-primary)";
}





/* ============================================================
   INIT
============================================================ */
document.addEventListener("DOMContentLoaded", loadOrder);



