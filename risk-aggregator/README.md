# Risk Aggregator Service

A FastAPI-based microservice for aggregating risk signals from multiple sources and computing comprehensive risk assessments.

## Overview

The Risk Aggregator Service combines risk signals from various data sources (KYC, transactions, credit history, loans, repayments) to provide a unified risk assessment for customers and entities. It features:

- **Multi-Source Risk Aggregation**: Combines signals from anomaly detection, rule engines, and other services
- **Weighted Risk Scoring**: Configurable weights for different risk categories
- **Batch Processing**: Efficient processing of multiple entities
- **Caching**: In-memory caching for improved performance
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **RESTful API**: Well-documented REST endpoints with automatic OpenAPI documentation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Risk Aggregator Service                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │   API v1    │  │  Services    │  │  Data Collector │    │
│  │  Endpoints  │→ │  - Risk      │→ │  - KYC         │    │
│  │             │  │  - Aggregation│  │  - Transaction │    │
│  └─────────────┘  │  - Cache     │  │  - Credit      │    │
│                   └──────────────┘  │  - Loan        │    │
│  ┌─────────────┐                    │  - Repayment   │    │
│  │ Middleware  │                    └─────────────────┘    │
│  │ - Rate Limit│                                            │
│  │ - Error     │                                            │
│  └─────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Anomaly       │  │   Java Engine   │  │   Backend API   │
│   Detection     │  │   (Rules)       │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Features

### Risk Assessment
- Individual entity risk scoring
- Comprehensive customer risk profiling
- Real-time risk level classification (LOW, MEDIUM, HIGH, CRITICAL)
- Configurable risk thresholds and weights

### Batch Processing
- Parallel processing of multiple entities
- Background job processing for large datasets
- Job status tracking and monitoring

### Data Integration
- Integration with anomaly detection service
- Integration with Java rule engine
- Extensible data collector for adding new sources

### Performance & Reliability
- In-memory caching with TTL
- Rate limiting middleware
- Structured logging (JSON format)
- Health check endpoints
- Error handling and recovery

## API Endpoints

### Health Checks
- `GET /health` - Basic health check
- `GET /api/v1/health` - Detailed health status
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

### Risk Assessment
- `POST /api/v1/risk/assess` - Assess risk for entity with provided signals
- `POST /api/v1/risk/customer` - Comprehensive customer risk assessment
- `GET /api/v1/risk/customer/{customer_id}` - Get cached customer risk
- `GET /api/v1/risk/score/{entity_id}` - Get quick risk score

### Batch Aggregation
- `POST /api/v1/aggregate/batch` - Process batch risk aggregation
- `POST /api/v1/aggregate/job` - Create background aggregation job
- `GET /api/v1/aggregate/job/{job_id}` - Get job status
- `POST /api/v1/aggregate/weights` - Update risk weights
- `GET /api/v1/aggregate/weights` - Get current risk weights

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

### Local Setup

1. Clone the repository:
```bash
cd risk-aggregator
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
make install
# or for development
make dev-install
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
make run
# or
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8003`

### Docker Setup

1. Build and run with Docker Compose:
```bash
make docker-up
```

2. View logs:
```bash
make docker-logs
```

3. Stop containers:
```bash
make docker-down
```

## Configuration

Environment variables (see `.env.example` for all options):

```bash
# Application
ENVIRONMENT=development
DEBUG=True
PORT=8003

# Security
SECRET_KEY=your-secret-key
API_KEY=optional-api-key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/fraud_detection

# External Services
ANOMALY_DETECTION_URL=http://localhost:8002
JAVA_ENGINE_URL=http://localhost:8080
BACKEND_URL=http://localhost:8000

# Risk Weights
RISK_SCORE_WEIGHTS={"kyc": 0.25, "transaction": 0.30, "credit": 0.20, "loan": 0.15, "repayment": 0.10}
```

## Usage Examples

### Assess Risk with Signals

```python
import requests

# Prepare risk signals
payload = {
    "entity_id": "customer-123",
    "entity_type": "customer",
    "signals": [
        {
            "category": "kyc",
            "score": 0.7,
            "confidence": 0.9,
            "source": "kyc-service",
            "details": {"verification_status": "pending"}
        },
        {
            "category": "transaction",
            "score": 0.5,
            "confidence": 0.8,
            "source": "transaction-service"
        }
    ]
}

# Call API
response = requests.post(
    "http://localhost:8003/api/v1/risk/assess",
    json=payload
)

result = response.json()
print(f"Risk Score: {result['overall_risk_score']}")
print(f"Risk Level: {result['risk_level']}")
```

### Assess Customer Risk

```python
import requests

payload = {
    "customer_id": "customer-123",
    "include_kyc": True,
    "include_transactions": True,
    "include_credit": True,
    "time_window_days": 90
}

response = requests.post(
    "http://localhost:8003/api/v1/risk/customer",
    json=payload
)

result = response.json()
print(f"Overall Risk: {result['overall_risk_score']}")
print(f"KYC Risk: {result['risk_profile']['kyc_risk']}")
print(f"Recommendations: {result['recommendations']}")
```

### Batch Processing

```python
import requests

payload = {
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
    "parallel": True
}

response = requests.post(
    "http://localhost:8003/api/v1/aggregate/batch",
    json=payload
)

result = response.json()
print(f"Processed: {result['successful']}/{result['total_entities']}")
print(f"Average Risk: {result['average_risk_score']}")
```

## Development

### Running Tests
```bash
make test
```

### Code Quality
```bash
# Run linters
make lint

# Format code
make format
```

### Project Structure
```
risk-aggregator/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # API endpoint handlers
│   │       └── router.py       # API router
│   ├── core/                   # Core configuration
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── middleware/             # Custom middleware
│   │   ├── error_handler.py
│   │   └── rate_limiter.py
│   ├── models/                 # Data models
│   │   ├── database.py
│   │   └── schemas.py
│   ├── services/               # Business logic
│   │   ├── aggregation_service.py
│   │   ├── cache_service.py
│   │   ├── data_collector.py
│   │   └── risk_service.py
│   ├── utils/                  # Utility functions
│   │   ├── helpers.py
│   │   └── validators.py
│   └── main.py                 # Application entry point
├── tests/                      # Test files
├── docs/                       # Documentation
├── Dockerfile                  # Production container
├── Dockerfile.dev              # Development container
├── docker-compose.yml          # Docker Compose config
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## API Documentation

When running the application, interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8003/api/v1/docs`
- **ReDoc**: `http://localhost:8003/api/v1/redoc`
- **OpenAPI JSON**: `http://localhost:8003/api/v1/openapi.json`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is part of the Fraud Detection System.

## Support

For issues and questions:
- Create an issue in the repository
- Contact the development team

## Changelog

### Version 1.0.0 (2025-01-25)
- Initial release
- Multi-source risk aggregation
- Batch processing support
- Caching and rate limiting
- Comprehensive API documentation

