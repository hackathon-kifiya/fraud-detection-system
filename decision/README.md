# Decision Service

Configurable decision service that aggregates scores from rule engine, anomaly detection, and predictive engine to make fraud detection decisions.

## Features

- **Configurable Weight Distribution**: Manually set weights for each engine (must sum to 100)
- **Decision Thresholds**: Configure auto-approve and auto-reject thresholds
- **Weighted Score Calculation**: Combines three engine scores using configured weights
- **Clean Architecture**: Domain-driven design with separation of concerns

## API Documentation

### Swagger UI

The service exposes interactive API documentation via Swagger UI:

- **Swagger UI**: http://localhost:5003/docs
- **ReDoc**: http://localhost:5003/redoc
- **OpenAPI Schema**: http://localhost:5003/openapi.json

### Endpoints

#### Health Check
- `GET /health` - Check service health

#### Configuration
- `GET /config` - Get current configuration
- `POST /config` - Update configuration

#### Decision
- `POST /decide` - Make a decision based on engine scores

### Example Request

```json
POST /decide
{
  "entity_id": "txn_123456",
  "rule_engine_score": 0.4,
  "anomaly_detection_score": 0.6,
  "predictive_engine_score": 0.3
}
```

### Example Response

```json
{
  "entity_id": "txn_123456",
  "final_score": 0.445,
  "final_score_percent": 44.5,
  "decision": "HUMAN_REVIEW",
  "breakdown": {
    "rule_engine": {
      "score": 0.4,
      "weight": 40.0,
      "contribution": 16.0
    },
    "anomaly_detection": {
      "score": 0.6,
      "weight": 35.0,
      "contribution": 21.0
    },
    "predictive_engine": {
      "score": 0.3,
      "weight": 25.0,
      "contribution": 7.5
    }
  },
  "confidence": 0.5
}
```

## Configuration

The service uses a PostgreSQL database to store configuration. Default configuration:

- `auto_approve_threshold`: 25.0
- `auto_reject_threshold`: 85.0
- `rule_engine_weight`: 40.0
- `anomaly_detection_weight`: 35.0
- `predictive_engine_weight`: 25.0

**Validation Rules:**
- Weights must sum to 100
- `auto_approve_threshold` must be less than `auto_reject_threshold`
- All values must be between 0 and 100

## Running the Service

```bash
# Build Docker image
docker build -t decision-service .

# Run with docker-compose
docker-compose up decision-service

# Or run directly
python main.py
```

The service runs on port 5003 by default.

## Architecture

The service follows clean architecture principles:

```
decision/
├── domain/           # Domain models and interfaces
│   ├── models.py
│   └── repository.py
├── usecases/         # Business logic
│   └── decision_service.py
├── adapters/         # External adapters
│   ├── database/
│   └── api/
└── main.py          # Application entry point
```

### Layers

1. **Domain Layer**: Core business models and repository interfaces
2. **Use Cases Layer**: Business logic for decisions and configuration
3. **Adapters Layer**: Database and API implementations
4. **Interface Layer**: FastAPI application setup

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn main:app --reload --port 5003
```

