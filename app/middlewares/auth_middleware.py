"""
Authentication Middleware with Silent Refresh
---------------------------------------------
- Allows ALL static assets under /public (HTML, JS, CSS, images)
- Allows public pages & public API routes
- Protects private HTML pages (checkout, orders, account)
- Protects private API routes
- Validates JWT access tokens
- Performs silent refresh using refresh token
- Loads user into request.state.user
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.jwt_handler import (
    verify_access_token,
    verify_refresh_token,
    create_access_token
)

from app.database import get_db
from app.models.user_model import User


# ============================================================
# PUBLIC HTML PAGES (NO LOGIN REQUIRED)
# ============================================================
PUBLIC_HTML = [
    "/public/pages/login.html",
    "/public/pages/register.html",
    "/public/pages/shop.html",
    "/public/pages/product.html",
    "/public/pages/about.html",
    "/public/pages/contact.html",
    "/public/pages/cart.html",

    # Admin dashboard should load without login
    "/public/pages/admin/dashboard.html"
]


# ============================================================
# PROTECTED HTML PAGES (LOGIN REQUIRED)
# ============================================================
PROTECTED_HTML = [
    "/public/pages/checkout.html",
    "/public/pages/order-history.html",
    "/public/pages/order.html",
    "/public/pages/account.html",
    "/public/pages/settings.html",
]


# ============================================================
# PUBLIC API ROUTES
# ============================================================
PUBLIC_API = [
    "/auth/users/login",
    "/auth/users/register",
    "/auth/users/logout",

    "/search",
    "/search/suggest",

    "/products",
    "/categories",
    "/reviews",

    "/",
    "/home",
    "/about",
    "/contact",
    "/faq",
    "/terms",
    "/privacy",

    "/cart",
    "/cart/items",
    "/cart/clear",
    "/cart/merge",

    "/docs",
    "/openapi.json",
    "/redoc",
    "/health",
    "/ping",
]


# ============================================================
# PATH CHECKERS
# ============================================================
def is_public(path: str) -> bool:
    """Return True if path is public."""

    # Allow ALL static assets under /public (HTML, JS, CSS, images, uploads)
    if path.startswith("/public"):
        return True

    # Public HTML pages
    if path in PUBLIC_HTML:
        return True

    # Public API routes
    for p in PUBLIC_API:
        if path == p or path.startswith(p + "/"):
            return True

    return False



def is_protected_html(path: str) -> bool:
    """Return True if path is a protected HTML page."""
    return path in PROTECTED_HTML


# ============================================================
# TOKEN EXTRACTION
# ============================================================
def extract_token(request: Request) -> str | None:
    """Extract JWT from Authorization header or cookie."""
    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.lower().startswith("bearer "):
        return auth_header.split(" ")[1]

    return request.cookies.get("access_token")


# ============================================================
# AUTH MIDDLEWARE
# ============================================================
class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow all CORS preflight requests
        if request.method == "OPTIONS":
            return await call_next(request)

        # --------------------------------------------------------
        # 1. Allow all public routes (including ALL /public files)
        # --------------------------------------------------------
        if is_public(path):
            return await call_next(request)

        # --------------------------------------------------------
        # 2. Protected HTML pages require login
        # --------------------------------------------------------
        if is_protected_html(path):
            access_token = extract_token(request)
            refresh_token = request.cookies.get("refresh_token")

            # Validate access token
            payload = verify_access_token(access_token) if access_token else None

            if payload:
                user = self._load_user(payload.get("sub"))
                if user:
                    request.state.user = user
                    return await call_next(request)

            # Try silent refresh
            if refresh_token:
                refresh_payload = verify_refresh_token(refresh_token)
                if refresh_payload:
                    user_id = refresh_payload.get("sub")
                    new_access = create_access_token(user_id)
                    user = self._load_user(user_id)

                    if user:
                        request.state.user = user
                        response = await call_next(request)
                        response.set_cookie(
                            key="access_token",
                            value=new_access,
                            httponly=True,
                            secure=False,
                            samesite="lax",
                            max_age=60 * 15
                        )
                        return response

            # Not authenticated → return 401
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )

        # --------------------------------------------------------
        # 3. Protected API routes (anything not public)
        # --------------------------------------------------------
        access_token = extract_token(request)
        refresh_token = request.cookies.get("refresh_token")

        payload = verify_access_token(access_token) if access_token else None

        if payload:
            user = self._load_user(payload.get("sub"))
            if user:
                request.state.user = user
                return await call_next(request)

        # Silent refresh
        if refresh_token:
            refresh_payload = verify_refresh_token(refresh_token)
            if refresh_payload:
                user_id = refresh_payload.get("sub")
                new_access = create_access_token(user_id)
                user = self._load_user(user_id)

                if user:
                    request.state.user = user
                    response = await call_next(request)
                    response.set_cookie(
                        key="access_token",
                        value=new_access,
                        httponly=True,
                        secure=False,
                        samesite="lax",
                        max_age=60 * 15
                    )
                    return response

        # No valid authentication
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication required"}
        )

    # --------------------------------------------------------
    # Helper: Load user from DB
    # --------------------------------------------------------
    def _load_user(self, user_id: str) -> User | None:
        try:
            db_gen = get_db()
            db = next(db_gen)
            return db.query(User).filter(User.id == user_id).first()
        except Exception:
            return None
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass