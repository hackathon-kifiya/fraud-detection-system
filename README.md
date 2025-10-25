MAX - A fraud detection system for embedded finance.

## Architecture

```
                                ┌─────────────────┐
                                │     frontend    │
                                └────────┬────────┘
                                         |
                                         ↓
                                ┌─────────────────┐
                                │     backend     │
                                └────────┬────────┘
                                         |           
                                         ↓
         ┌────────────────────┬────────────────────┬────────────────────┐
         ↓                    ↓                    ↓                    ↓
┌─────────────────┐  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   rule engine   │  │   descriptive   │ │   predictive    │ │ risk aggreagtion│ 
│                 │  │analytics engine │ │analytics engine │ │    engine       │
└─────────────────┘  └─────────────────┘ └─────────────────┘ └─────────────────┘


```
## Data flow

```
+--------------------+
                     
        ┌───────────────────────────────────────┐
        │            Ingestion                  │
        └─────────────────┬─────────────────────┘
                          │
                          │
                          ↓
        ┌───────────────────────────────────────┐
        │           BACKEND                     │
        │  - Orchestration (Workflows)          │
        │  - User Management (Auth)             │
        │  - Input/Ingestion                    │
        │  - Input Sanitization                 │
        └─────────────────┬─────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ↓               ↓               ↓
┌───────────────┐   ┌───────────┐ ┌──────────────┐
│ RULE ENGINE   │   │ ML MODEL  │ │   ANOMALY    │
│               │   │           │ │  DETECTION   │
│ Deterministic │   │ XGBoost/NN│ │              │
│ - Blacklist   |   | - Features| | Unsupervised |
| - Velocity    |   | - Scoring | | - Isolation  |
|               │   │           │ │ - Autoencoder|
└───────┬───────┘   └─────┬─────┘ └──────┬───────┘
        │                 │              │
        └─────────────────┼──────────────┘
                          ↓
        ┌───────────────────────────────────────┐
        │   RISK AGGREGATION ENGINE             │
        │                                       │
        │   Score = 0.3×Rule + 0.5×ML + 0.2×AD  │
        │                                       │
        │   Thresholds:                         │
        │   < 0.3  → Auto-Approve               │
        │   0.3-0.7 → Human Review              │
        │   > 0.7  → Auto-Block                 │
        └───────────────┬───────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ↓               ↓               ↓
    ┌────────┐  ┌──────────────┐  ┌────────┐
    │APPROVE │  │ HUMAN REVIEW │  │ BLOCK  │
    └────────┘  └──────┬───────┘  └────────┘
                       │
                       │
                       ↓
        ┌──────────────────────────────────────┐
        │   FEEDBACK LOOP                      │
        │   Labels → Model Retraining          │
        └──────────────────────────────────────┘
                   
```


## Use cases

https://docs.google.com/spreadsheets/d/1YFAoreEE3M_yJxrjLkx92qoIPFh0YinAQshdZ5iMICQ/edit?usp=sharing


## Components

### Rule Engine (Java/Spring Boot)
- **Dynamic Data Types**: Support for any data type (transaction, kyc, loan, credit, repayment, custom types)
- **DRL Rules**: Drools-based rule engine with configurable rules
- **API**: RESTful API for rule evaluation and management
- **Database**: PostgreSQL for rule storage and versioning

### Backend (Go/Gin)
- **Rule Integration**: Seamless integration with rule engine
- **Flagged Items**: Automatic creation of flagged items from rule violations
- **API**: RESTful API for data evaluation and management
- **Authentication**: JWT-based user authentication

### Frontend (React)
- **Dashboard**: Real-time fraud detection dashboard
- **Rule Management**: Interface for creating and managing rules
- **Flagged Items**: Review and management of flagged items
- **Analytics**: Performance metrics and reporting

## Rule Engine Integration

The system now features a fully dynamic rule engine that supports:

- **Any Data Type**: Create rules for any data type without code changes
- **DRL Rules**: Write rules in Drools Rule Language (DRL)
- **Real-time Evaluation**: Evaluate data against rules in real-time
- **Flagged Item Creation**: Automatically create flagged items for violations

See [RULE_ENGINE_INTEGRATION.md](./RULE_ENGINE_INTEGRATION.md) for detailed integration documentation.

## Quick Start

1. **Start Services**:
   ```bash
   docker-compose up -d
   ```

2. **Test Integration**:
   ```bash
   ./test-rule-engine-integration.sh
   ```

3. **Access Services**:
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8081
   - Rule Engine API: http://localhost:8082

## v2

- Model driven risk aggrigation engine

Use a second machine learning model (a "meta-learner" or "stacking model") that takes the three engine scores (ScoreR​,ScoreML​,ScoreDA​) as its input features and outputs the final risk score. This allows for a non-linear combination of the scores.

