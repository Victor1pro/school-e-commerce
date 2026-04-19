"""
Request Logging Middleware.

This middleware logs key information about each incoming HTTP request,
including:

- HTTP method (GET, POST, etc.)
- Request path
- Response status code
- Processing time in milliseconds
- Client IP address

Logging is automatically enabled only in development mode to avoid
performance overhead and leaking sensitive information in production.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import settings


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request/response details.

    Activated only when APP_ENVIRONMENT == "development".

    Purpose:
        - Provide visibility into request flow
        - Help debug performance issues
        - Track client activity during development

    This middleware never interrupts or breaks the request lifecycle.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Middleware entry point.

        Measures request processing time and logs relevant metadata.

        Args:
            request (Request): Incoming HTTP request.
            call_next: Function that forwards the request to the next handler.

        Returns:
            Response: The final response after processing.
        """

        # Start high-precision timer
        start_time = time.perf_counter()

        # Process request
        response = await call_next(request)

        # Calculate total processing time in milliseconds
        process_time = round((time.perf_counter() - start_time) * 1000, 2)

        # Extract client IP (fallback to "unknown")
        client_ip = request.client.host if request.client else "unknown"

        # Only log in development mode
        if settings.APP_ENVIRONMENT == "development":
            try:
                print(
                    f"[LOG] {request.method} {request.url.path} "
                    f"Status: {response.status_code} "
                    f"Time: {process_time}ms "
                    f"IP: {client_ip}"
                )
            except Exception:
                # Logging must never break the request flow
                pass

        return response