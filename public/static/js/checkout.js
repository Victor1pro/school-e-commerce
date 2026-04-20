/* ============================================================
   PROGRESS STEPS
============================================================ */
const progressSteps = document.querySelectorAll('.checkout-progress .step');
const sections = document.querySelectorAll('.checkout-section');

function setActiveStep(index) {
  progressSteps.forEach((step, i) => {
    step.classList.toggle('active', i === index);
  });
}

// Link <details> open state to progress bar
sections.forEach(section => {
  section.addEventListener('toggle', () => {
    if (section.open) {
      const stepIndex = parseInt(section.dataset.stepIndex, 10);
      setActiveStep(stepIndex);
    }
  });
});

// Clicking a step scrolls to that section
progressSteps.forEach(step => {
  step.addEventListener('click', () => {
    const index = parseInt(step.dataset.step, 10);
    const targetSection = [...sections].find(
      s => parseInt(s.dataset.stepIndex, 10) === index
    );
    if (targetSection) {
      targetSection.open = true;
      targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});


/* ============================================================
   CREDIT CARD PREVIEW
============================================================ */
const cardNumberInput = document.getElementById('cardnum');
const cardNameInput = document.getElementById('fullname');
const cardExpInput = document.getElementById('exp');
const cardCvvInput = document.getElementById('cvv');

const previewNumber = document.getElementById('card-preview-number');
const previewName = document.getElementById('card-preview-name');
const previewExp = document.getElementById('card-preview-exp');
const previewCvv = document.getElementById('card-preview-cvv');

function formatCardNumber(value) {
  return value
    .replace(/\D/g, '')
    .substring(0, 16)
    .replace(/(.{4})/g, '$1 ')
    .trim();
}

cardNumberInput.addEventListener('input', () => {
  const formatted = formatCardNumber(cardNumberInput.value);
  cardNumberInput.value = formatted;
  previewNumber.textContent = formatted || '1234 5678 9012 3456';
});

cardNameInput.addEventListener('input', () => {
  const value = cardNameInput.value.trim();
  previewName.textContent = value ? value.toUpperCase() : 'JOHN DOE';
});

cardExpInput.addEventListener('input', () => {
  let value = cardExpInput.value.replace(/[^\d]/g, '').substring(0, 4);
  if (value.length >= 3) {
    value = value.substring(0, 2) + '/' + value.substring(2);
  }
  cardExpInput.value = value;
  previewExp.textContent = value || 'MM/YY';
});

cardCvvInput.addEventListener('input', () => {
  const value = cardCvvInput.value.replace(/\D/g, '').substring(0, 3);
  cardCvvInput.value = value;
  previewCvv.textContent = value ? '•'.repeat(value.length) : '•••';
});


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
   CHECKOUT SUBMISSION
============================================================ */
const placeOrderBtn = document.getElementById('place-order-btn');

placeOrderBtn.addEventListener('click', async () => {
  // Move to review step visually
  setActiveStep(4);

  // Collect form data
  const payload = {
    full_name: document.getElementById('fullname').value,
    email: document.getElementById('email').value,
    address: document.getElementById('address').value,
    city: document.getElementById('city').value,
    postcode: document.getElementById('postcode').value,
    card_number: document.getElementById('cardnum').value,
    expiry: document.getElementById('exp').value,
    cvv: document.getElementById('cvv').value
  };

  // Basic validation
  if (!payload.full_name || !payload.email || !payload.address || !payload.city || !payload.postcode) {
    showPopup("Please fill in all required fields.", "error");
    return;
  }

  // Loading state
  placeOrderBtn.disabled = true;
  placeOrderBtn.textContent = "Processing...";

  try {
      const res = await fetch("http://127.0.0.1:9000/checkout/", {
      method: "POST",
      credentials: "include",   // <-- CRITICAL
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      showPopup(err.detail || "Checkout failed.", "error");
      placeOrderBtn.disabled = false;
      placeOrderBtn.textContent = "Place Order";
      return;
    }

    const order = await res.json();

    // Success popup
    showPopup("Order placed successfully!", "success");

    // Redirect after short delay
    setTimeout(() => {
      window.location.href = "public/pages/order.html";
    }, 1500);

  } catch (error) {
    showPopup("Network error. Please try again.", "error");
    placeOrderBtn.disabled = false;
    placeOrderBtn.textContent = "Place Order";
  }
});