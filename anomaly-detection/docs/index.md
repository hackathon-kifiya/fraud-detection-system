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

## 📋 Quick Links

- [API Documentation](api_documentation.md) - Complete API reference
- [Model Documentation](model_documentation.md) - ML models and training
- [Security Features](security_features.md) - Security implementation
- [Deployment Guide](deployment_guide.md) - Production deployment

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
- **Documentation Site**: http://localhost:8001 (run `make docs-serve`)

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

## 🧠 Model Training

### Using Make Commands

```bash
# Generate synthetic training data
make generate-data

# Train all models
make train-models

# Evaluate models
make evaluate-all

# Run complete demo
make demo
```

## 📁 Project Structure

```
kyc-anomaly-detection/
├── app/                        # Application code
│   ├── api/                    # API routes
│   ├── core/                   # Core functionality
│   ├── models/                 # Data models
│   ├── services/               # Business logic
│   ├── middleware/             # Middleware
│   └── main.py                 # Application entry point
├── tests/                      # Test suite
├── data/                       # Data directory
├── docker/                     # Docker files
├── scripts/                    # Utility scripts
├── notebooks/                  # Jupyter notebooks
├── docs/                       # Documentation
└── requirements.txt            # Dependencies
```

## 🔒 Security

- **API Keys**: Enable API key authentication in production
- **Rate Limiting**: Protect against abuse
- **HTTPS**: Always use HTTPS in production
- **Input Validation**: All inputs validated with Pydantic

See [Security Features](security_features.md) for details.

## 📞 Support

For issues and questions:

- Check the documentation pages
- Review the API docs at http://localhost:8000/docs
- Open an issue on GitHub

