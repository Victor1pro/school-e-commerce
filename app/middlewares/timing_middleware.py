"""
Request Timing Middleware.

This middleware measures how long each request takes to process and
adds the duration to the response headers.

Key features:
- High‑precision timing using time.perf_counter()
- Adds `X-Process-Time` header to every response
- Optional console logging in development mode
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import settings


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for measuring request processing time.

    Adds a custom response header:
        X-Process-Time: <duration_in_seconds>

    Useful for:
        - Performance monitoring
        - Debugging slow endpoints
        - Profiling API behaviour during development
    """

    async def dispatch(self, request: Request, call_next):
        """
        Middleware entry point.

        Measures the time taken to process the request and attaches
        the duration to the response headers.

        Args:
            request (Request): Incoming HTTP request.
            call_next: Function that forwards the request to the next handler.

        Returns:
            Response: The final response with timing metadata.
        """

        # Start high‑precision timer
        start_time = time.perf_counter()

        # Process the request
        response = await call_next(request)

        # Compute duration
        duration = time.perf_counter() - start_time
        duration_rounded = round(duration, 6)

        # Add timing header to response
        response.headers["X-Process-Time"] = str(duration_rounded)

        # Optional logging in development mode
        if settings.APP_ENVIRONMENT == "development":
            try:
                print(
                    f"[TIMING] {request.method} {request.url.path} "
                    f"took {duration_rounded}s"
                )
            except Exception:
                # Logging must never break the request flow
                pass

        return response