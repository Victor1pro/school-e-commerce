// ============================================================
//  API HELPER MODULE
//  - Centralized wrapper around fetch()
//  - Ensures consistent headers, error handling, and cookie use
//  - Used across the entire frontend (auth, cart, orders, etc.)
// ============================================================

/**
 * Base API helper for performing HTTP requests.
 *
 * This function abstracts:
 *  - HTTP method handling
 *  - JSON serialization
 *  - Cookie/session forwarding (guest_token, auth cookies)
 *  - Unified error handling for all API calls
 *
 * @param {string} url - Full API endpoint URL
 * @param {string} method - HTTP method (GET, POST, PATCH, DELETE)
 * @param {Object|null} body - Optional request payload
 * @returns {Promise<Object>} - Parsed JSON response from backend
 */
export async function api(url, method = "GET", body = null) {

    // ------------------------------------------------------------
    // REQUEST CONFIGURATION
    // - credentials: "include" ensures cookies are sent automatically
    //   (guest_token for cart, session cookies for auth)
    // - Content-Type ensures FastAPI receives JSON payloads
    // ------------------------------------------------------------
    const options = {
        method,
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        }
    };

    // Attach JSON body only when needed
    if (body) {
        options.body = JSON.stringify(body);
    }

    // ------------------------------------------------------------
    // EXECUTE REQUEST
    // - fetch() returns a Response object
    // - We wait for the server to respond before continuing
    // ------------------------------------------------------------
    const res = await fetch(url, options);

    // ------------------------------------------------------------
    // ERROR HANDLING
    // - If response is not OK (status 4xx or 5xx)
    // - Attempt to extract FastAPI's error JSON
    // - Throw clean, readable error message for UI
    // ------------------------------------------------------------
    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Request failed");
    }

    // ------------------------------------------------------------
    // SUCCESSFUL RESPONSE
    // - Parse JSON body and return it to the caller
    // ------------------------------------------------------------
    return res.json();
}