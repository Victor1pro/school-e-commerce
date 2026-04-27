"""
Request Timing Middleware
-------------------------
Measures how long each request takes to process and attaches the
duration to the response headers.

Adds:
    X-Process-Time: <duration_in_seconds>

Useful for:
    - Performance monitoring
    - Debugging slow endpoints
    - Profiling API behaviour during development
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import settings


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for measuring request processing time.

    Uses time.perf_counter() for high‑precision timing and optionally
    logs timing information in development mode.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Start high‑precision timer
        start = time.perf_counter()

        # Process request
        response = await call_next(request)

        # Compute duration
        duration = round(time.perf_counter() - start, 6)

        # Add timing header
        response.headers["X-Process-Time"] = str(duration)

        # Optional logging (development only)
        if settings.is_development():
            try:
                # Avoid leaking query params in logs
                path = request.url.path
                method = request.method

                print(f"[TIMING] {method} {path} → {duration}s")
            except Exception:
                # Logging must never break the request flow
                pass

        return response