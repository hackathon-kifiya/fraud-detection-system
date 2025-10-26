# API Structure: Supervised vs Unsupervised Anomaly Detection

## Overview

The Anomaly Detection API is now organized into two separate detection paradigms:

1. **Unsupervised Models** (Isolation Forest)
   - Uses anomaly scoring and statistical analysis
   - No training labels required
   - Located under `/api/v1/unsupervised/`

2. **Supervised Models** (Random Forest Classifiers)
   - Uses labeled training data (binary classification)
   - Confidence-based anomaly probability
   - Located under `/api/v1/supervised/`

---

## API Structure

```
/api/v1/
├── /unsupervised/
│   ├── /kyc/              [KYC anomaly detection (Isolation Forest)]
│   ├── /transaction/      [Transaction anomaly detection (Isolation Forest)]
│   └── /merged/           [Combined KYC + Business (Isolation Forest)]
└── /supervised/
    ├── /transaction/      [Transaction anomaly detection (Random Forest)]
    └── /merged/           [Combined KYC + Business (Random Forest)]
```

---

## Unsupervised Endpoints

### KYC Endpoints - `/api/v1/unsupervised/kyc/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/check` | POST | Single KYC record anomaly check |
| `/batch` | POST | Batch KYC records (up to 100) |
| `/combined/check` | POST | Combined KYC + Business check |
| `/combined/batch` | POST | Batch combined records |
| `/stats` | GET | Model statistics |
| `/combined/stats` | GET | Combined model statistics |
| `/check-with-masking` | POST | KYC check with data masking demo |

**Model Type:** Isolation Forest  
**Detection:** Anomaly score based on isolation distance

---

### Transaction Endpoints - `/api/v1/unsupervised/transaction/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/check` | POST | Single transaction anomaly check |
| `/batch` | POST | Batch transactions (up to 100) |
| `/customer/batch` | POST | All customer transactions with aggregation |
| `/stats` | GET | Model statistics |

**Model Type:** Isolation Forest  
**Detection:** Anomaly score based on isolation distance  
**Customer Flagging Logic:**
- Anomaly ratio > 30%, OR
- High-risk transactions > 20%, OR
- Customer risk level = HIGH

---

### Merged Model Endpoints - `/api/v1/unsupervised/merged/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/check` | POST | Single merged (KYC + Business) check |
| `/batch` | POST | Batch merged records (up to 100) |
| `/stats` | GET | Model statistics |

**Model Type:** Isolation Forest  
**Features:** 26 combined (11 KYC + 12 Business + 3 derived)  
**Detection:** Comprehensive customer-business profile analysis

---

## Supervised Endpoints

### Transaction Endpoints - `/api/v1/supervised/transaction/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/check` | POST | Single transaction anomaly check |
| `/batch` | POST | Batch transactions (up to 100) |
| `/customer/batch` | POST | All customer transactions with aggregation |
| `/stats` | GET | Model statistics |

**Model Type:** Random Forest Classifier  
**Detection:** Anomaly probability (0-1)  
**Features:** 8 transaction features
**Key Difference from Unsupervised:**
- Outputs confidence-based probability
- Trained on labeled data
- Class 1 = Anomaly, Class 0 = Normal

---

### Merged Model Endpoints - `/api/v1/supervised/merged/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/check` | POST | Single merged (KYC + Business) check |
| `/batch` | POST | Batch merged records (up to 100) |
| `/stats` | GET | Model statistics |

**Model Type:** Random Forest Classifier  
**Features:** 26 combined (11 KYC + 12 Business + 3 derived)  
**Detection:** Supervised classification of customer-business profiles

---

## Comparison: Unsupervised vs Supervised

| Aspect | Unsupervised (Isolation Forest) | Supervised (Random Forest) |
|--------|--------------------------------|--------------------------|
| **Training Data** | Unlabeled anomalies | Labeled data (binary) |
| **Model Type** | Anomaly scoring | Binary classification |
| **Score Type** | Isolation distance | Probability (0-1) |
| **Threshold** | Statistical isolation | Configurable probability |
| **Interpretability** | Feature importance | Feature importance |
| **New Data Handling** | No retraining needed | Retraining may help |
| **Imbalanced Data** | Handles naturally | Requires class weights |

---

## Response Format (Both Models)

### Successful Response (200 OK)
```json
{
  "is_anomaly": false,
  "anomaly_score": 0.75,
  "risk_level": "MEDIUM",
  "explanation": {
    "top_contributing_features": {
      "amount": 0.45,
      "transaction_type": 0.32
    },
    "feature_values": {
      "amount": 1500.0,
      "transaction_type": 2
    },
    "shap_values": {
      "amount": -0.15,
      "transaction_type": 0.08
    }
  },
  "timestamp": "2024-10-26T10:00:00"
}
```

### Difference in Score Interpretation
- **Unsupervised:** Score = anomaly score (negative = more anomalous)
- **Supervised:** Score = probability (0-1, higher = more likely anomalous)

---

## Risk Level Thresholds

**Both models use the same risk classification:**

