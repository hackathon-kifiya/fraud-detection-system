# Security Features Documentation

This document describes the security features implemented in the Anomaly Detection API using the `security.py` module.

## Table of Contents

1. [Overview](#overview)
2. [API Key Authentication](#api-key-authentication)
3. [Security Headers](#security-headers)
4. [Audit Logging](#audit-logging)
5. [Input Sanitization & Validation](#input-sanitization--validation)
6. [Data Masking](#data-masking)
7. [Additional Security Features](#additional-security-features)
8. [Usage Examples](#usage-examples)

---

## Overview

The security framework provides comprehensive protection through multiple layers:

- **Authentication**: API key-based authentication for all endpoints
- **Authorization**: Role-based access control (RBAC) support
- **Audit Logging**: Comprehensive logging of security events
- **Input Validation**: Sanitization and validation of user inputs
- **Data Masking**: Protection of sensitive information in responses
- **Security Headers**: Standard HTTP security headers
- **Request Signing**: HMAC-based request signature verification

---

## API Key Authentication

### Configuration

API key authentication is configured through environment variables:

```bash
API_KEY_ENABLED=true
API_KEY=your-secret-api-key-here
```

### Implementation

All protected endpoints require the `X-API-Key` header:

```python
from app.core.security import get_api_key

@router.post("/check")
async def check_transaction(
    data: TransactionData,
    api_key: str = Depends(get_api_key)
):
    # Endpoint logic here
    pass
```

### Usage

```bash
curl -X POST "http://localhost:8000/api/v1/transaction/check" \
  -H "X-API-Key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST_123",
    "transaction_id": "TXN_001",
    "amount": 1000.00
  }'
```

### Key Management

Generate a new API key programmatically:

```python
from app.core.security import security_manager

# Generate new API key
new_key = security_manager.generate_api_key(prefix="sk")
print(f"New API Key: {new_key}")

# Hash API key for storage
hashed = security_manager.hash_api_key(new_key)
```

---

## Security Headers

### Implemented Headers

The application automatically adds the following security headers to all responses:

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME type sniffing |
| `X-Frame-Options` | `DENY` | Prevents clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Enables XSS filtering |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Enforces HTTPS |
| `Content-Security-Policy` | `default-src 'self'` | Restricts resource loading |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Controls referrer information |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=()` | Restricts browser features |

### Implementation

Headers are automatically added via middleware:

```python
from app.core.security import get_security_headers

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        headers = get_security_headers()
        for key, value in headers.items():
            response.headers[key] = value
        return response
```

---

## Audit Logging

### Overview

All security-relevant events are logged for compliance and forensics:

- Authentication attempts
- Authorization decisions
- Anomaly detection results
- Data access events

### Types of Audit Logs

#### 1. Authentication Logging

```python
from app.core.security import AuditLogger

AuditLogger.log_authentication(
    user_id="user_123",
    success=True,
    ip_address="192.168.1.1"
)
```

#### 2. Authorization Logging

```python
AuditLogger.log_authorization(
    user_id="user_123",
    resource="kyc_data",
    action="read",
    granted=True
)
```

#### 3. Anomaly Detection Logging

```python
AuditLogger.log_anomaly_detection(
    customer_id="CUST_123",
    model_type="transaction",
    is_anomaly=True,
    risk_level="HIGH",
    score=0.95
)
```

#### 4. Data Access Logging

```python
AuditLogger.log_data_access(
    user_id="user_123",
    resource="kyc_data/CUST_123",
    action="view"
)
```

### Log Format

All audit logs include:

```json
{
  "event": "anomaly_detection",
  "customer_id": "CUST_123",
  "model_type": "transaction",
  "is_anomaly": true,
  "risk_level": "HIGH",
  "score": 0.95,
  "timestamp": "2025-10-25T12:34:56.789Z"
}
```

---

## Input Sanitization & Validation

### String Sanitization

Removes dangerous characters and limits length:

```python
from app.core.security import InputSanitizer

# Sanitize string input
clean_string = InputSanitizer.sanitize_string(
    user_input,
    max_length=1000
)
```

### Numeric Sanitization

Extracts only valid numeric characters:

```python
# Sanitize numeric input
clean_number = InputSanitizer.sanitize_numeric(user_input)
```

### Customer ID Validation

Enforces strict format requirements:

```python
# Validate customer ID format
is_valid = InputSanitizer.validate_customer_id("CUST_12345")
# Returns: True

# Invalid formats
InputSanitizer.validate_customer_id("invalid")  # False
InputSanitizer.validate_customer_id("cust_123")  # False (lowercase)
```

**Requirements:**
- Must start with `CUST_`
- Maximum 50 characters
- Only uppercase letters, numbers, and underscores

### Endpoint Implementation

```python
@router.post("/check")
async def check_transaction(data: TransactionData):
    # Validate customer ID format
    if not InputSanitizer.validate_customer_id(data.customer_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid customer_id format"
        )
    # Process request...
```

---

## Data Masking

### Overview

Protects sensitive information in API responses by masking PII (Personally Identifiable Information).

### Supported Masking Types

#### 1. Phone Number Masking

```python
from app.core.security import DataMasker

# Mask phone number
masked = DataMasker.mask_phone("1234567890")
# Returns: "***7890"
```

#### 2. Email Masking

```python
# Mask email address
masked = DataMasker.mask_email("john.doe@example.com")
# Returns: "j***e@example.com"
```

#### 3. Account Number Masking

```python
# Mask account number
masked = DataMasker.mask_account("1234567890123456")
# Returns: "***3456"
```

#### 4. TIN (Tax ID) Masking

```python
# Mask TIN number
masked = DataMasker.mask_tin("123456789")
# Returns: "12***89"
```

### KYC Service Integration

The `KYCService` provides comprehensive data masking:

```python
from app.services.kyc_service import KYCService

kyc_service = KYCService()

# Mask customer data
kyc_data = {
    "customer_id": "CUST_123",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "1234567890",
    "account_number": "9876543210",
    "tin_number": "123456789"
}

# Partial masking (default)
masked_data = kyc_service.mask_kyc_data(kyc_data, mask_level="partial")
```

### Masking Levels

1. **none**: No masking applied
2. **partial**: Masks sensitive fields (phone, email, account, TIN)
3. **full**: Masks all PII including address and date of birth

### API Endpoint Example

The `/kyc/check-with-masking` endpoint demonstrates data masking:

```bash
curl -X POST "http://localhost:8000/api/v1/kyc/check-with-masking?mask_level=partial" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST_123",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "1234567890"
  }'
```

**Response:**

```json
{
  "anomaly_result": {
    "is_anomaly": false,
    "anomaly_score": 0.23,
    "risk_level": "LOW",
    "explanation": {...}
  },
  "masked_customer_data": {
    "customer_id": "CUST_123",
    "first_name": "John",
    "last_name": "Doe",
    "email": "j***e@example.com",
    "phone_number": "***7890"
  },
  "masking_applied": "partial",
  "security_note": "Sensitive fields have been masked according to the specified mask level"
}
```

---

## Additional Security Features

### JWT Token Support

For more advanced authentication scenarios:

```python
from app.core.security import security_manager
from datetime import timedelta

# Create access token
token = security_manager.create_access_token(
    data={"user_id": "user_123", "role": "analyst"},
    expires_delta=timedelta(hours=1)
)

# Verify token
payload = security_manager.verify_token(token)
```

### Role-Based Access Control (RBAC)

```python
from app.core.security import require_admin_role, require_analyst_role

@router.post("/admin/settings")
async def update_settings(
    token_data: dict = Depends(require_admin_role())
):
    # Only admins can access this endpoint
    pass

@router.get("/analytics/report")
async def get_report(
    token_data: dict = Depends(require_analyst_role())
):
    # Analysts and admins can access this endpoint
    pass
```

### Request Signing

For high-security scenarios:

```python
from app.core.security import RequestSigner
from datetime import datetime

# Sign request
signature = RequestSigner.sign_request(
    method="POST",
    path="/api/v1/transaction/check",
    body='{"customer_id": "CUST_123"}',
    timestamp=datetime.utcnow().isoformat()
)

# Verify request
is_valid = RequestSigner.verify_request(
    method="POST",
    path="/api/v1/transaction/check",
    body='{"customer_id": "CUST_123"}',
    timestamp=timestamp,
    signature=signature
)
```

---

## Usage Examples

### Complete Transaction Check with Security

```python
import requests

# API configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Transaction data
transaction_data = {
    "customer_id": "CUST_123456",
    "transaction_id": "TXN_001",
    "amount": 1500.00,
    "transaction_type": "purchase",
    "merchant_category": "RETAIL"
}

# Make request
response = requests.post(
    f"{API_BASE_URL}/api/v1/transaction/check",
    headers=headers,
    json=transaction_data
)

if response.status_code == 200:
    result = response.json()
    print(f"Is Anomaly: {result['is_anomaly']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Score: {result['anomaly_score']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### KYC Check with Data Masking

```python
import requests

API_BASE_URL = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# KYC data
kyc_data = {
    "customer_id": "CUST_123456",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "1234567890",
    "date_of_birth": "1990-01-15",
    "account_number": "9876543210",
    "tin_number": "123456789"
}

# Request with partial masking
response = requests.post(
    f"{API_BASE_URL}/api/v1/kyc/check-with-masking?mask_level=partial",
    headers=headers,
    json=kyc_data
)

result = response.json()
print("Masked Data:")
print(result["masked_customer_data"])
```

---

## Best Practices

### 1. API Key Management

- **Never commit API keys to version control**
- Use environment variables or secrets management systems
- Rotate keys regularly
- Use different keys for different environments

### 2. Logging

- Monitor audit logs regularly
- Set up alerts for suspicious activity
- Retain logs according to compliance requirements
- Use log aggregation tools (ELK, Splunk, etc.)

### 3. Data Masking

- Always mask PII in logs and responses
- Use appropriate masking levels based on user permissions
- Consider data residency requirements
- Implement field-level access control

### 4. Input Validation

- Validate all user inputs
- Use allowlists over denylists
- Sanitize data before processing
- Return generic error messages to prevent information disclosure

### 5. Security Headers

- Keep headers updated with current best practices
- Test with security scanning tools
- Consider CSP (Content Security Policy) for web interfaces
- Use HTTPS in production

---

## Configuration

### Environment Variables

```bash
# Security Configuration
API_KEY_ENABLED=true
API_KEY=your-secret-api-key-here

# JWT Configuration (optional)
JWT_SECRET_KEY=your-jwt-secret-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Logging
LOG_LEVEL=INFO
```

### Security Settings

Located in `app/core/config.py`:

```python
class Settings(BaseSettings):
    API_KEY_ENABLED: bool = True
    API_KEY: str
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
```

---

## Testing Security Features

### Test API Key Authentication

```bash
# Without API key (should fail)
curl -X GET "http://localhost:8000/api/v1/transaction/stats"

# With valid API key (should succeed)
curl -X GET "http://localhost:8000/api/v1/transaction/stats" \
  -H "X-API-Key: your-api-key"
```

### Test Input Validation

```bash
# Invalid customer ID format (should fail)
curl -X POST "http://localhost:8000/api/v1/transaction/check" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "invalid_format"}'
```

### Test Data Masking

```bash
# Compare different masking levels
curl -X POST "http://localhost:8000/api/v1/kyc/check-with-masking?mask_level=none" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d @kyc_data.json

curl -X POST "http://localhost:8000/api/v1/kyc/check-with-masking?mask_level=full" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d @kyc_data.json
```

---

## Troubleshooting

### Common Issues

#### 1. 401 Unauthorized

**Problem**: Missing or invalid API key

**Solution**:
- Ensure `X-API-Key` header is included
- Verify API key matches the configured value
- Check if `API_KEY_ENABLED=true`

#### 2. 400 Bad Request (Invalid customer_id format)

**Problem**: Customer ID doesn't match required format

**Solution**:
- Ensure customer ID starts with `CUST_`
- Use only uppercase letters, numbers, and underscores
- Keep length under 50 characters

#### 3. Security Headers Not Applied

**Problem**: Response missing security headers

**Solution**:
- Verify `SecurityHeadersMiddleware` is registered
- Check middleware order in `main.py`
- Ensure middleware is properly configured

---

## Security Checklist

- [ ] API key authentication enabled
- [ ] Secure API key storage (not in code)
- [ ] Security headers middleware active
- [ ] Audit logging configured
- [ ] Input validation on all endpoints
- [ ] Data masking for sensitive responses
- [ ] HTTPS enabled in production
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Regular security audits scheduled

---

## Support

For questions or issues:

- Review API documentation: `/docs`
- Check audit logs for security events
- Contact security team for sensitive issues

---

**Last Updated**: October 25, 2025  
**Version**: 1.0.0




