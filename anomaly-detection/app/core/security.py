"""
Security Utilities
Handles authentication, authorization, and security features
"""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import (APIKeyHeader, HTTPAuthorizationCredentials,
                              HTTPBearer)

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# API Key Security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Bearer Token Security
bearer_scheme = HTTPBearer(auto_error=False)


class SecurityManager:
    """Centralized security management"""

    def __init__(self):
        self.secret_key = settings.API_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60

    def verify_api_key(self, api_key: str) -> bool:
        """
        Verify API key using constant-time comparison

        Args:
            api_key: API key to verify

        Returns:
            bool: True if valid, False otherwise
        """
        if not settings.API_KEY_ENABLED:
            return True

        if not api_key:
            return False

        # Constant-time comparison to prevent timing attacks
        return secrets.compare_digest(api_key, settings.API_KEY)

    def hash_api_key(self, api_key: str) -> str:
        """
        Hash API key for storage

        Args:
            api_key: Plain API key

        Returns:
            str: Hashed API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()

    def generate_api_key(self, prefix: str = "sk") -> str:
        """
        Generate a new API key

        Args:
            prefix: Key prefix for identification

        Returns:
            str: New API key
        """
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time

        Returns:
            str: JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({"exp": expire, "iat": datetime.utcnow()})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> dict:
        """
        Verify and decode JWT token

        Args:
            token: JWT token

        Returns:
            dict: Decoded token data

        Raises:
            HTTPException: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        except jwt.JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    def create_signature(self, data: str) -> str:
        """
        Create HMAC signature for data

        Args:
            data: Data to sign

        Returns:
            str: HMAC signature
        """
        signature = hmac.new(
            self.secret_key.encode(), data.encode(), hashlib.sha256
        ).hexdigest()
        return signature

    def verify_signature(self, data: str, signature: str) -> bool:
        """
        Verify HMAC signature

        Args:
            data: Original data
            signature: Signature to verify

        Returns:
            bool: True if valid, False otherwise
        """
        expected_signature = self.create_signature(data)
        return secrets.compare_digest(signature, expected_signature)


# Initialize security manager
security_manager = SecurityManager()


# Dependency functions for FastAPI


async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Validate API key from header

    Args:
        api_key: API key from X-API-Key header

    Returns:
        str: Validated API key

    Raises:
        HTTPException: If API key is invalid
    """
    if not settings.API_KEY_ENABLED:
        return "disabled"

    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not security_manager.verify_api_key(api_key):
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )

    logger.info("API key validated successfully")
    return api_key


async def get_bearer_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> dict:
    """
    Validate bearer token

    Args:
        credentials: Bearer token credentials

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException: If token is invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return security_manager.verify_token(credentials.credentials)


async def get_optional_api_key(
    api_key: Optional[str] = Security(api_key_header),
) -> Optional[str]:
    """
    Optional API key validation (doesn't raise error if missing)

    Args:
        api_key: API key from header

    Returns:
        Optional[str]: API key if present and valid, None otherwise
    """
    if not settings.API_KEY_ENABLED:
        return None

    if not api_key:
        return None

    if security_manager.verify_api_key(api_key):
        return api_key

    return None


# Role-based access control


class RoleChecker:
    """Check user roles for authorization"""

    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, token_data: dict = Depends(get_bearer_token)):
        """
        Check if user has required role

        Args:
            token_data: Decoded token data

        Raises:
            HTTPException: If user doesn't have required role
        """
        user_role = token_data.get("role")

        if user_role not in self.allowed_roles:
            logger.warning(f"Access denied for role: {user_role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}",
            )

        return token_data


# Permission checkers


def require_admin_role():
    """Require admin role"""
    return RoleChecker(["admin"])


def require_analyst_role():
    """Require analyst or admin role"""
    return RoleChecker(["analyst", "admin"])


def require_viewer_role():
    """Require viewer, analyst, or admin role"""
    return RoleChecker(["viewer", "analyst", "admin"])


# Request signing utilities


class RequestSigner:
    """Sign and verify API requests"""

    @staticmethod
    def sign_request(method: str, path: str, body: str, timestamp: str) -> str:
        """
        Sign API request

        Args:
            method: HTTP method
            path: Request path
            body: Request body
            timestamp: Request timestamp

        Returns:
            str: Request signature
        """
        message = f"{method}{path}{body}{timestamp}"
        return security_manager.create_signature(message)

    @staticmethod
    def verify_request(
        method: str, path: str, body: str, timestamp: str, signature: str
    ) -> bool:
        """
        Verify API request signature

        Args:
            method: HTTP method
            path: Request path
            body: Request body
            timestamp: Request timestamp
            signature: Signature to verify

        Returns:
            bool: True if valid, False otherwise
        """
        # Check timestamp to prevent replay attacks (5 minute window)
        try:
            request_time = datetime.fromisoformat(timestamp)
            time_diff = abs((datetime.utcnow() - request_time).total_seconds())

            if time_diff > 300:  # 5 minutes
                logger.warning(f"Request timestamp too old: {time_diff}s")
                return False
        except ValueError:
            logger.warning(f"Invalid timestamp format: {timestamp}")
            return False

        # Verify signature
        message = f"{method}{path}{body}{timestamp}"
        return security_manager.verify_signature(message, signature)


