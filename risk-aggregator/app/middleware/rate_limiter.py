"""
Rate limiting middleware.
"""

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import setup_logging

logger = setup_logging()


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""

    def __init__(self, app):
        """
        Initialize rate limiter middleware.

        Args:
            app: FastAPI application
        """
        super().__init__(app)
        self.enabled = settings.RATE_LIMIT_ENABLED
        self.max_requests = settings.RATE_LIMIT_REQUESTS
        self.window_seconds = settings.RATE_LIMIT_WINDOW
        self.clients: Dict[str, Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response
        """
        if not self.enabled:
            return await call_next(request)

        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for client: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(self.window_seconds)},
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        count, window_start = self.clients.get(client_ip, (0, time.time()))
        remaining = max(0, self.max_requests - count)

        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(window_start + self.window_seconds)
        )

        return response

    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Check if client is within rate limit.

        Args:
            client_ip: Client IP address

        Returns:
            bool: True if within limit, False otherwise
        """
        current_time = time.time()

        # Get client's request count and window start time
        if client_ip in self.clients:
            count, window_start = self.clients[client_ip]

            # Check if window has expired
            if current_time - window_start >= self.window_seconds:
                # Reset window
                self.clients[client_ip] = (1, current_time)
                return True

            # Check if limit exceeded
            if count >= self.max_requests:
                return False

            # Increment count
            self.clients[client_ip] = (count + 1, window_start)
            return True
        else:
            # First request from this client
            self.clients[client_ip] = (1, current_time)
            return True

    def cleanup_expired_windows(self):
        """Clean up expired rate limit windows."""
        current_time = time.time()
        expired_clients = [
            client
            for client, (count, window_start) in self.clients.items()
            if current_time - window_start >= self.window_seconds
        ]

        for client in expired_clients:
            del self.clients[client]

        if expired_clients:
            logger.debug(f"Cleaned up {len(expired_clients)} expired rate limit windows")

