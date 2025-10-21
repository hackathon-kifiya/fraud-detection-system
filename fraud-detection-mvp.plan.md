# Fraud Detection MVP Implementation Plan

## Overview

Create a complete fraud detection system with PostgreSQL for data persistence, a Python service for fraud analysis, a Golang backend for API/orchestration, and a React frontend for data upload and review - all running via Docker Compose.

## Architecture Summary

- **PostgreSQL**: Centralized storage for transactions, loans, credit history, KYC, repayments, and flagged items
- **Python Engine**: Statistical analysis, rule-based flagging, and risk scoring (Flask API)
- **Golang Backend**: Data ingestion, orchestration, and API for frontend (Gin framework)
- **React Frontend**: Upload interface and flagged items dashboard (no auth)

## Implementation Steps

### 1. Project Structure Setup

Create the following directory structure:

```
fraud-detection/
├── docker-compose.yml
├── .env.example
├── README.md
├── database/
│   └── init.sql
├── engine/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── detection.py
│   └── config.py
├── backend/
│   ├── Dockerfile
│   ├── go.mod
│   ├── go.sum
│   ├── main.go
│   ├── handlers/
│   │   ├── upload.go
│   │   ├── detection.go
│   │   └── flagged.go
│   ├── models/
│   │   └── models.go
│   └── db/
│       └── postgres.go
├── frontend/
│   ├── package.json
│   ├── Dockerfile
│   ├── public/
│   └── src/
│       ├── App.js
│       ├── components/
│       │   ├── UploadPage.js
│       │   ├── Dashboard.js
│       │   └── FlaggedTable.js
│       └── services/
│           └── api.js
└── templates/
    ├── transactions.csv
    ├── loan_requests.csv
    ├── credit_history.csv
    ├── kyc.csv
    └── repayments.csv
```

### 2. Database Layer (PostgreSQL)

**File**: `database/init.sql`

Create schema with 6 tables:

- `transactions`: txn_id (PK), user_id, amount, timestamp, type, payment_method, items (jsonb), account_balance
- `loan_requests`: loan_id (PK), user_id, amount_requested, purpose, request_timestamp
- `credit_history`: user_id (PK), credit_score, past_loans (jsonb), defaults_count
- `kyc`: user_id (PK), verified_status, documents (jsonb), verification_timestamp
- `repayments`: repayment_id (PK), user_id, loan_id, amount, timestamp, status
- `flagged_items`: id (PK), type, ref_id, user_id, score, reasons (jsonb), status, verified_at

Add indexes on user_id and timestamp columns for query performance.

### 3. Python Fraud Detection Engine

**Key Files**: `engine/main.py`, `engine/detection.py`

**Features**:

- Flask API with `/detect` endpoint (accepts time_range parameter)
- PostgreSQL connection using psycopg2
- Detection pipeline:
  - **Data Aggregation**: Query and join tables by user_id/loan_id
  - **Statistical Analysis**: Calculate z-scores, IQR for anomalies, baseline metrics per user
  - **Rule-Based Checks**: 
    - Transactions: Multiple credits in 5min, rejections, volume spikes, nighttime activity
    - Loans: >2 requests in 24h, amount vs credit history
    - Credit: defaults_count >1, score drop >50
    - KYC: unverified status
    - Repayments: >3 late payments, duplicates
  - **Risk Scoring**: Weighted combination (stats 40%, rules 30%, new checks 30%)
- Insert results into `flagged_items` table with score >70
- Dependencies: Flask, psycopg2, pandas, numpy

**File**: `engine/requirements.txt`

```
flask==3.0.0
psycopg2-binary==2.9.9
pandas==2.1.0
numpy==1.24.0
```

### 4. Golang Backend API

**Key Files**: `backend/main.go`, `backend/handlers/*.go`, `backend/db/postgres.go`

**Endpoints**:

- `POST /upload/transactions`: Parse CSV, batch insert to transactions table
- `POST /upload/loan_requests`: Insert loan requests
- `POST /upload/credit_history`: Insert credit history
- `POST /upload/kyc`: Insert KYC records
- `POST /upload/repayments`: Insert repayments
- `POST /api/detect`: Trigger engine with time range, return flagged count
- `GET /api/flagged`: Fetch pending flagged items with pagination
- `POST /api/verify/:id`: Update flagged item status (fraud/safe)

**Implementation**:

- Use Gin framework for routing
- `github.com/jackc/pgx/v5` for PostgreSQL
- CSV parsing with `encoding/csv`
- HTTP client to call engine `/detect` endpoint
- CORS middleware for frontend

