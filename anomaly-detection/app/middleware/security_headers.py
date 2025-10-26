"""
Security Headers Middleware
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import get_security_headers


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        headers = get_security_headers()
        for key, value in headers.items():
            response.headers[key] = value
        return response
