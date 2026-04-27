"""
Request Logging Middleware
--------------------------
Logs key information about each incoming HTTP request:

- HTTP method
- Request path
- Response status code
- Processing time (ms)
- Client IP address

Logging is enabled only in development mode to avoid leaking
sensitive information or adding overhead in production.
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import settings


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request/response details.

    Activated only when running in development mode.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Start timer
        start = time.perf_counter()

        # Process request
        response = await call_next(request)

        # Compute duration in ms
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        # Extract client IP
        client_ip = request.client.host if request.client else "unknown"

        # Log only in development mode
        if settings.is_development():
            try:
                method = request.method
                path = request.url.path  # Avoid logging query params
                status = response.status_code

                print(
                    f"[REQUEST] {method} {path} "
                    f"→ Status {status} | {duration_ms}ms | IP: {client_ip}"
                )
            except Exception:
                # Logging must never break the request flow
                pass

        return response