```python
# For Unsupervised (negative scores)
HIGH_RISK_THRESHOLD = -0.3      # score < -0.3 → HIGH risk
MEDIUM_RISK_THRESHOLD = -0.1    # -0.3 ≤ score < -0.1 → MEDIUM risk
                                 # score ≥ -0.1 → LOW risk

# For Supervised (probability scores)
HIGH_RISK_THRESHOLD = 0.7       # probability ≥ 0.7 → HIGH risk
MEDIUM_RISK_THRESHOLD = 0.5     # 0.5 ≤ probability < 0.7 → MEDIUM risk
                                 # probability < 0.5 → LOW risk
```

---

## Batch Processing

Both supervised and unsupervised endpoints support batch processing:

### Standard Batch (Multiple Records)
```json
{
  "transactions": [
    {...},
    {...},
    ...
  ]
}
```

**Limits:** Up to 100 records per request

### Customer Batch (Single Customer, Multiple Transactions)
```json
{
  "customer_id": "CUST_12345",
  "transactions": [
    {...},
    {...},
    ...
  ]
}
```

**Limits:** Up to 1000 transactions per customer  
**Features:** Aggregated customer-level risk assessment

---

## Authentication

All endpoints require API key authentication:

```bash
curl -H "X-API-Key: your-api-key-here" \
     -H "Content-Type: application/json" \
     "http://localhost:8000/api/v1/unsupervised/transaction/check"
```

---

## Error Handling

### Common Error Responses

**400 - Invalid Input**
```json
{
  "detail": "Invalid customer_id format. Must start with 'CUST_' and contain only alphanumeric characters and underscores"
}
```

**503 - Model Not Available**
```json
{
  "detail": "Supervised merged model not available. Please train the merged model first."
}
```

**500 - Server Error**
```json
{
  "detail": "Error processing [operation]: [error details]"
}
```

---

## Service Configuration

### app/services/

- `unsupervised_anomaly_detector.py` - Isolation Forest service
- `supervised_anomaly_detector.py` - Random Forest service

### app/api/v1/

- `dependencies.py` - Dependency injection
- `router.py` - Main API router with both paradigms
- `endpoints/unsupervised/` - Unsupervised endpoints
- `endpoints/supervised/` - Supervised endpoints

### app/main.py

Initializes both services at startup:

```python
# Unsupervised service
unsupervised_anomaly_service = UnsupervisedAnomalyDetectorService()
await unsupervised_anomaly_service.initialize()

# Supervised service
supervised_anomaly_service = SupervisedAnomalyDetectorService()
await supervised_anomaly_service.initialize()
```

Both services are stored in `app.state` for dependency injection.

---

## Model Files

### Unsupervised Models
- `data/models/kyc_model.pkl` / `kyc_scaler.pkl`
- `data/models/transaction_model.pkl` / `transaction_scaler.pkl`
- `data/models/merged_model.pkl` / `merged_scaler.pkl`
- `data/models/customer_model.pkl` / `customer_scaler.pkl`

### Supervised Models
- `data/models/kyc_supervised_model.pkl` / `kyc_supervised_scaler.pkl`
- `data/models/transaction_supervised_model.pkl` / `transaction_supervised_scaler.pkl`
- `data/models/merged_supervised_model.pkl` / `merged_supervised_scaler.pkl`
- `data/models/customer_supervised_model.pkl` / `customer_supervised_scaler.pkl`

---

## Usage Examples

### Example 1: Unsupervised Single Transaction Check
```bash
curl -X POST "http://localhost:8000/api/v1/unsupervised/transaction/check" \
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

### Example 2: Supervised Customer Batch Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/supervised/transaction/customer/batch" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST_12345",
    "transactions": [...]
  }'
```

### Example 3: Unsupervised Merged Check
```bash
curl -X POST "http://localhost:8000/api/v1/unsupervised/merged/check" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST_12345",
    "customer_name": "John Doe",
    ...
    "business_association_type": "SOLE_PROPRIETORSHIP"
  }'
```

### Example 4: Supervised Merged Batch
```bash
curl -X POST "http://localhost:8000/api/v1/supervised/merged/batch" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "records": [...]
  }'
```

---

## Health Check

```bash
curl "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "unsupervised_kyc_model_loaded": true,
  "unsupervised_transaction_model_loaded": true,
  "unsupervised_combined_model_loaded": true,
  "supervised_kyc_model_loaded": true,
  "supervised_transaction_model_loaded": true,
  "supervised_combined_model_loaded": true
}
```

---

## Summary

✅ **Two Complete Detection Paradigms**
- Unsupervised: Statistical anomaly detection (Isolation Forest)
- Supervised: Confidence-based classification (Random Forest)

✅ **Organized API Structure**
- Clear URL separation: `/unsupervised/` vs `/supervised/`
- Consistent endpoint patterns across both paradigms
- Full feature parity between models

✅ **Production Ready**
- Error handling and validation
- SHAP explainability for both models
- Audit logging for compliance
- Batch processing support
- Health checks and monitoring
