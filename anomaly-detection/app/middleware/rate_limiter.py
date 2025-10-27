"""
Rate Limiter Middleware
"""
import time
from collections import defaultdict

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter
    For production, use Redis-based rate limiting
    """

    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""

        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Skip rate limiting for health check and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get client identifier (IP address)
        client_ip = request.client.host

        # Current time
        current_time = time.time()

        # Clean old requests
        window_start = current_time - settings.RATE_LIMIT_WINDOW
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip] if req_time > window_start
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= settings.RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": (
                        f"Maximum {settings.RATE_LIMIT_REQUESTS} requests per "
                        f"{settings.RATE_LIMIT_WINDOW} seconds"
                    ),
                },
            )

        # Add current request
        self.requests[client_ip].append(current_time)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(
            settings.RATE_LIMIT_REQUESTS - len(self.requests[client_ip])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(current_time + settings.RATE_LIMIT_WINDOW)
        )

        return response
