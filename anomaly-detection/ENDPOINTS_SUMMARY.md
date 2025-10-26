# Anomaly Detection API - Finalized Endpoints Summary

## Overview
This document describes all finalized endpoints for the Anomaly Detection API. The API provides three main detection models:

1. **KYC Model** - Customer Know Your Customer verification
2. **Transaction Model** - Individual transaction anomaly detection
3. **Merged Model** - Combined KYC + Business data analysis

---

## Transaction Endpoints (`/api/v1/transaction/`)

### 1. Single Transaction Check
**Endpoint:** `POST /api/v1/transaction/check`

**Purpose:** Check a single transaction for anomalies

**Request Body:**
```json
{
  "customer_id": "CUST_12345",
  "date": "2024-10-25T14:30:00",
  "credit": 1000.0,
  "debit": 0.0,
  "closingBalance": 5000.0,
  "narrative": "Cash Deposit BY SELF",
  "source": "CASH DEPOSIT",
  "is_anomaly": 0
}
```

**Response:**
```json
{
  "is_anomaly": false,
  "anomaly_score": 0.85,
  "risk_level": "LOW",
  "explanation": {
    "top_contributing_features": {...},
    "feature_values": {...},
    "shap_values": {...}
  },
  "timestamp": "2024-10-26T10:00:00"
}
```

**Features:**
- Input validation for customer ID format
- SHAP explainability with feature contributions
- Risk level classification (LOW, MEDIUM, HIGH)
- Audit logging of all detections

---

### 2. Batch Transaction Check
**Endpoint:** `POST /api/v1/transaction/batch`

**Purpose:** Process multiple transactions from different customers at once

**Request Body:**
```json
{
  "transactions": [
    {
      "customer_id": "CUST_12345",
      "date": "2024-10-25T14:30:00",
      "credit": 1000.0,
      "debit": 0.0,
      "closingBalance": 5000.0,
      "narrative": "Cash Deposit BY SELF",
      "source": "CASH DEPOSIT"
    },
    {...}
  ]
}
```

**Response:**
```json
{
  "batch_results": [
    {
      "customer_id": "CUST_12345",
      "result": {...},
      "error": null
    }
  ],
  "total_processed": 50,
  "total_anomalies": 3,
  "processing_time_seconds": 2.34
}
```

**Features:**
- Batch processing up to 100 transactions
- Per-record error handling and logging
- Aggregated statistics
- Performance metrics

---

### 3. Customer Batch Transaction Analysis
**Endpoint:** `POST /api/v1/transaction/customer/batch`

**Purpose:** Process all transactions for a specific customer and generate customer-level risk assessment

**Request Body:**
```json
{
  "customer_id": "CUST_12345",
  "transactions": [
    {
      "customer_id": "CUST_12345",
      "date": "2024-10-25T14:30:00",
      "credit": 1000.0,
      "debit": 0.0,
      "closingBalance": 5000.0,
      "narrative": "Cash Deposit BY SELF",
      "source": "CASH DEPOSIT"
    },
    {...}
  ]
}
```

**Response:**
```json
{
  "customer_id": "CUST_12345",
  "total_transactions": 100,
  "anomaly_count": 5,
  "customer_risk_level": "MEDIUM",
  "customer_anomaly_score": 0.42,
  "customer_flagged": false,
  "transaction_results": [...],
  "processing_time_seconds": 1.23
}
```

**Features:**
- Aggregated customer-level anomaly scoring
- Transaction-level anomaly detection
- Customer flagging based on:
  - Anomaly ratio > 30% of transactions, OR
  - > 20% of transactions are high risk, OR
  - Customer risk level is HIGH
- Per-transaction explainability

---

### 4. Transaction Model Statistics
**Endpoint:** `GET /api/v1/transaction/stats`

**Purpose:** Get model statistics and feature information

