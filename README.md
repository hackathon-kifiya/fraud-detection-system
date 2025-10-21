# Fraud Detection MVP

A comprehensive fraud detection system for embedded finance with PostgreSQL database, Python fraud detection engine, Golang backend API, and React frontend.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   React     │    │   Golang    │    │   Python    │
│  Frontend   │◄──►│   Backend   │◄──►│   Engine    │
│  (Port 3000)│    │  (Port 8080)│    │  (Port 5001)│
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │ PostgreSQL  │
                   │  (Port 5432)│
                   └─────────────┘
```

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Clone the repository
2. Copy environment file:
   ```bash
   cp .env.example .env
   ```
3. Start all services:
   ```bash
   docker-compose up --build
   ```
4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - Engine API: http://localhost:5001

## Demo Workflow

1. **Upload Sample Data**: Use the CSV templates in the `templates/` directory
2. **Run Detection**: Click "Run Fraud Detection" to analyze the data
3. **Review Results**: Check the dashboard for flagged items
4. **Verify Items**: Mark items as "Fraud" or "Safe" for verification

## Usage

### 1. Upload Data
- Navigate to the upload page
- Use the provided CSV templates in the `templates/` directory
- Upload each data type (transactions, loan_requests, credit_history, kyc, repayments)
- Click "Trigger Detection" to run fraud analysis

### 2. Review Flagged Items
- Go to the dashboard to view flagged items
- Review risk scores and reasons
- Mark items as "Fraud" or "Safe" for verification

## API Endpoints

### Backend API (Port 8080)

#### Upload Endpoints
- `POST /upload/transactions` - Upload transaction data (CSV)
- `POST /upload/loan_requests` - Upload loan request data (CSV)
- `POST /upload/credit_history` - Upload credit history data (CSV)
- `POST /upload/kyc` - Upload KYC data (CSV)
- `POST /upload/repayments` - Upload repayment data (CSV)

#### Detection & Review
- `POST /api/detect` - Trigger fraud detection
  - Body: `{"days_back": 30}` (optional)
  - Response: Detection results with flagged counts
- `GET /api/flagged` - Get flagged items with pagination
  - Query params: `status`, `type`, `user_id`, `page`, `limit`
- `GET /api/flagged/:id` - Get specific flagged item
- `POST /api/verify/:id` - Verify flagged item
  - Body: `{"status": "fraud"|"safe"}`
- `GET /api/flagged/stats` - Get flagged items statistics
- `GET /api/detect/status` - Get detection system status

#### Health Check
- `GET /health` - Backend health status

### Engine API (Port 5001)

- `POST /detect` - Run fraud detection analysis
  - Body: `{"days_back": 30}` (optional)
  - Response: Detailed detection results
- `GET /health` - Engine health status
- `GET /detect/status` - Engine configuration and status

## CSV Templates

Use the templates in the `templates/` directory for data upload:

- `transactions.csv` - Transaction history (txn_id, user_id, amount, timestamp, type, payment_method, items, account_balance)
- `loan_requests.csv` - Loan applications (loan_id, user_id, amount_requested, purpose, request_timestamp)
- `credit_history.csv` - Credit scores and history (user_id, credit_score, past_loans, defaults_count)
- `kyc.csv` - Know Your Customer data (user_id, verified_status, documents, verification_timestamp)
- `repayments.csv` - Loan repayments (repayment_id, user_id, loan_id, amount, timestamp, status)

### Sample Data
Each template includes 2-3 example rows with realistic data for testing the fraud detection system.

## Troubleshooting

### Common Issues

1. **Database connection errors**: Ensure PostgreSQL is healthy before starting other services
2. **Port conflicts**: Check if ports 3000, 5001, 8080, or 5432 are already in use
3. **CSV upload failures**: Verify CSV format matches template headers exactly

### Logs

View logs for specific services:
```bash
docker-compose logs postgres
docker-compose logs engine
docker-compose logs backend
docker-compose logs frontend
```

### Reset Database

To reset the database and start fresh:
```bash
docker-compose down -v
docker-compose up --build
```

## Development

### Running Individual Services

```bash
# Database only
docker-compose up postgres

# Backend only (requires database)
docker-compose up postgres backend

# Frontend only (requires backend)
docker-compose up postgres backend frontend
```

### Adding New Detection Rules

1. Edit `engine/detection.py`
2. Add new rule functions in the appropriate check method
3. Update the main detection pipeline in `run_detection()`
4. Rebuild the engine service: `docker-compose up --build engine`

### Database Schema

The system uses PostgreSQL with 6 main tables:
- `transactions` - Financial transactions with JSONB items field
- `loan_requests` - Loan applications and requests
- `credit_history` - User credit scores and loan history
- `kyc` - Know Your Customer verification data
- `repayments` - Loan repayment records
- `flagged_items` - Fraud detection results and verification status

### Fraud Detection Rules

The engine implements multiple rule categories:
- **Transaction Rules**: Multiple credits, rejections, unusual amounts, nighttime activity
- **Loan Rules**: Multiple requests, amount vs credit score
- **Credit Rules**: Multiple defaults, low credit scores
- **KYC Rules**: Unverified status
- **Repayment Rules**: Late payments, duplicate IDs

Risk scoring combines statistical analysis (40%), rule violations (30%), and new data checks (30%).
