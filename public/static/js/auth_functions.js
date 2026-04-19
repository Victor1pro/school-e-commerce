// ============================================================
// AUTH VALIDATION HELPERS
// - Pure validation logic (no DOM manipulation)
// - Used by register.js and login.js
// ============================================================

export function hasNoWhitespace(value) {
  return !/\s/.test(value);
}

export function validateEmail(value) {
  if (!hasNoWhitespace(value)) return false;
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(value);
}

export function validatePassword(value) {
  if (!hasNoWhitespace(value)) return false;
  const pattern =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,16}$/;
  return pattern.test(value);
}

export function validateUKPhone(phone) {
  const pattern = /^(?:0|\+44)\d{10}$/;
  return pattern.test(phone);
}

export function validateLoginPassword(value) {
  return hasNoWhitespace(value) && value.length >= 12 && value.length <= 16;
}


// ============================================================
// UI VALIDATION HELPERS
// - Adds red/green borders
// - Shows inline error messages
// ============================================================

export function markInvalid(inputEl, message) {
  inputEl.classList.remove("valid");
  inputEl.classList.add("invalid");

  let msg = inputEl.parentElement.querySelector(".input-error");
  if (!msg) {
    msg = document.createElement("small");
    msg.className = "input-error";
    inputEl.parentElement.appendChild(msg);
  }
  msg.textContent = message;
}

export function markValid(inputEl) {
  inputEl.classList.remove("invalid");
  inputEl.classList.add("valid");

  const msg = inputEl.parentElement.querySelector(".input-error");
  if (msg) msg.remove();
}