"""
Security utilities and authentication.
"""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key authentication.

    Args:
        api_key: API key from request header

    Returns:
        str: Verified API key

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not settings.API_KEY:
        # If no API key is configured, allow all requests (development mode)
        return "development"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
            headers={"WWW-Authenticate": "APIKey"},
        )

    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "APIKey"},
        )

    return api_key


def hash_string(value: str) -> str:
    """
    Hash a string value for secure storage.

    Args:
        value: String to hash

    Returns:
        str: Hashed string
    """
    import hashlib

    return hashlib.sha256(value.encode()).hexdigest()


def generate_request_id() -> str:
    """
    Generate a unique request ID.

    Returns:
        str: Unique request ID
    """
    import uuid

    return str(uuid.uuid4())

