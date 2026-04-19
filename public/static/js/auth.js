/* ============================================================
   AUTH MODULE (Unified)
   - Register
   - Login
   - Logout
   - Popup system
   - LocalStorage user object
============================================================ */

const API_URL = "http://127.0.0.1:9000/auth/users";

/* ------------------------------------------------------------
   POPUP (Glassmorphism)
------------------------------------------------------------ */
export function showPopup(message, type = "success") {
    const popup = document.createElement("div");
    popup.className = `popup ${type}`;
    popup.innerHTML = `
        <div class="popup-content">
            <p>${message}</p>
        </div>
    `;

    document.body.appendChild(popup);

    setTimeout(() => popup.classList.add("show"), 10);
    setTimeout(() => popup.classList.remove("show"), 2500);
    setTimeout(() => popup.remove(), 3000);
}

/* ============================================================
   REGISTER USER
============================================================ */
export async function registerUser(name, email, password) {
    const payload = { name, email, password };

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            showPopup(err.detail || "Registration failed", "error");
            return null;
        }

        showPopup("Account created successfully!");

        setTimeout(() => {
            window.location.href = "/public/pages/login.html";
        }, 1500);

        return true;

    } catch (error) {
        console.error("Registration error:", error);
        showPopup("Something went wrong.", "error");
        return null;
    }
}

/* ============================================================
   LOGIN USER (Unified)
============================================================ */
export async function loginUser(email, password) {
    const payload = { email, password };

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            showPopup(err.detail || "Login failed", "error");
            return null;
        }

        const data = await response.json();

        // Store full user object
        localStorage.setItem("user", JSON.stringify(data.user));

        showPopup(`Welcome back, ${data.user.name}!`);

        setTimeout(() => {
            window.location.href = "/public/pages/shop.html";
        }, 1200);

        return true;

    } catch (error) {
        console.error("Login error:", error);
        showPopup("Something went wrong.", "error");
        return null;
    }
}

/* ============================================================
   LOGOUT USER (Unified)
============================================================ */
export async function logoutUser() {
    try {
        const response = await fetch(`${API_URL}/logout`, {
            method: "POST",
            credentials: "include"
        });

        if (!response.ok) {
            showPopup("Logout failed", "error");
            return;
        }

        // Remove all user data
        localStorage.removeItem("user");
        localStorage.removeItem("user_name"); // cleanup old key
        sessionStorage.clear();

        showPopup("You have been logged out");

        setTimeout(() => {
            window.location.assign("/public/pages/shop.html");
            console.log("LOGOUT SUCCESS — redirecting...");
        }, 1200);

    } catch (error) {
        console.error("Logout error:", error);
        showPopup("Something went wrong.", "error");
    }
}