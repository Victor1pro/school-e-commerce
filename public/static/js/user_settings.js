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
       Stored as: "light" | "dark"
    ========================================================== */
    const themeToggle = document.getElementById("themeToggle");

    const applyTheme = (theme) => {
        document.documentElement.setAttribute("data-theme", theme);
    };

    // Load saved theme (default = light)
    const savedTheme = loadSetting("themeMode", "light");
    themeToggle.checked = (savedTheme === "dark");
    applyTheme(savedTheme);

    themeToggle.addEventListener("change", () => {
        const newTheme = themeToggle.checked ? "dark" : "light";
        saveSetting("themeMode", newTheme);
        applyTheme(newTheme);
    });


    /* =========================================================
       HIGH CONTRAST MODE
    ========================================================== */
    const contrastToggle = document.getElementById("contrastToggle");

    const applyContrast = (enabled) => {
        document.documentElement.classList.toggle("high-contrast", enabled);
    };

    const savedContrast = loadSetting("highContrast", false);
    contrastToggle.checked = savedContrast;
    applyContrast(savedContrast);

    contrastToggle.addEventListener("change", () => {
        saveSetting("highContrast", contrastToggle.checked);
        applyContrast(contrastToggle.checked);
    });


    /* =========================================================
       TEXT SIZE (90% – 130%)
    ========================================================== */
    const textSizeRange = document.getElementById("textSizeRange");
    const textPreview = document.querySelector(".text-preview");

    const applyTextSize = (size) => {
        document.documentElement.style.fontSize = `${size}%`;
        textPreview.style.fontSize = `${size}%`;
    };

    const savedTextSize = loadSetting("textSize", 100);
    textSizeRange.value = savedTextSize;
    applyTextSize(savedTextSize);

    textSizeRange.addEventListener("input", () => {
        const size = textSizeRange.value;
        saveSetting("textSize", size);
        applyTextSize(size);
    });


    /* =========================================================
       NOTIFICATIONS (frontend only)
    ========================================================== */
    const notificationToggle = document.getElementById("notificationToggle");

    const savedNotifications = loadSetting("notificationsEnabled", false);
    notificationToggle.checked = savedNotifications;

    notificationToggle.addEventListener("change", () => {
        saveSetting("notificationsEnabled", notificationToggle.checked);
    });


    /* =========================================================
       EMAIL ALERTS (frontend only)
    ========================================================== */
    const emailToggle = document.getElementById("emailToggle");

    const savedEmailAlerts = loadSetting("emailAlerts", false);
    emailToggle.checked = savedEmailAlerts;

    emailToggle.addEventListener("change", () => {
        saveSetting("emailAlerts", emailToggle.checked);
    });


    /* =========================================================
       DEVICE PERMISSIONS (local only)
    ========================================================== */
    const deviceToggles = {
        locationToggle: "deviceLocation",
        cameraToggle: "deviceCamera",
        micToggle: "deviceMic"
    };

    Object.entries(deviceToggles).forEach(([id, key]) => {
        const el = document.getElementById(id);
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