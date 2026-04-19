"""
Global Error Handling Middleware.

This middleware provides a centralized mechanism for catching and
handling unhandled exceptions across the entire FastAPI application.

Key responsibilities:
- Intercept unexpected errors before they propagate
- Return consistent JSON error responses
- Show detailed debugging information only in development mode
- Prevent leaking sensitive stack traces in production
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import settings
import traceback


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for global exception handling.

    Behaves differently depending on environment:
        - Development: prints full traceback and returns detailed error info
        - Production: returns a safe, generic error message

    This ensures a clean API response format while still supporting
    debugging during development.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Middleware entry point.

        Wraps the request/response cycle in a try/except block to catch
        any unhandled exceptions raised by downstream routes, dependencies,
        or other middleware.

        Args:
            request (Request): Incoming HTTP request.
            call_next: Function that forwards the request to the next handler.

        Returns:
            JSONResponse: A structured error response.
        """
        try:
            # Attempt to process the request normally
            return await call_next(request)

        except Exception as e:
            # Determine environment mode
            is_dev = settings.APP_ENVIRONMENT == "development"

            # -------------------------
            # Development Mode
            # -------------------------
            if is_dev:
                print("ERROR:", e)
                traceback.print_exc()

                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "detail": "Internal server error",
                        "error": str(e),               # Raw error message
                        "path": request.url.path,      # Request path
                        "method": request.method,      # HTTP method
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