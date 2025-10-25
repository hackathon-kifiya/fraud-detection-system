# KYC & Transaction Anomaly Detection API

A FastAPI-based microservice for detecting anomalies in KYC (Know Your Customer) data and financial transactions using Isolation Forest and SHAP explainability.

## 🚀 Features

- **Dual Anomaly Detection**: Separate models for KYC profiles and transactions
- **Isolation Forest**: Unsupervised machine learning for anomaly detection
- **SHAP Explanations**: Interpretable AI with feature importance explanations
- **Batch Processing**: Process multiple records at once
- **RESTful API**: Well-documented FastAPI endpoints
- **Rate Limiting**: Built-in request throttling
- **Docker Support**: Ready for containerized deployment
- **Comprehensive Testing**: Unit and integration tests with pytest

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Model Training](#model-training)
- [Testing](#testing)
- [Project Structure](#project-structure)

## 🔧 Installation

### Prerequisites

- Python 3.11+
- pip or poetry
- Docker (optional)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/kyc-anomaly-detection.git
cd kyc-anomaly-detection

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration
```

## 🏃 Quick Start

### Run Locally

```bash
# Start the server
python -m app.main

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs


## 📚 API Documentation

### Endpoints

#### KYC Endpoints

- `POST /api/v1/kyc/check` - Check single KYC record
- `POST /api/v1/kyc/batch` - Batch check multiple KYC records
- `GET /api/v1/kyc/stats` - Get KYC model statistics

#### Transaction Endpoints

- `POST /api/v1/transaction/check` - Check single transaction
- `POST /api/v1/transaction/batch` - Batch check multiple transactions
- `GET /api/v1/transaction/stats` - Get transaction model statistics

#### Health & Info

- `GET /` - API information
- `GET /health` - Health check endpoint


## 🐳 Docker Deployment

### Build and Run

```bash
# Build the image
docker build -f docker/Dockerfile -t kyc-anomaly-api .

# Run the container
docker run -d -p 8000:8000 --name kyc-api kyc-anomaly-api

# Or use docker-compose
cd docker
docker-compose up -d
```

### Docker Compose Services

The compose file includes:
- **API Service**: FastAPI application
- **PostgreSQL** (optional): Database for storing results
- **Redis** (optional): Caching and rate limiting

## ⚙️ Configuration

Configuration is managed through environment variables. Key settings:

```bash
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Model Parameters
CONTAMINATION=0.1
N_ESTIMATORS=100
HIGH_RISK_THRESHOLD=-0.3
MEDIUM_RISK_THRESHOLD=-0.1
```

See `.env.example` for all available options.

## 🧠 Model Training

### Using Synthetic Data (Default)

The service automatically generates synthetic training data on startup if models don't exist.

### Training with Real Data

```bash
# Prepare your training data
python scripts/generate_synthetic_data.py

# Train models  
python scripts/train_models.py

# Evaluate models
python scripts/evaluate_models.py
```

### Model Files

Trained models are saved in `data/models/`:
- `kyc_model.pkl` - KYC Isolation Forest model
- `transaction_model.pkl` - Transaction Isolation Forest model
- `kyc_scaler.pkl` - KYC feature scaler
- `transaction_scaler.pkl` - Transaction feature scaler



## 📁 Project Structure

```
kyc-anomaly-detection/
├── app/                        # Application code
│   ├── api/                    # API routes
│   │   └── v1/                 # API version 1
│   │       ├── endpoints/      # Endpoint implementations
│   │       └── router.py       # Router configuration
│   ├── core/                   # Core functionality
│   │   ├── config.py           # Configuration
│   │   ├── logging.py          # Logging setup
│   │   └── security.py         # Security utilities
│   ├── models/                 # Data models
│   │   └── schemas.py          # Pydantic schemas
│   ├── services/               # Business logic
│   │   ├── anomaly_detector.py # Anomaly detection service
│   │   └── explainer.py        # SHAP explainer
│   ├── middleware/             # Middleware
│   │   ├── error_handler.py    # Error handling
│   │   └── rate_limiter.py     # Rate limiting
│   └── main.py                 # Application entry point
├── tests/                      # Test suite
├── data/                       # Data directory
│   ├── models/                 # Saved models
│   ├── raw/                    # Raw training data
│   └── processed/              # Processed data
├── docker/                     # Docker files
├── scripts/                    # Utility scripts
├── notebooks/                  # Jupyter notebooks
├── docs/                       # Documentation
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
└── README.md                   # This file
```

## 🔒 Security Considerations

- **API Keys**: Enable API key authentication in production
- **Rate Limiting**: Protect against abuse with rate limiting
- **HTTPS**: Always use HTTPS in production
- **Input Validation**: All inputs are validated with Pydantic
