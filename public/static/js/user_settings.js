/* =========================================================
   USER SETTINGS — FRONTEND ONLY (localStorage)
   Mobile-first, modular, clean
   Works with manual theme system (data-theme="light"/"dark")
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =========================================================
       STORAGE HELPERS
    ========================================================== */
    const saveSetting = (key, value) => {
        localStorage.setItem(key, JSON.stringify(value));
    };

    const loadSetting = (key, fallback = null) => {
        const value = localStorage.getItem(key);
        return value ? JSON.parse(value) : fallback;
    };


    /* =========================================================
       THEME MODE (light / dark)
    ========================================================== */
    const themeToggle = document.getElementById("themeToggle");

    const applyTheme = (theme) => {
        document.documentElement.setAttribute("data-theme", theme);
    };

    if (themeToggle) {
        const savedTheme = loadSetting("themeMode", "light");
        themeToggle.checked = (savedTheme === "dark");
        applyTheme(savedTheme);

        themeToggle.addEventListener("change", () => {
            const newTheme = themeToggle.checked ? "dark" : "light";
            saveSetting("themeMode", newTheme);
            applyTheme(newTheme);
        });
    }


    /* =========================================================
       HIGH CONTRAST MODE
    ========================================================== */
    const contrastToggle = document.getElementById("contrastToggle");

    const applyContrast = (enabled) => {
        document.documentElement.classList.toggle("high-contrast", enabled);
    };

    if (contrastToggle) {
        const savedContrast = loadSetting("highContrast", false);
        contrastToggle.checked = savedContrast;
        applyContrast(savedContrast);

        contrastToggle.addEventListener("change", () => {
            saveSetting("highContrast", contrastToggle.checked);
            applyContrast(contrastToggle.checked);
        });
    }


    /* =========================================================
       TEXT SIZE (90% – 130%)
    ========================================================== */
    const textSizeRange = document.getElementById("textSizeRange");
    const textPreview = document.querySelector(".text-preview");

    const applyTextSize = (size) => {
        document.documentElement.style.fontSize = `${size}%`;
        if (textPreview) textPreview.style.fontSize = `${size}%`;
    };

    if (textSizeRange) {
        const savedTextSize = loadSetting("textSize", 100);
        textSizeRange.value = savedTextSize;
        applyTextSize(savedTextSize);

        textSizeRange.addEventListener("input", () => {
            const size = textSizeRange.value;
            saveSetting("textSize", size);
            applyTextSize(size);
        });
    }


    /* =========================================================
       NOTIFICATIONS
    ========================================================== */
    const notificationToggle = document.getElementById("notificationToggle");

    if (notificationToggle) {
        const savedNotifications = loadSetting("notificationsEnabled", false);
        notificationToggle.checked = savedNotifications;

        notificationToggle.addEventListener("change", () => {
            saveSetting("notificationsEnabled", notificationToggle.checked);
        });
    }


    /* =========================================================
       EMAIL ALERTS
    ========================================================== */
    const emailToggle = document.getElementById("emailToggle");

    if (emailToggle) {
        const savedEmailAlerts = loadSetting("emailAlerts", false);
        emailToggle.checked = savedEmailAlerts;

        emailToggle.addEventListener("change", () => {
            saveSetting("emailAlerts", emailToggle.checked);
        });
    }


    /* =========================================================
       DEVICE PERMISSIONS
    ========================================================== */
    const deviceToggles = {
        locationToggle: "deviceLocation",
        cameraToggle: "deviceCamera",
        micToggle: "deviceMic"
    };

    Object.entries(deviceToggles).forEach(([id, key]) => {
        const el = document.getElementById(id);
        if (!el) return;

        const saved = loadSetting(key, false);
        el.checked = saved;

        el.addEventListener("change", () => {
            saveSetting(key, el.checked);
        });
    });


    /* =========================================================
       DEBUG LOG
    ========================================================== */
    console.log("%cUser settings loaded from localStorage", "color:#4CAF50");
});