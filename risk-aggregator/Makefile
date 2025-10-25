.PHONY: help install dev-install test lint format clean run docker-build docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make dev-install   - Install development dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean temporary files"
	@echo "  make run           - Run application locally"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

lint:
	flake8 app/ tests/
	mypy app/
	pylint app/

format:
	black app/ tests/
	isort app/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

docker-build:
	docker build -t risk-aggregator:latest .

docker-build-dev:
	docker build -f Dockerfile.dev -t risk-aggregator:dev .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f risk-aggregator

docker-restart:
	docker-compose restart risk-aggregator

docker-shell:
	docker-compose exec risk-aggregator /bin/bash