**Response:**
```json
{
  "model_type": "Isolation Forest",
  "features": [
    "amount",
    "transaction_type",
    "hour_of_day",
    "day_of_week",
    "distance_from_home",
    "is_online",
    "num_transactions_last_24h",
    "avg_amount_last_30d"
  ],
  "num_features": 8,
  "contamination": 0.02,
  "n_estimators": 150
}
```

---

## Merged Model Endpoints (`/api/v1/merged/`)

### 1. Single Merged Check
**Endpoint:** `POST /api/v1/merged/check`

**Purpose:** Check combined KYC + Business data for anomalies

**Request Body:**
```json
{
  "customer_id": "CUST_12345",
  "customer_name": "John Doe",
  "customer_phone_number": 9123456789,
  "customer_age": 35,
  "customer_gender": "male",
  "customer_marital_status": "single",
  "customer_education_level": "primary",
  "customer_tin_number": "1234567890",
  "customer_bank_account_number": "1234567890",
  "customer_region": "ADDIS_ABABA",
  "customer_city": "ADDIS_ABABA",
  "customer_zone_or_sub_city": "ZONE_1",
  "customer_woreda": 1,
  "customerId": "CUST_12345",
  "business_id": "BUS_12345",
  "business_name": "John's Business",
  "business_tin_number": "9876543210",
  "business_city": "ADDIS_ABABA",
  "business_zone_or_sub_city": "ZONE_1",
  "business_woreda": "01",
  "business_establishment_year": 2020,
  "business_sector": "AGRICULTURE",
  "business_level": "GROWING",
  "business_starting_capital": 100000.0,
  "business_current_capital": 150000.0,
  "business_annual_profit": 25000.0,
  "business_annual_sales": 200000.0,
  "business_current_no_of_employees": 5,
  "business_starting_no_of_employees": 2,
  "business_source_of_initial_capital": "FAMILY",
  "business_association_type": "SOLE_PROPRIETORSHIP"
}
```

**Response:**
```json
{
  "is_anomaly": false,
  "anomaly_score": 0.78,
  "risk_level": "LOW",
  "explanation": {...},
  "timestamp": "2024-10-26T10:00:00"
}
```

**Features:**
- Comprehensive KYC + Business analysis
- 23 combined features analyzed
- SHAP explainability for each feature
- Risk assessment based on merged profile

---

### 2. Batch Merged Check
**Endpoint:** `POST /api/v1/merged/batch`

**Purpose:** Process multiple merged records at once

**Request Body:**
```json
{
  "records": [
    {
      "customer_id": "CUST_12345",
      "customer_name": "John Doe",
      ...
      "business_association_type": "SOLE_PROPRIETORSHIP"
    },
    {...}
  ]
}
```

**Response:**
```json
{
  "batch_results": [
    {
      "customer_id": "CUST_12345",
      "business_id": "BUS_12345",
      "result": {...},
      "error": null
    }
  ],
  "total_processed": 50,
  "total_anomalies": 2,
  "processing_time_seconds": 3.45
}
```

**Features:**
- Batch processing up to 100 merged records
- Per-record error handling
- Paired customer-business linkage tracking
- Performance metrics

---

### 3. Merged Model Statistics
**Endpoint:** `GET /api/v1/merged/stats`

**Purpose:** Get merged model statistics

**Response:**
```json
{
  "model_type": "Isolation Forest (Merged KYC+Business)",
  "features": [
    "customer_age",
    "customer_gender_encoded",
    "customer_marital_status_encoded",
    "customer_education_level_encoded",
    "customer_region_encoded",
    "customer_city_encoded",
    "customer_zone_encoded",
    "customer_woreda_numeric",
    "customer_phone_last_4",
    "customer_tin_length",
    "customer_account_length",
    "business_establishment_year",
    "business_sector_encoded",
    "business_level_encoded",
    "business_starting_capital",
    "business_current_capital",
    "business_annual_profit",
    "business_annual_sales",
    "business_starting_no_of_employees",
    "business_current_no_of_employees",
    "business_source_encoded",
    "business_association_encoded",
    "capital_growth",
    "employee_growth",
    "profit_margin",
    "business_age"
  ],
  "num_features": 26,
  "contamination": 0.02,
  "n_estimators": 175
}
```

