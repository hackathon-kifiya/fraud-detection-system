.PHONY: help install install-dev test run docker-build docker-run clean lint format

help:
	@echo "Available commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make setup-dev     - Setup complete development environment"
	@echo ""
	@echo "Development:"
	@echo "  make run           - Run the application"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean generated files"
	@echo ""
	@echo "Data & Training:"
	@echo "  make generate-data      - Generate synthetic training data"
	@echo "  make train-models       - Train all models (supervised + unsupervised)"
	@echo "  make train-unsupervised - Train unsupervised models (Isolation Forest)"
	@echo "  make train-supervised   - Train supervised models (Random Forest)"
	@echo "  make train-transaction  - Train Transaction model only"
	@echo "  make train-merged       - Train Merged (KYC+Business) model only"
	@echo "  make train-customer     - Train Customer model only"
	@echo "  make evaluate-all       - Evaluate all models"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build          - Build production Docker image"
	@echo "  make docker-build-dev      - Build development Docker image"
	@echo "  make docker-run            - Run production container"
	@echo "  make docker-run-dev        - Run development container (hot reload)"
	@echo "  make docker-compose-up    - Start services with docker-compose"
	@echo "  make docker-compose-up-dev - Start development environment"
	@echo "  make docker-compose-down  - Stop docker-compose"
	@echo "  make docker-compose-logs  - Show API logs"
	@echo "  make docker-clean         - Clean Docker images and containers"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs-serve    - Serve documentation locally"
	@echo "  make docs-build    - Build documentation site"
	@echo ""
	@echo "Workflows:"
	@echo "  make demo          - Run complete demo (generate + train + evaluate)"
	@echo "  make quick-start   - Quick start with small dataset"

install:
	.venv/bin/pip install -r requirements.txt

install-dev:
	.venv/bin/pip install -r requirements-dev.txt

test:
	.venv/bin/pytest tests/ -v

test-cov:
	.venv/bin/pytest tests/ --cov=app --cov-report=html --cov-report=term

run:
	.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	@echo "Building production Docker image..."
	docker build -f docker/Dockerfile -t anomaly-detection-api:latest .

docker-build-dev:
	@echo "Building development Docker image..."
	docker build -f docker/Dockerfile.dev -t anomaly-detection-api:dev .

docker-run:
	@echo "Running production container..."
	docker run -d -p 8000:8000 --name anomaly-api anomaly-detection-api:latest

docker-run-dev:
	@echo "Running development container with hot reload..."
	docker run -d -p 8001:8000 -v $(PWD):/app --name anomaly-api-dev anomaly-detection-api:dev

docker-compose-up:
	@echo "Starting services with docker-compose..."
	cd docker && docker-compose up -d

docker-compose-up-dev:
	@echo "Starting development environment..."
	cd docker && docker-compose --profile dev up -d api-dev

docker-compose-down:
	@echo "Stopping docker-compose services..."
	cd docker && docker-compose down

docker-compose-logs:
	@echo "Showing docker-compose logs..."
	cd docker && docker-compose logs -f api

docker-clean:
	@echo "Cleaning Docker images and containers..."
	docker-compose -f docker/docker-compose.yml down
	docker rmi anomaly-detection-api:latest anomaly-detection-api:dev 2>/dev/null || true

lint:
	.venv/bin/flake8 app/ scripts/
	.venv/bin/pylint app/
	.venv/bin/mypy app/

