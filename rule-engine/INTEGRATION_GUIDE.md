# Rule Engine Integration Guide

## Overview

The Rule Engine evaluates transaction data and returns risk scores with violations. This guide explains how to integrate and interpret the results.

## API Endpoint

**POST** `/api/evaluate`

Evaluates transaction data against active fraud detection rules.

## Request Format

```json
{
  "dataType": "transactions",
  "facts": [
    {
      "entityId": "123",
      "amount": 1000.0,
      "accountBalance": 500.0,
      "type": "wire_transfer",
      "paymentMethod": "cryptocurrency"
    }
  ]
}
```

## Response Format

```json
{
  "entityId": "aggregated",
  "riskScore": 8.0,
  "violationsCount": 2,
  "violations": [
    {
      "code": "HIGH_AMOUNT",
      "weight": 5,
      "description": "Transaction exceeds balance"
    },
    {
      "code": "SUSPICIOUS_METHOD",
      "weight": 3,
      "description": "Cryptocurrency payment detected"
    }
  ],
  "metadata": {
    "totalFacts": 1,
    "totalRiskScore": 8.0,
    "averageRiskScore": 8.0,
    "normalizedRiskScore": 0.4,
    "totalViolations": 2,
    "individualResponses": 1
  }
}
```

## Understanding Risk Scores

### Score Types

1. **`riskScore`** - Cumulative violation score (0 to potentially unlimited)
2. **`normalizedRiskScore`** - Normalized to 0-1 scale (recommended for decisions)

### Normalized Risk Score (0-1 Scale)

| Value Range | Risk Level | Action |
|------------|------------|--------|
| **0.00** | No Risk | ✅ Auto-approve |
| **0.01 - 0.20** | Low Risk | ⚠️ Approve with log |
| **0.21 - 0.40** | Medium Risk | 🔍 Manual review |
| **0.41 - 0.60** | High Risk | 🚫 Hold for investigation |
| **0.61 - 0.80** | Critical | 🚨 Alert & block |
| **0.81 - 1.00** | Extreme | 🔒 Block immediately |

### Example Decisions

```javascript
// Integration example
const response = await evaluateTransaction(data);
const risk = response.metadata.normalizedRiskScore;

if (risk === 0) {
    // No risk - auto-approve
    approveTransaction();
} else if (risk <= 0.2) {
    // Low risk - approve with logging
    approveWithLog(transaction);
} else if (risk <= 0.4) {
    // Medium risk - queue for review
    queueForManualReview(transaction);
} else {
    // High risk - block transaction
    blockTransaction(transaction);
}
```

## How Scores Are Calculated

1. Rules trigger violations with assigned weights
2. Total score = sum of all violation weights
3. Normalized score = min(1.0, total_score / 20.0)

## Common Violation Codes

| Code | Weight | Description |
|------|--------|-------------|
| `UNUSUAL_TYPE` | 2 | Unusual transaction type detected |
| `SUSPICIOUS_METHOD` | 3 | Suspicious payment method |
| `HIGH_AMOUNT` | 5 | Transaction amount exceeds threshold |
| `HIGH_PAYMENT` | 5 | Payment exceeds account balance |

## Response Fields

- **`entityId`** - Identifier for the evaluated entity
- **`riskScore`** - Raw cumulative score
- **`normalizedRiskScore`** - Score normalized to 0-1 (use this for decisions)
- **`violationsCount`** - Number of violations detected
- **`violations`** - Array of violation details with codes and weights

## Quick Integration Checklist

1. ✅ Send POST request to `/api/evaluate` with your transaction data
2. ✅ Extract `normalizedRiskScore` from response metadata
3. ✅ Apply decision logic based on risk thresholds
4. ✅ Log transactions with high scores for auditing
5. ✅ Use violation codes for detailed reporting

## Support

For questions or issues, refer to the main system documentation or contact the development team.