---

## Authentication

All endpoints require API key authentication via the `X-API-Key` header:

```
X-API-Key: your-api-key-here
```

---

## Error Handling

### Common Error Responses

**Invalid Customer ID (400):**
```json
{
  "detail": "Invalid customer_id format. Must start with 'CUST_' and contain only alphanumeric characters and underscores"
}
```

**Model Not Available (503):**
```json
{
  "detail": "Merged model not available. Please train the merged model first."
}
```

**Server Error (500):**
```json
{
  "detail": "Error processing [operation]: [error message]"
}
```

---

## Features of All Endpoints

1. **Input Validation**
   - Customer ID format validation
   - Field range/format validation
   - Type checking

2. **Logging & Monitoring**
   - Structured logging at INFO, WARNING, and ERROR levels
   - Processing time metrics
   - Anomaly count tracking

3. **Audit Trail**
   - All anomaly detections are logged with:
     - Customer ID
     - Model type
     - Prediction result
     - Risk level
     - Anomaly score

4. **Explainability (SHAP)**
   - Top contributing features
   - Feature values used in prediction
   - SHAP values for each feature
   - Per-transaction/record explanations

5. **Error Resilience**
   - Per-record error handling in batch operations
   - Graceful error messages
   - Continues processing remaining records on errors

---

## Usage Examples

### Example 1: Single Transaction Check
```bash
curl -X POST "http://localhost:8000/api/v1/transaction/check" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST_12345",
    "date": "2024-10-25T14:30:00",
    "credit": 1000.0,
    "debit": 0.0,
    "closingBalance": 5000.0,
    "narrative": "Cash Deposit",
    "source": "CASH DEPOSIT"
  }'
```

### Example 2: Customer Batch Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/transaction/customer/batch" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST_12345",
    "transactions": [...]
  }'
```

### Example 3: Merged Model Check
```bash
curl -X POST "http://localhost:8000/api/v1/merged/check" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST_12345",
    "customer_name": "John Doe",
    ...
    "business_association_type": "SOLE_PROPRIETORSHIP"
  }'
```

---

## Model Information

### Transaction Model
- **Type:** Isolation Forest (Unsupervised)
- **Features:** 8
- **Contamination:** 0.02 (2%)
- **Estimators:** 150
- **Purpose:** Detect anomalous individual transactions

### Merged Model
- **Type:** Isolation Forest (Unsupervised)
- **Features:** 26 (KYC + Business)
- **Contamination:** 0.02 (2%)
- **Estimators:** 175
- **Purpose:** Detect anomalies in combined customer-business profiles

### Risk Level Classification
- **HIGH:** Score < HIGH_RISK_THRESHOLD
- **MEDIUM:** Score < MEDIUM_RISK_THRESHOLD but >= HIGH_RISK_THRESHOLD
- **LOW:** Score >= MEDIUM_RISK_THRESHOLD

---

## Implementation Details

### Files Modified/Created
- `app/api/v1/endpoints/transaction.py` - Transaction endpoints
- `app/api/v1/endpoints/unsupervised/merged.py` - Merged model endpoints
- `app/api/v1/router.py` - Router configuration
- `app/main.py` - Fixed import statement

### Key Services Used
- `UnsupervisedAnomalyDetectorService` - Core anomaly detection
- `ShapExplainerService` - SHAP explainability
- `AuditLogger` - Audit trail logging
- `InputSanitizer` - Input validation

---

## Status
✅ All endpoints finalized and ready for use
✅ Error handling implemented
✅ Audit logging implemented
✅ SHAP explanations integrated
✅ Input validation implemented
