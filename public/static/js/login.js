// ============================================================
// LOGIN PAGE SCRIPT
// - Real-time validation
// - Submit disabled until valid
// - Password reveal toggle (Line Awesome)
// - Uses showPopup() for all messages
// ============================================================

import { loginUser, showPopup } from "./auth.js";
import {
    validateEmail,
    validateLoginPassword,
    markInvalid,
    markValid
} from "./auth_functions.js";

const loginForm = document.querySelector(".auth-form");

if (loginForm) {
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const submitBtn = document.querySelector(".auth-submit");

    // ============================================================
    // PASSWORD REVEAL TOGGLE (Reusable function)
    // ============================================================
    function attachPasswordToggle(inputEl) {
        const icon = document.createElement("i");
        icon.className = "la la-eye password-toggle";
        inputEl.parentElement.appendChild(icon);

        icon.addEventListener("click", () => {
            const isPassword = inputEl.type === "password";
            inputEl.type = isPassword ? "text" : "password";
            icon.classList.toggle("la-eye");
            icon.classList.toggle("la-eye-slash");
        });
    }

    // Attach toggle to login password field
    attachPasswordToggle(passwordInput);

    // ============================================================
    // ENABLE/DISABLE SUBMIT BUTTON
    // ============================================================
    function updateSubmitState() {
        const valid =
            emailInput.classList.contains("valid") &&
            passwordInput.classList.contains("valid");

        submitBtn.disabled = !valid;
        submitBtn.style.opacity = valid ? "1" : "0.5";
    }

    // ============================================================
    // REAL-TIME VALIDATION
    // ============================================================
    emailInput.addEventListener("input", () => {
        validateEmail(emailInput.value)
            ? markValid(emailInput)
            : markInvalid(emailInput, "Invalid email format");
        updateSubmitState();
    });

    passwordInput.addEventListener("input", () => {
        validateLoginPassword(passwordInput.value)
            ? markValid(passwordInput)
            : markInvalid(passwordInput, "Password must be 12–16 characters");
        updateSubmitState();
    });

    // ============================================================
    // SUBMIT HANDLER
    // ============================================================
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const success = await loginUser(
            emailInput.value.trim(),
            passwordInput.value.trim()
        );

        if (!success) showPopup("Login failed", "error");
    });
}
