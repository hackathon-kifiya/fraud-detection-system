# Rule Engine Integration

This document describes the integration between the backend and the dynamic rule engine.

## Architecture Overview

The system now supports a fully dynamic rule engine that can evaluate any data type against configurable rules:

```
Frontend → Backend → Rule Engine → Database
    ↓         ↓           ↓
Flagged Items ← Rules ← DRL Files
```

## Components

### 1. Rule Engine (Java/Spring Boot)
- **Port**: 8082 (external), 8081 (internal)
- **API Endpoint**: `/api/evaluate`
- **Features**:
  - Dynamic data type support
  - DRL rule execution
  - Single-record evaluation
  - Database-backed rule management

### 2. Backend (Go/Gin)
- **Port**: 8081 (external), 8080 (internal)
- **API Endpoints**: `/api/v1/evaluate/*`
- **Features**:
  - Rule evaluation service
  - Flagged item creation
  - Health checks

## API Endpoints

### Rule Engine Direct Access

#### Evaluate Data
```bash
POST http://localhost:8082/api/evaluate
Content-Type: application/json

{
  "dataType": "transaction",
  "facts": [{
    "entityId": "txn-123",
    "amount": 1500.0,
    "accountBalance": 500.0,
    "type": "debit",
    "paymentMethod": "card"
  }]
}
```

### Backend Integration

#### Evaluate Any Data Type
```bash
POST http://localhost:8081/api/v1/evaluate
Content-Type: application/json

{
  "dataType": "transaction",
  "data": [{
    "entityId": "txn-123",
    "amount": 1500.0,
    "accountBalance": 500.0,
    "type": "debit",
    "paymentMethod": "card"
  }]
}
```

#### Evaluate Specific Data Types
```bash
# Transaction
POST http://localhost:8081/api/v1/evaluate/transaction

# KYC
POST http://localhost:8081/api/v1/evaluate/kyc

# Loan
POST http://localhost:8081/api/v1/evaluate/loan

# Credit
POST http://localhost:8081/api/v1/evaluate/credit

# Repayment
POST http://localhost:8081/api/v1/evaluate/repayment
```

#### Health Checks
```bash
# Rule Engine Health
GET http://localhost:8082/health

# Backend Health
GET http://localhost:8081/health

# Rule Engine Health via Backend
GET http://localhost:8081/api/v1/rule-engine/health
```

## Data Types

The system supports both predefined and custom data types:

### Predefined Types
- `transaction` - Financial transactions
- `kyc` - Know Your Customer data
- `loan` - Loan applications
- `credit` - Credit history
- `repayment` - Loan repayments

### Custom Types
Any string can be used as a data type, e.g.:
- `payment` - Payment processing
- `withdrawal` - ATM withdrawals
- `transfer` - Money transfers
- `deposit` - Account deposits

## Rule Creation

Rules are created via the rule engine API:

```bash
POST http://localhost:8082/api/rules
Content-Type: application/json

{
  "name": "High Value Transaction Rule",
  "dataType": "transaction",
  "drlContent": "package rules;\n\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"High value transaction\"\nwhen\n    $t: DynamicFact( dataType == \"transaction\", getDoubleProperty(\"amount\") > 10000 )\nthen\n    $t.addViolation(\"HIGH_VALUE\", 25, \"High value transaction detected\");\nend",
  "createdBy": "admin"
}
```

## DRL Rule Examples

### Transaction Rules
```drl
package rules;

import com.frauddetection.domain.DynamicFact;

rule "High amount vs balance"
when
    $t: DynamicFact( dataType == "transaction", getDoubleProperty("amount") > getDoubleProperty("accountBalance") * 2 )
then
    $t.addViolation("TXN_HIGH_VS_BAL", 20, "Transaction amount exceeds 2x account balance");
end
```

### Custom Data Type Rules
```drl
package rules;

import com.frauddetection.domain.DynamicFact;

rule "High value custom transaction"
when
    $f: DynamicFact( 
        dataType in ("payment", "transfer", "withdrawal"), 
        getDoubleProperty("amount") > 5000 
    )
then
    $f.addViolation("HIGH_VALUE", 20, "High value transaction detected");
end
```

## Configuration

### Environment Variables

#### Backend
- `ENGINE_URL` - Rule engine URL (default: http://localhost:8082/api)
- `PYTHON_STATS_URL` - Python stats service URL (default: http://localhost:5001)

#### Rule Engine
- `DATABASE_URL` - PostgreSQL connection string
- `SERVER_PORT` - Server port (default: 8081)

### Docker Compose
The services are configured in `docker-compose.yml`:
- Rule engine: `http://rule-engine:8081/api`
- Backend: `http://backend:8080`

## Testing

Run the integration test:
```bash
./test-rule-engine-integration.sh
```

## Workflow

1. **Data Submission**: Frontend submits data to backend
2. **Rule Evaluation**: Backend calls rule engine to evaluate data
3. **Violation Detection**: Rule engine applies DRL rules and returns violations
4. **Flagged Item Creation**: Backend creates flagged items for violations
5. **Review Process**: Analysts review flagged items in the frontend

## Benefits

- **Dynamic Data Types**: Support any data type without code changes
- **Flexible Rules**: DRL-based rules can be modified without redeployment
- **Single API**: Unified evaluation endpoint for all data types
- **Scalable**: Rule engine can be scaled independently
- **Maintainable**: Clear separation of concerns between services
