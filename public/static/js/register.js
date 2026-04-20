/* ============================================================
   REGISTER PAGE SCRIPT (Unified User + Admin)
   ------------------------------------------------------------
   - Real-time validation
   - Password strength meter
   - Submit disabled until valid
   - Password reveal toggle
   - Uses registerUser() from auth.js
   - Detects admin-register.html automatically
============================================================ */

import { registerUser, showPopup } from "./auth.js";
import {
    validateEmail,
    validatePassword,
    markInvalid,
    markValid
} from "./auth_functions.js";

/* ------------------------------------------------------------
   DETECT REGISTRATION MODE
   - If the page filename contains "admin-register"
   - We treat this as an admin registration page
------------------------------------------------------------ */
const isAdminRegister = window.location.pathname.includes("admin-register");

const registerForm = document.querySelector(".auth-form");

if (registerForm) {
    const nameInput = document.getElementById("fullname");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const confirmInput = document.getElementById("confirm-password");
    const submitBtn = document.querySelector(".auth-submit");

    const strengthBar = document.querySelector(".strength-bar");
    const strengthLabel = document.querySelector(".strength-label");

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
    attachPasswordToggle(confirmInput);

    /* ============================================================
       PASSWORD STRENGTH METER
    ============================================================ */
    function getPasswordStrength(password) {
        let score = 0;
        if (password.length >= 12) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[a-z]/.test(password)) score++;
        if (/\d/.test(password)) score++;
        if (/[@$!%*?&]/.test(password)) score++;
        return score;
    }

    function updateStrengthMeter(password) {
        const score = getPasswordStrength(password);
        strengthBar.className = "strength-bar";

        if (score <= 1) {
            strengthBar.style.width = "20%";
            strengthBar.classList.add("strength-weak");
            strengthLabel.textContent = "Weak";
        } else if (score === 2) {
            strengthBar.style.width = "40%";
            strengthBar.classList.add("strength-medium");
            strengthLabel.textContent = "Medium";
        } else if (score === 3) {
            strengthBar.style.width = "60%";
            strengthBar.classList.add("strength-strong");
            strengthLabel.textContent = "Strong";
        } else if (score >= 4) {
            strengthBar.style.width = "100%";
            strengthBar.classList.add("strength-very-strong");
            strengthLabel.textContent = "Very Strong";
        }
    }

    /* ============================================================
       ENABLE/DISABLE SUBMIT BUTTON
    ============================================================ */
    function updateSubmitState() {
        const isValid =
            nameInput.classList.contains("valid") &&
            emailInput.classList.contains("valid") &&
            passwordInput.classList.contains("valid") &&
            confirmInput.classList.contains("valid");

        submitBtn.disabled = !isValid;
        submitBtn.style.opacity = isValid ? "1" : "0.5";
        submitBtn.style.cursor = isValid ? "pointer" : "not-allowed";
    }

    /* ============================================================
       REAL-TIME VALIDATION
    ============================================================ */
    nameInput.addEventListener("input", () => {
        if (nameInput.value.trim().length < 3) {
            markInvalid(nameInput, "Name must be at least 3 characters");
        } else {
            markValid(nameInput);
        }
        updateSubmitState();
    });

    emailInput.addEventListener("input", () => {
        if (!validateEmail(emailInput.value)) {
            markInvalid(emailInput, "Enter a valid email address");
        } else {
            markValid(emailInput);
        }
        updateSubmitState();
    });

    passwordInput.addEventListener("input", () => {
        updateStrengthMeter(passwordInput.value);

        if (!validatePassword(passwordInput.value)) {
            markInvalid(
                passwordInput,
                "12–16 chars, upper, lower, number & symbol required"
            );
        } else {
            markValid(passwordInput);
        }
        updateSubmitState();
    });

    confirmInput.addEventListener("input", () => {
        if (confirmInput.value !== passwordInput.value) {
            markInvalid(confirmInput, "Passwords do not match");
        } else {
            markValid(confirmInput);
        }
        updateSubmitState();
    });

    /* ============================================================
       SUBMIT HANDLER (Unified)
       ------------------------------------------------------------
       - Normal register → registerUser(name, email, pass)
       - Admin register → registerUser(name, email, pass, true)
    ============================================================ */
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const name = nameInput.value.trim();
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        const success = await registerUser(name, email, password, isAdminRegister);

        if (!success) {
            showPopup("Registration failed", "error");
        }
    });
}