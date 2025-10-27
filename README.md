MAX - A fraud detection system for embedded finance.

## Architecture

```
                        ┌─────────────────┐
                        │    Frontend     │
                        │     (React)     │
                        └────────┬────────┘
                                 │
                                 ↓
                        ┌─────────────────┐
                        │    Backend      │
                        │   (Go/Gin)      │
                        └────────┬────────┘
                                 │
              ┌──────────────────┼────────────────────────┼────────────────────┼───────────────────┐
              │                  │                        │                    │                   │
              ↓                  ↓                        ↓                    ↓                   ↓
    ┌──────────────────┐  ┌──────────────────┐   ┌──────────────────┐  ┌─────────────────┐ ┌─────────────────┐   
    │ Data Management  │  │   Rule Engine    │   │  Decision Service│  │ Anomaly Engine  │ │ Prediction Eng  │ 
    │    Service       │  ┤   (Java/Spring)  │   │   (Python)       │  │   (Python)      │ │   (Python)      │
    │   (Python)       │  └──────────────────┘   └──────────────────┘  └─────────────────┘ └─────────────────┘
    └──────────────────┘                                         
  
```

**Key Features:**
- **Data-Type Driven**: Centralized data type management
- **Hierarchical Configuration**: System defaults + per-data-type overrides
- **Flexible Decision Logic**: Data-type-specific risk thresholds and weights
- **Integrated Engines**: Rule-based, ML-based, and anomaly detection
## Data Flow

```
        ┌────────────────────────────────────────┐
        │         Data Ingestion                 │
        │  (Transactions, KYC, Loans, etc.)      │
        └────────────────┬───────────────────────┘
                         │
                         ↓
        ┌────────────────────────────────────────┐
        │            BACKEND (Go)                │
        │  • Orchestration & Workflows           │
        │  • User Management (JWT Auth)          │
        │  • Input Validation & Sanitization     │
        │  • Data Type Routing                   │
        └────────────────┬───────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ↓               ↓               ↓
┌──────────────┐  ┌────────────┐  ┌─────────────┐
│ RULE ENGINE  │  │ PREDICTION │  │  ANOMALY    │
│   (Java)     │  │   ENGINE   │  │ DETECTION   │
│              │  │  (Python)  │  │  (Python)   │
│ • DRL Rules  │  │ • XGBoost  │  │ • Isolation │
│ • Drools     │  │ • Features │  │ • Patterns  │
│ • Dynamic    │  │ • ML Model │  │ • Outliers  │
└──────┬───────┘  └─────┬──────┘  └──────┬──────┘
       │ Normalized     │ Normalized     │ Normalized
       │ ScoreRule      │ ScoreML        │ ScoreAnomaly
       │ (0-1)          │ (0-1)          │ (0-1)
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ↓
        ┌────────────────────────────────────────┐
        │   DECISION SERVICE (Python)            │
        │                                        │
        │   Data-Type-Specific Configuration:    │
        │   • Transactions: W₁=50%, W₂=30%, W₃=20%│
        │   • KYC: W₁=40%, W₂=35%, W₃=25%        │
        │   • System Default: W₁=40%, W₂=35%, W₃=25%│
        │                                        │
        │   Score = W₁×Rule + W₂×ML + W₃×Anomaly │
        │                                        │
        │   Thresholds (per data type):          │
        │   ≤ 25%  → Auto-Approve                │
        │   25-85% → Human Review                │
        │   ≥ 85%  → Auto-Reject                 │
        └────────────────┬───────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ↓               ↓               ↓
    ┌─────────┐  ┌──────────────┐  ┌──────────┐
    │ APPROVE │  │ HUMAN REVIEW │  │  REJECT  │
    └─────────┘  └──────┬───────┘  └──────────┘
                        │
                        │ Auditor Classification
                        ↓
        ┌────────────────────────────────────────┐
        │        FEEDBACK LOOP                   │
        │  • Human Labels → Training Data        │
        │  • Model Retraining & Optimization     │
        │  • Rule Updates & Refinement           │
        └────────────────────────────────────────┘
```


## Use cases

https://docs.google.com/spreadsheets/d/1YFAoreEE3M_yJxrjLkx92qoIPFh0YinAQshdZ5iMICQ/edit?usp=sharing


## Components

### Data Management Service (Python/FastAPI)
- **Centralized Data Types**: Single source of truth for all data type schemas
- **Schema Management**: Define and validate data structures for transactions, KYC, loans, etc.
- **API**: RESTful API for data type CRUD operations
- **Integration**: Used by all services for schema validation and discovery

### Rule Engine (Java/Spring Boot)
- **Dynamic Data Types**: Support for any data type via data-management-service integration
- **DRL Rules**: Drools-based rule engine with configurable rules
- **Real-time Evaluation**: Evaluate data against rules in milliseconds
- **Version Control**: Rule versioning and rollback capabilities
- **API**: RESTful API for rule evaluation and management
- **Database**: PostgreSQL for rule storage and versioning

### Decision Service (Python/FastAPI)
- **Hierarchical Configuration**: System-wide defaults + per-data-type overrides
- **Smart Aggregation**: Weighted scoring from rule, ML, and anomaly engines
- **Flexible Thresholds**: Data-type-specific approval/rejection thresholds
- **Non-linear Scoring**: Optional ML-based weight optimization
- **API**: RESTful API for decision-making and configuration

### Anomaly Detection Engine (Python/FastAPI)
- **Unsupervised Learning**: Isolation Forest for outlier detection
- **Pattern Recognition**: Identify unusual transaction patterns
- **Real-time Scoring**: Return anomaly scores (0-1) for transactions
- **API**: RESTful API for anomaly detection

