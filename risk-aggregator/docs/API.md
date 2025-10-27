# Risk Aggregator API Documentation

## Overview

The Risk Aggregator API provides endpoints for aggregating risk signals from multiple sources and computing comprehensive risk assessments.

## Base URL

```
http://localhost:8003/api/v1
```

## Authentication

API key authentication (optional):
```
X-API-Key: your-api-key
```

## Common Response Format

### Success Response
```json
{
  "entity_id": "string",
  "overall_risk_score": 0.75,
  "risk_level": "high",
  "confidence": 0.85,
  ...
}
```

### Error Response
```json
{
  "error": {
    "status_code": 400,
    "message": "Error message",
    "details": {},
    "path": "/api/v1/risk/assess"
  }
}
```

## Endpoints

### Health Checks

#### GET /health
Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "service": "risk-aggregator",
  "version": "1.0.0",
  "environment": "development"
}
```

#### GET /api/v1/health/ready
Readiness probe for Kubernetes.

#### GET /api/v1/health/live
Liveness probe for Kubernetes.

---

### Risk Assessment

#### POST /api/v1/risk/assess
Assess risk for an entity with provided signals.

**Request Body:**
```json
{
  "entity_id": "customer-123",
  "entity_type": "customer",
  "signals": [
    {
      "category": "kyc",
      "score": 0.7,
      "confidence": 0.9,
      "source": "kyc-service",
      "details": {
        "verification_status": "pending"
      }
    },
    {
      "category": "transaction",
      "score": 0.5,
      "confidence": 0.8,
      "source": "transaction-service"
    }
  ],
  "weights": {
    "kyc": 0.3,
    "transaction": 0.7
  }
}
```

**Response:**
```json
{
  "entity_id": "customer-123",
  "entity_type": "customer",
  "overall_risk_score": 0.58,
  "risk_level": "medium",
  "components": [
    {
      "category": "kyc",
      "score": 0.7,
      "weight": 0.3,
      "weighted_score": 0.21,
      "confidence": 0.9,
      "source": "kyc-service",
      "details": {...}
    }
  ],
  "confidence": 0.86,
  "assessed_at": "2025-01-25T12:00:00Z",
  "metadata": null
}
```

#### POST /api/v1/risk/customer
Comprehensive customer risk assessment.

**Request Body:**
```json
{
  "customer_id": "customer-123",
  "include_kyc": true,
  "include_transactions": true,
  "include_credit": true,
  "include_loans": true,
  "include_repayments": true,
  "time_window_days": 90,
  "force_refresh": false
}
```

**Response:**
```json
{
  "customer_id": "customer-123",
  "overall_risk_score": 0.65,
  "risk_level": "medium",
  "risk_profile": {
    "kyc_risk": {...},
    "transaction_risk": {...},
    "credit_risk": {...},
    "loan_risk": {...},
    "repayment_risk": {...}
  },
  "total_signals": 5,
  "confidence": 0.82,
  "assessed_at": "2025-01-25T12:00:00Z",
  "cached": false,
  "recommendations": [
    "Review and update KYC documentation",
    "Monitor transaction patterns closely"
  ],
  "alerts": [
    {
      "severity": "high",
      "category": "transaction",
      "message": "High risk detected in transaction",
      "score": 0.85,
      "timestamp": "2025-01-25T12:00:00Z"
    }
  ]
}
```

#### GET /api/v1/risk/customer/{customer_id}
Get cached customer risk assessment.

**Response:** Same as POST /api/v1/risk/customer

#### GET /api/v1/risk/score/{entity_id}
Get quick risk score for an entity.

**Response:**
```json
{
  "entity_id": "customer-123",
  "risk_score": 0.65,
  "risk_level": "medium"
}
```

---

### Batch Aggregation

#### POST /api/v1/aggregate/batch
Process batch risk aggregation.

**Request Body:**
```json
{
  "entities": [
    {
      "entity_id": "customer-1",
      "entity_type": "customer",
      "signals": [...]
    },
    {
      "entity_id": "customer-2",
      "entity_type": "customer",
      "signals": [...]
    }
  ],
  "weights": {
    "kyc": 0.25,
    "transaction": 0.3
  },
  "parallel": true
}
```

**Response:**
```json
{
  "total_entities": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "entity_id": "customer-1",
      "entity_type": "customer",
      "risk_score": 0.65,
      "risk_level": "medium",
      "success": true,
      "error": null
    }
  ],
  "average_risk_score": 0.65,
  "processing_time_seconds": 1.25,
  "processed_at": "2025-01-25T12:00:00Z"
}
```

#### POST /api/v1/aggregate/job
Create background aggregation job.

**Request Body:**
```json
{
  "job_name": "Daily Risk Assessment",
  "entity_ids": ["customer-1", "customer-2", "customer-3"],
  "entity_type": "customer",
  "include_sources": ["kyc", "transaction", "credit"],
  "weights": {...},
  "notification_webhook": "https://example.com/webhook"
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_name": "Daily Risk Assessment",
  "status": "pending",
  "total_entities": 3,
  "processed_entities": 0,
  "successful": 0,
  "failed": 0,
  "progress_percentage": 0.0,
  "created_at": "2025-01-25T12:00:00Z",
  "started_at": null,
  "completed_at": null,
  "results_url": null,
  "error": null
}
```

#### GET /api/v1/aggregate/job/{job_id}
Get job status and results.

**Response:** Same as POST /api/v1/aggregate/job

#### POST /api/v1/aggregate/weights
Update risk weight configuration.

**Request Body:**
```json
{
  "kyc": 0.3,
  "transaction": 0.3,
  "credit": 0.2,
  "loan": 0.1,
  "repayment": 0.1
}
```

**Response:**
```json
{
  "message": "Risk weights updated successfully",
  "weights": {
    "kyc": 0.3,
    "transaction": 0.3,
    "credit": 0.2,
    "loan": 0.1,
    "repayment": 0.1
  }
}
```

#### GET /api/v1/aggregate/weights
Get current risk weight configuration.

**Response:**
```json
{
  "weights": {
    "kyc": 0.25,
    "transaction": 0.3,
    "credit": 0.2,
    "loan": 0.15,
    "repayment": 0.1
  }
}
```

---

## Risk Categories

- `kyc` - Know Your Customer verification
- `transaction` - Transaction patterns and anomalies
- `credit` - Credit history and score
- `loan` - Loan status and behavior
- `repayment` - Repayment history and compliance
- `behavioral` - User behavioral patterns
- `external` - External risk factors

## Risk Levels

- `low` - Score: 0.0 - 0.25
- `medium` - Score: 0.25 - 0.50
- `high` - Score: 0.50 - 0.75
- `critical` - Score: 0.75 - 1.0

## Rate Limits

Default rate limits:
- 100 requests per minute per IP address
- Headers include rate limit information:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Error Codes

- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