format:
	.venv/bin/black app/  scripts/
	.venv/bin/isort app/ scripts/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf outputs/*.png
	rm -rf outputs/*.json

generate-data:
	@echo "Generating synthetic training data..."
	.venv/bin/python scripts/generate_synthetic_data.py --samples 8999 --anomaly-fraction 0.1

generate-data-large:
	@echo "Generating large synthetic dataset..."
	.venv/bin/python scripts/generate_synthetic_data.py --kyc-samples 100000 --transaction-samples 500000 --anomaly-fraction 0.1

train-models:
	@echo "Training all models (supervised + unsupervised)..."
	@.venv/bin/python -m app.ml.training --mode all

train-unsupervised:
	@echo "Training unsupervised models (Isolation Forest)..."
	@.venv/bin/python -m app.ml.training --mode unsupervised

train-supervised:
	@echo "Training supervised models (Random Forest)..."
	@.venv/bin/python -m app.ml.training --mode supervised

train-transaction:
	@echo "Training Transaction model (unsupervised)..."
	@.venv/bin/python -m app.ml.training --mode unsupervised --model transaction

train-merged:
	@echo "Training Merged KYC+Business model (unsupervised)..."
	@.venv/bin/python -m app.ml.training --mode unsupervised --model merged

train-customer:
	@echo "Training Customer model (unsupervised)..."
	@.venv/bin/python -m app.ml.training --mode unsupervised --model customer

# Legacy targets (deprecated - kept for backwards compatibility)
train-kyc:
	@echo "⚠️  DEPRECATED: Use 'make train-unsupervised' instead"
	@echo "Training all unsupervised models..."
	python -m app.ml.training --mode unsupervised

train-business:
	@echo "⚠️  DEPRECATED: Business model is part of merged model"
	@echo "Training merged model..."
	python -m app.ml.training --mode unsupervised --model merged

train-combined:
	@echo "⚠️  DEPRECATED: Use 'make train-merged' instead"
	@echo "Training merged model..."
	python -m app.ml.training --mode unsupervised --model merged

evaluate-all:
	@echo "Evaluating all models..."
	.venv/bin/python scripts/evaluate_models.py --model-type all

evaluate-kyc:
	@echo "Evaluating KYC model..."
	.venv/bin/python scripts/evaluate_models.py --model-type kyc --test-data data/raw/kyc_training_data.csv

evaluate-business:
	@echo "Evaluating Business model..."
	.venv/bin/python scripts/evaluate_models.py --model-type business --test-data data/raw/business_training_data.csv

evaluate-transaction:
	@echo "Evaluating Transaction model..."
	.venv/bin/python scripts/evaluate_models.py --model-type transaction --test-data data/raw/transaction_training_data.csv

evaluate-combined:
	@echo "Evaluating Combined model..."
	.venv/bin/python scripts/evaluate_models.py --model-type combined --test-data data/raw/kyc_business_training_data.csv

evaluate-customer:
	@echo "Evaluating Customer model..."
	.venv/bin/python scripts/evaluate_models.py --model-type customer --test-data data/raw/transaction_training_data.csv

setup-dev:
	@echo "Setting up development environment..."
	make install-dev
	cp .env.example .env
	mkdir -p data/models data/raw data/processed outputs
	@echo "✓ Development environment setup complete!"
	@echo "Edit .env file with your configuration"
	@echo "Run 'make demo' to generate data, train models, and evaluate"

demo:
	@echo "=========================================="
	@echo "Running Complete Demo"
	@echo "=========================================="
	@echo ""
	@echo "[1/3] Generating synthetic data..."
	make generate-data
	@echo ""
	@echo "[2/3] Training all models..."
	make train-models
	@echo ""
	@echo "[3/3] Evaluating all models..."
	make evaluate-all
	@echo ""
	@echo "=========================================="
	@echo "Demo Complete!"
	@echo "=========================================="
	@echo "Check outputs/ for evaluation results"
	@echo "Start API with: make run"

quick-start:
	@echo "Quick Start - Small Dataset"
	.venv/bin/python scripts/generate_synthetic_data.py --kyc-samples 1000 --transaction-samples 5000
	.venv/bin/python -m app.ml.training --mode unsupervised
	@echo "✓ Quick start complete! Run 'make run' to start the API"

docs-serve:
	@echo "Starting documentation server..."
	@echo "Documentation will be available at http://localhost:8001"
	mkdocs serve -a localhost:8001

docs-build:
	@echo "Building documentation site..."
	mkdocs build
	@echo "✓ Documentation built in site/ directory"