**File**: `backend/go.mod`

```
module fraud-detection-backend

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/jackc/pgx/v5 v5.5.0
    github.com/google/uuid v1.5.0
)
```

### 5. React Frontend

**Key Files**: `frontend/src/App.js`, `frontend/src/components/*.js`

**Pages**:

1. **Upload Page**: 

   - 5 file upload forms (one per data type)
   - Calls backend `/upload/{type}` endpoints
   - Success/error notifications
   - "Trigger Detection" button (calls `/api/detect`)

2. **Dashboard**:

   - Table showing flagged items (type, ref_id, user_id, score, reasons, status)
   - Action buttons: Mark as Fraud / Mark as Safe
   - Filter by status (pending/fraud/safe)
   - Risk score histogram using Chart.js
   - Pagination support

**Dependencies**: React 18, Axios, Material-UI (@mui/material), Chart.js

**File**: `frontend/package.json`

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "@mui/material": "^5.14.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0"
  }
}
```

### 6. CSV Templates

**Files**: `templates/*.csv`

Create 5 CSV templates with headers and 2-3 example rows:

- `transactions.csv`: txn_id, user_id, amount, timestamp, type, payment_method, items, account_balance
- `loan_requests.csv`: loan_id, user_id, amount_requested, purpose, request_timestamp
- `credit_history.csv`: user_id, credit_score, past_loans, defaults_count
- `kyc.csv`: user_id, verified_status, documents, verification_timestamp
- `repayments.csv`: repayment_id, user_id, loan_id, amount, timestamp, status

### 7. Docker Configuration

**File**: `docker-compose.yml`

Define 4 services:

1. **postgres**: postgres:15 image, volume for data persistence, init.sql mounted
2. **engine**: Python service, depends_on postgres, exposes port 5001
3. **backend**: Go service, depends_on postgres and engine, exposes port 8080
4. **frontend**: React dev server (or nginx for production), exposes port 3000

**File**: `.env.example`

```
DATABASE_URL=postgresql://frauduser:fraudpass@postgres:5432/frauddb
ENGINE_URL=http://engine:5001
BACKEND_URL=http://backend:8080
```

### 8. Documentation

**File**: `README.md`

Include:

- Architecture overview diagram (ASCII art)
- Prerequisites (Docker, Docker Compose)
- Quick start: `docker-compose up --build`
- How to upload CSV files (use templates)
- How to trigger detection
- How to review flagged items
- API documentation (endpoint list)
- Troubleshooting common issues

## Key Implementation Details

**PostgreSQL Schema Decisions**:

- Use UUID for primary keys (txn_id, loan_id, etc.)
- JSONB for flexible fields (items, past_loans, documents, reasons)
- Indexes on user_id, timestamp, loan_id for join performance
- status enum: 'pending', 'fraud', 'safe'

**Engine Detection Logic**:

- Query last N days of data (configurable via API)
- Per-user baseline calculation using pandas groupby
- Z-score threshold: 3.0 for amount anomalies
- Rule violations increment rule_score by 10-20 points each
- Final score = (stat_score * 0.4) + (rule_score * 0.3) + (new_checks * 0.3)
- Flag if score >= 70

**Backend CSV Parsing**:

- Validate headers match expected columns
- Parse JSON fields (items, past_loans, documents) from CSV strings
- Batch insert in chunks of 100 rows
- Return counts and error messages

**Frontend State Management**:

- Use React hooks (useState, useEffect) for simplicity
- Poll `/api/flagged` every 10 seconds on dashboard
- Material-UI DataGrid for table with sorting/filtering
- Chart.js histogram bins: 0-50, 50-70, 70-85, 85-100

## Testing Strategy

1. **Database**: Test table creation, insert sample data manually
2. **Engine**: Unit test each rule, test API endpoint with curl
3. **Backend**: Test each upload endpoint with curl, verify DB inserts
4. **Frontend**: Manual testing in browser
5. **Integration**: Upload templates → trigger detection → verify flags appear

## Time Estimates

- Setup & Docker config: 45 min
- Database schema: 30 min
- Engine implementation: 2 hours
- Backend API: 1.5 hours
- Frontend: 2 hours
- CSV templates: 15 min
- Integration & testing: 1 hour
- **Total**: ~7-8 hours

## Success Criteria

- All services start via `docker-compose up`
- CSV uploads succeed and populate database
- Detection endpoint flags suspicious items (score >70)
- Dashboard displays flagged items with correct details
- Verification updates status in database
- README allows new user to run full demo in <10 minutes