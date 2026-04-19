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
   RENDER ORDER HISTORY
============================================================ */
function renderOrderHistory(orders) {
  const container = document.getElementById("order-history-list");
  container.innerHTML = "";

  if (orders.length === 0) {
    container.innerHTML = `
      <p style="text-align:center; color:var(--role-text-muted);">
        You have no past orders yet.
      </p>
    `;
    return;
  }

  orders.forEach(order => {
    const card = document.createElement("div");
    card.className = "order-card";

    const statusClass =
      order.status === "completed" ? "status-completed" :
      order.status === "cancelled" ? "status-cancelled" :
      "status-processing";

    card.innerHTML = `
      <div class="order-row">
        <span class="order-id">Order #${order.id}</span>
        <span class="order-status ${statusClass}">${order.status}</span>
      </div>

      <div class="order-row">
        <span>Date:</span>
        <span>${new Date(order.created_at).toLocaleDateString()}</span>
      </div>

      <div class="order-row">
        <span>Total:</span>
        <span>£${order.total_amount.toFixed(2)}</span>
      </div>

      <a href="/track-order.html?id=${order.id}" class="view-btn">
        View Order
      </a>
    `;

    container.appendChild(card);
  });
}


/* ============================================================
   FETCH ORDER HISTORY
============================================================ */
async function loadOrderHistory() {
  try {
    const res = await fetch("http://127.0.0.1:9000/orders/history", {
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      }
    });

    if (!res.ok) {
      const err = await res.json();
      showPopup(err.detail || "Unable to load order history.", "error");
      return;
    }

    const orders = await res.json();
    renderOrderHistory(orders);

  } catch (error) {
    showPopup("Network error. Please try again.", "error");
  }
}


/* ============================================================
   INIT
============================================================ */
document.addEventListener("DOMContentLoaded", loadOrderHistory);