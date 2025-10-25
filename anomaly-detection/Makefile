.PHONY: help install install-dev test run docker-build docker-run clean lint format

help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make run           - Run the application"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean generated files"
	@echo "  make generate-data - Generate synthetic training data"
	@echo "  make train-models  - Train all ML models"
	@echo "  make train-kyc     - Train KYC model only"
	@echo "  make train-business - Train Business model only"
	@echo "  make train-transaction - Train Transaction model only"
	@echo "  make train-combined - Train Combined model only"
	@echo "  make train-customer - Train Customer model only"
	@echo "  make evaluate-all  - Evaluate all models"
	@echo "  make setup-dev     - Setup complete development environment"
	@echo "  make demo          - Run complete demo (generate + train + evaluate)"
	@echo "  make docs-serve    - Serve documentation locally"
	@echo "  make docs-build    - Build documentation site"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=app --cov-report=html --cov-report=term

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -f docker/Dockerfile -t kyc-anomaly-api:latest .

docker-run:
	docker run -d -p 8000:8000 --name kyc-api kyc-anomaly-api:latest

docker-compose-up:
	cd docker && docker-compose up -d

docker-compose-down:
	cd docker && docker-compose down

lint:
	flake8 app/ scripts/
	pylint app/
	mypy app/

format:
	black app/  scripts/
	isort app/ scripts/

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
	python scripts/generate_synthetic_data.py --kyc-samples 8999 --transaction-samples 8999 --anomaly-fraction 0.1

generate-data-large:
	@echo "Generating large synthetic dataset..."
	python scripts/generate_synthetic_data.py --kyc-samples 100000 --transaction-samples 500000 --anomaly-fraction 0.1

train-models:
	@echo "Training all models..."
	python scripts/train_models.py

train-kyc:
	@echo "Training KYC model..."
	python scripts/train_models.py --train-kyc --kyc-data data/raw/kyc_training_data.csv

train-business:
	@echo "Training Business model..."
	python scripts/train_models.py --train-business --business-data data/raw/business_training_data.csv

train-transaction:
	@echo "Training Transaction model..."
	python scripts/train_models.py --train-transaction --transaction-data data/raw/transaction_training_data.csv

train-combined:
	@echo "Training Combined KYC+Business model..."
	python scripts/train_models.py --train-merged --merged-data data/raw/kyc_business_training_data.csv

train-customer:
	@echo "Training Customer model..."
	python scripts/train_models.py --train-customer --transaction-data data/raw/transaction_training_data.csv

evaluate-all:
	@echo "Evaluating all models..."
	python scripts/evaluate_models.py --model-type all

evaluate-kyc:
	@echo "Evaluating KYC model..."
	python scripts/evaluate_models.py --model-type kyc --test-data data/raw/kyc_training_data.csv

evaluate-business:
	@echo "Evaluating Business model..."
	python scripts/evaluate_models.py --model-type business --test-data data/raw/business_training_data.csv

evaluate-transaction:
	@echo "Evaluating Transaction model..."
	python scripts/evaluate_models.py --model-type transaction --test-data data/raw/transaction_training_data.csv

evaluate-combined:
	@echo "Evaluating Combined model..."
	python scripts/evaluate_models.py --model-type combined --test-data data/raw/kyc_business_training_data.csv

evaluate-customer:
	@echo "Evaluating Customer model..."
	python scripts/evaluate_models.py --model-type customer --test-data data/raw/transaction_training_data.csv

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
	python scripts/generate_synthetic_data.py --kyc-samples 1000 --transaction-samples 5000
	python scripts/train_models.py
	@echo "✓ Quick start complete! Run 'make run' to start the API"

docs-serve:
	@echo "Starting documentation server..."
	@echo "Documentation will be available at http://localhost:8001"
	mkdocs serve -a localhost:8001

docs-build:
	@echo "Building documentation site..."
	mkdocs build
	@echo "✓ Documentation built in site/ directory"