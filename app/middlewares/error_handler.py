"""
Global Error Handling Middleware
--------------------------------
Provides centralized handling of unexpected exceptions across the app.

Features:
- Catches unhandled exceptions
- Returns consistent JSON error responses
- Shows detailed debugging info only in development mode
- Prevents leaking stack traces in production
"""

import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi.exceptions import HTTPException
from app.config.settings import settings


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for global exception handling.

    Behaviour:
        - Development: prints full traceback + returns detailed error info
        - Production: returns safe, generic error message
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            # Let the request proceed normally
            return await call_next(request)

        except HTTPException:
            # Allow FastAPI to handle its own HTTPExceptions
            raise

        except Exception as exc:
            # Determine environment
            is_dev = settings.is_development()

            # -------------------------
            # Development Mode
            # -------------------------
            if is_dev:
                print("\n[ERROR] Unhandled exception occurred:")
                traceback.print_exc()

                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "detail": "Internal server error",
                        "error": str(exc),
                        "path": request.url.path,
                        "method": request.method,
                    }
                )

            # -------------------------
            # Production Mode
            # -------------------------
            # Do NOT expose internal details
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )