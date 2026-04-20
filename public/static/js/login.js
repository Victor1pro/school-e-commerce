/* ============================================================
   LOGIN PAGE SCRIPT (Unified User + Admin)
   ------------------------------------------------------------
   - Real-time validation
   - Submit disabled until valid
   - Password reveal toggle
   - Uses loginUser() from auth.js
   - Detects admin-login.html automatically
   - Handles admin spinner + role check
============================================================ */

import { loginUser, showPopup } from "./auth.js";
import {
    validateEmail,
    validateLoginPassword,
    markInvalid,
    markValid
} from "./auth_functions.js";

/* ------------------------------------------------------------
   DETECT LOGIN MODE
   - If URL contains "admin-login", treat as admin login page
------------------------------------------------------------ */
const isAdminLogin = window.location.pathname.includes("admin-login");

const loginForm = document.querySelector(".auth-form");

if (loginForm) {
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const submitBtn = document.querySelector(".auth-submit");

    /* ============================================================
       PASSWORD REVEAL TOGGLE
    ============================================================ */
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

    attachPasswordToggle(passwordInput);

    /* ============================================================
       ENABLE/DISABLE SUBMIT BUTTON
    ============================================================ */
    function updateSubmitState() {
        const valid =
            emailInput.classList.contains("valid") &&
            passwordInput.classList.contains("valid");

        submitBtn.disabled = !valid;
        submitBtn.style.opacity = valid ? "1" : "0.5";
    }

    /* ============================================================
       REAL-TIME VALIDATION
    ============================================================ */
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

    /* ============================================================
       SUBMIT HANDLER (Unified)
       ------------------------------------------------------------
       - Normal login → loginUser(email, pass)
       - Admin login → loginUser(email, pass, true)
       - Includes spinner + role check
    ============================================================ */
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Spinner state
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i class="la la-spinner la-spin"></i> Logging in...`;

        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        // Call unified loginUser()
        const success = await loginUser(email, password, isAdminLogin);

        if (!success) {
            showPopup("Login failed", "error");
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<i class="la la-unlock"></i> Login`;
            return;
        }

        // loginUser() handles redirects internally
    });
}