# Data masking utilities


class DataMasker:
    """Mask sensitive data in responses"""

    @staticmethod
    def mask_phone(phone: str) -> str:
        """
        Mask phone number

        Args:
            phone: Phone number

        Returns:
            str: Masked phone number
        """
        if len(phone) <= 4:
            return "***"
        return f"***{phone[-4:]}"

    @staticmethod
    def mask_email(email: str) -> str:
        """
        Mask email address

        Args:
            email: Email address

        Returns:
            str: Masked email
        """
        if "@" not in email:
            return "***"

        local, domain = email.split("@", 1)
        masked_local = local[0] + "***" + local[-1] if len(local) > 2 else "***"
        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_account(account: str) -> str:
        """
        Mask account number

        Args:
            account: Account number

        Returns:
            str: Masked account number
        """
        if len(account) <= 4:
            return "***"
        return f"***{account[-4:]}"

    @staticmethod
    def mask_tin(tin: str) -> str:
        """
        Mask TIN number

        Args:
            tin: TIN number

        Returns:
            str: Masked TIN
        """
        if len(tin) <= 4:
            return "***"
        return f"{tin[:2]}***{tin[-2:]}"


# Input sanitization


class InputSanitizer:
    """Sanitize user inputs"""

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input

        Args:
            value: Input string
            max_length: Maximum allowed length

        Returns:
            str: Sanitized string
        """
        # Remove null bytes
        value = value.replace("\x00", "")

        # Trim whitespace
        value = value.strip()

        # Limit length
        if len(value) > max_length:
            value = value[:max_length]

        return value

    @staticmethod
    def sanitize_numeric(value: str) -> str:
        """
        Sanitize numeric input (remove non-numeric characters)

        Args:
            value: Input string

        Returns:
            str: Sanitized numeric string
        """
        return "".join(c for c in value if c.isdigit() or c in [".", "-"])

    @staticmethod
    def validate_customer_id(customer_id: str) -> bool:
        """
        Validate customer ID format

        Args:
            customer_id: Customer ID to validate

        Returns:
            bool: True if valid, False otherwise
        """
        # Must start with CUST_ and contain only alphanumeric and underscore
        if not customer_id.startswith("CUST_"):
            return False

        if len(customer_id) > 50:
            return False

        allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
        return all(c in allowed_chars for c in customer_id)


# Security headers middleware helper


def get_security_headers() -> dict:
    """
    Get recommended security headers

    Returns:
        dict: Security headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        # Allow Swagger UI CDN resources while keeping security reasonable
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://cdn.jsdelivr.net; "
            "font-src 'self' https://cdn.jsdelivr.net"
        ),
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }


# Audit logging


class AuditLogger:
    """Log security-related events"""

    @staticmethod
    def log_authentication(user_id: str, success: bool, ip_address: str):
        """Log authentication attempt"""
        status = "SUCCESS" if success else "FAILED"
        logger.info(
            f"Authentication {status}",
            extra={
                "event": "authentication",
                "user_id": user_id,
                "success": success,
                "ip_address": ip_address,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @staticmethod
    def log_authorization(user_id: str, resource: str, action: str, granted: bool):
        """Log authorization check"""
        status = "GRANTED" if granted else "DENIED"
        logger.info(
            f"Authorization {status}",
            extra={
                "event": "authorization",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "granted": granted,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @staticmethod
    def log_anomaly_detection(
        customer_id: str,
        model_type: str,
        is_anomaly: bool,
        risk_level: str,
        score: float,
    ):
        """Log anomaly detection result"""
        logger.info(
            f"Anomaly detection: {risk_level}",
            extra={
                "event": "anomaly_detection",
                "customer_id": customer_id,
                "model_type": model_type,
                "is_anomaly": is_anomaly,
                "risk_level": risk_level,
                "score": score,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @staticmethod
    def log_data_access(user_id: str, resource: str, action: str):
        """Log data access"""
        logger.info(
            f"Data access: {resource}",
            extra={
                "event": "data_access",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


# Export commonly used items
__all__ = [
    "security_manager",
    "get_api_key",
    "get_bearer_token",
    "get_optional_api_key",
    "require_admin_role",
    "require_analyst_role",
    "require_viewer_role",
    "RequestSigner",
    "DataMasker",
    "InputSanitizer",
    "get_security_headers",
    "AuditLogger",
]