### Prediction Engine (Python/FastAPI)
- **ML Models**: XGBoost/Neural networks for fraud prediction
- **Feature Engineering**: Automatic feature extraction from transaction data
- **Real-time Inference**: Fast prediction serving
- **API**: RESTful API for predictions

### Backend (Go/Gin)
- **Orchestration**: Coordinates all engines for fraud detection workflow
- **User Management**: JWT-based authentication and authorization
- **Flagged Items**: Automatic creation and management of suspicious items
- **Audit Trail**: Complete audit logging for compliance
- **API Gateway**: RESTful API for all frontend operations
- **Database**: PostgreSQL for application data

### Frontend (React/Material-UI)
- **Dashboard**: Real-time fraud detection metrics and KPIs
- **Data Type Management**: Create and manage custom data types
- **Rule Management**: Visual interface for creating and testing rules
- **Decision Configuration**: Per-data-type risk thresholds and weights
- **Case Management**: Review and classify flagged items
- **Analytics**: Performance metrics, reports, and visualizations
- **User Management**: Admin interface for user and role management

## Key Features

### 1. Data-Type-Driven Architecture
The system features a centralized data management service that enables:
- **Any Data Type**: Define custom data types (transactions, KYC, loans, repayments, etc.)
- **Schema Validation**: Automatic validation of all data against defined schemas
- **Cross-Service Integration**: All services use the same data type definitions
- **No Code Changes**: Add new data types without modifying any service

### 2. Dynamic Rule Engine
Fully configurable rule engine with:
- **DRL Rules**: Write rules in Drools Rule Language
- **Real-time Evaluation**: Evaluate data against rules in real-time
- **Data Type Specific**: Different rules for different data types
- **Version Control**: Rule versioning and rollback capabilities

### 3. Hierarchical Decision Configuration
Sophisticated decision-making with:
- **System Defaults**: Global configuration for all data types
- **Per-Data-Type Overrides**: Custom thresholds and weights per data type
- **Flexible Weights**: Configure importance of each engine (rule, ML, anomaly)
- **Dynamic Thresholds**: Data-type-specific auto-approve/reject thresholds
- **Visual Configuration**: Easy-to-use UI for configuration management

### 4. Multi-Engine Detection
Comprehensive fraud detection using:
- **Rule-Based**: Deterministic business logic and blacklists
- **ML-Based**: Predictive models trained on historical fraud patterns
- **Anomaly-Based**: Statistical outlier detection for unusual behavior
- **Intelligent Aggregation**: Smart combination of all engine scores

## Documentation

- [Rule Engine Integration](./RULE_ENGINE_INTEGRATION.md) - Detailed rule engine documentation
- [Decision Service Integration](./DECISION_DATA_TYPE_INTEGRATION.md) - Data-type-specific configuration guide
- [Plan Implementation Summary](./PLAN_IMPLEMENTATION_SUMMARY.md) - Development roadmap and status

## Quick Start

### 1. Start All Services
```bash
docker-compose up -d
```

### 2. Access Services
```
Swagger Documentation Links
1. Backend Service (Go)
Port: 8080
Swagger UI: http://localhost:8080/swagger/index.html
OpenAPI JSON: http://localhost:8080/swagger/doc.json
Description: Fraud Detection System API
2. Anomaly Detection Service (Python/FastAPI)
Port: 5001 (mapped to 8000 internally)
Swagger UI: http://localhost:5001/docs
ReDoc: http://localhost:5001/redoc
OpenAPI JSON: http://localhost:5001/api/v1/openapi.json
Description: KYC & Transaction Anomaly Detection API with Isolation Forest and Random Forest models
3. Decision Service (Python/FastAPI)
Port: 5003
Swagger UI: http://localhost:5003/docs
ReDoc: http://localhost:5003/redoc
OpenAPI JSON: http://localhost:5003/openapi.json
Description: Configurable decision service aggregating scores from rule engine, anomaly detection, and predictive engine
4. Data Management Service (Python/FastAPI)
Port: 5004
Swagger UI: http://localhost:5004/docs
ReDoc: http://localhost:5004/redoc
OpenAPI JSON: http://localhost:5004/openapi.json
Description: Single source of truth for data type definitions
5. Rule Engine Service (Java/Spring Boot)
Port: 8081
Swagger UI: http://localhost:8081/swagger-ui.html
OpenAPI JSON: http://localhost:8081/v3/api-docs
Description: Drools-based fraud detection rules engine
6. Risk Aggregator Service (Python/FastAPI)
Port: 8003 (configured in risk-aggregator, may vary)
Swagger UI: http://localhost:8003/api/v1/docs
ReDoc: http://localhost:8003/api/v1/redoc
OpenAPI JSON: http://localhost:8003/api/v1/openapi.json
Description: Risk Aggregator Service combining and aggregating risk signals
```

### 3. Default Login
```
Username: admin@fraud.com
Password: admin123
```

### 4. Test Integration
```bash
# Test rule engine integration
./rule-engine/test-rule-engine-workflow.sh

# Test data type synchronization
./test-datatype-sync.sh

# Full system integration test
./test-integration.sh
```

### 5. Initial Setup (First Time Only)

Run the migration script to initialize data-type-specific configurations:
```bash
cd decision
python scripts/migrate_configs.py
```

### 6. Sample Data seed
```bash
Run ./create-rules-for-data-types.sh
Run ./backend/seed_cases.sh
```
## v2

- Model driven risk aggrigation engine

Use a second machine learning model (a "meta-learner" or "stacking model") that takes the three engine scores (ScoreR​,ScoreML​,ScoreDA​) as its input features and outputs the final risk score. This allows for a non-linear combination of the scores.

