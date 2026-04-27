/* =========================================================
   SETTINGS SYNC LAYER
   Syncs frontend localStorage settings with backend API.
   Works with FastAPI + JWT auth.
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =========================================================
       CONFIG
    ========================================================== */
    const API_URL = "http://127.0.0.1:9000/settings";   // FIXED
    const TOKEN_KEY = "access_token";                   // JWT stored in localStorage


    /* =========================================================
       HELPERS
    ========================================================== */

    const getToken = () => localStorage.getItem(TOKEN_KEY);

    const authHeaders = () => ({
        "Content-Type": "application/json",
        "Authorization": `Bearer ${getToken()}`
    });

    const loadLocal = (key, fallback) => {
        const v = localStorage.getItem(key);
        return v ? JSON.parse(v) : fallback;
    };

    const saveLocal = (key, value) => {
        localStorage.setItem(key, JSON.stringify(value));
    };


    /* =========================================================
       FRONTEND SETTINGS KEYS
    ========================================================== */

    const LOCAL_KEYS = {
        theme: "themeMode",               // "light" | "dark"
        contrast: "highContrast",
        textSize: "textSize",
        notifications: "notificationsEnabled",
        emailAlerts: "emailAlerts",
        deviceLocation: "deviceLocation",
        deviceCamera: "deviceCamera",
        deviceMic: "deviceMic"
    };

    /* Backend keys (FastAPI model) */
    const BACKEND_KEYS = {
        email_notifications: "emailAlerts",
        preferred_theme: "themeMode",
        text_size: "textSize"
    };


    /* =========================================================
       STEP 1 — APPLY LOCAL SETTINGS IMMEDIATELY
    ========================================================== */

    const applyLocalSettingsInstantly = () => {
        const theme = loadLocal(LOCAL_KEYS.theme, "light");   // FIXED
        const contrast = loadLocal(LOCAL_KEYS.contrast, false);
        const textSize = loadLocal(LOCAL_KEYS.textSize, 100);

        // Apply theme
        document.documentElement.setAttribute("data-theme", theme);

        // Apply contrast
        document.documentElement.classList.toggle("high-contrast", contrast);

        // Apply text size
        document.documentElement.style.fontSize = `${textSize}%`;
    };

    applyLocalSettingsInstantly();


    /* =========================================================
       STEP 2 — FETCH BACKEND SETTINGS (if logged in)
    ========================================================== */

    const fetchBackendSettings = async () => {
        const token = getToken();
        if (!token) return null;

        try {
            const res = await fetch(API_URL, {
                method: "GET",
                headers: authHeaders(),
                credentials: "include"
            });

            if (!res.ok) return null;

            return await res.json();
        } catch (err) {
            console.error("Failed to fetch backend settings:", err);
            return null;
        }
    };


    /* =========================================================
       STEP 3 — MERGE BACKEND + LOCAL SETTINGS
    ========================================================== */

    const mergeSettings = (backend) => {
        if (!backend) return;

        Object.entries(BACKEND_KEYS).forEach(([backendKey, localKey]) => {
            const backendValue = backend[backendKey];

            if (backendValue !== null && backendValue !== undefined) {
                saveLocal(localKey, backendValue);
            }
        });
    };


    /* =========================================================
       STEP 4 — APPLY MERGED SETTINGS TO UI
    ========================================================== */
    const applyMergedSettingsToUI = () => {
        const themeToggle = document.getElementById("themeToggle");
        const contrastToggle = document.getElementById("contrastToggle");
        const textSizeRange = document.getElementById("textSizeRange");
        const notificationToggle = document.getElementById("notificationToggle");
        const emailToggle = document.getElementById("emailToggle");
        const locationToggle = document.getElementById("locationToggle");
        const cameraToggle = document.getElementById("cameraToggle");
        const micToggle = document.getElementById("micToggle");

        // Theme
        if (themeToggle)
            themeToggle.checked = loadLocal(LOCAL_KEYS.theme, "light") === "dark";

        // Contrast
        if (contrastToggle)
            contrastToggle.checked = loadLocal(LOCAL_KEYS.contrast, false);

        // Text size
        if (textSizeRange)
            textSizeRange.value = loadLocal(LOCAL_KEYS.textSize, 100);

        // Notifications
        if (notificationToggle)
            notificationToggle.checked = loadLocal(LOCAL_KEYS.notifications, false);

        // Email alerts
        if (emailToggle)
            emailToggle.checked = loadLocal(LOCAL_KEYS.emailAlerts, false);

        // Device permissions
        if (locationToggle)
            locationToggle.checked = loadLocal(LOCAL_KEYS.deviceLocation, false);

        if (cameraToggle)
            cameraToggle.checked = loadLocal(LOCAL_KEYS.deviceCamera, false);

        if (micToggle)
            micToggle.checked = loadLocal(LOCAL_KEYS.deviceMic, false);
    };



    /* =========================================================
       STEP 5 — PATCH SETTINGS TO BACKEND WHEN CHANGED
    ========================================================== */

    const patchBackendSettings = async () => {
        const token = getToken();
        if (!token) return;

        const payload = {
            email_notifications: loadLocal(LOCAL_KEYS.emailAlerts, false),
            preferred_theme: loadLocal(LOCAL_KEYS.theme, "light"),   // FIXED
            text_size: loadLocal(LOCAL_KEYS.textSize, 100)
        };

        try {
            await fetch(API_URL, {
                method: "PATCH",
                headers: authHeaders(),
                credentials: "include",
                body: JSON.stringify(payload)
            });
        } catch (err) {
            console.error("Failed to sync settings to backend:", err);
        }
    };


    /* =========================================================
       STEP 6 — WATCH FOR CHANGES & SYNC
    ========================================================== */

    const watchSetting = (id, localKey) => {
        const el = document.getElementById(id);
        if (!el) return;

        el.addEventListener("change", () => {
            const value =
                el.type === "checkbox"
                    ? (id === "themeToggle" ? (el.checked ? "dark" : "light") : el.checked)
                    : el.value;

            saveLocal(localKey, value);
            patchBackendSettings();
        });
    };

    // Watch all settings
    watchSetting("themeToggle", LOCAL_KEYS.theme);
    watchSetting("contrastToggle", LOCAL_KEYS.contrast);
    watchSetting("textSizeRange", LOCAL_KEYS.textSize);
    watchSetting("notificationToggle", LOCAL_KEYS.notifications);
    watchSetting("emailToggle", LOCAL_KEYS.emailAlerts);
    watchSetting("locationToggle", LOCAL_KEYS.deviceLocation);
    watchSetting("cameraToggle", LOCAL_KEYS.deviceCamera);
    watchSetting("micToggle", LOCAL_KEYS.deviceMic);


    /* =========================================================
       FULL SYNC PIPELINE
    ========================================================== */

    (async () => {
        const backend = await fetchBackendSettings();
        mergeSettings(backend);
        applyMergedSettingsToUI();
    })();

});