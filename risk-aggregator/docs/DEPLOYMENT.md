# Deployment Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker 20.10+ (for containerized deployment)
- Docker Compose 2.0+ (for orchestration)

## Environment Configuration

### Required Environment Variables

```bash
# Application
ENVIRONMENT=production
DEBUG=False
PORT=8003
LOG_LEVEL=INFO

# Security
SECRET_KEY=<generate-secure-key>
API_KEY=<optional-api-key>

# Database
DATABASE_URL=postgresql://user:password@host:5432/fraud_detection

# External Services
ANOMALY_DETECTION_URL=http://anomaly-detection:8002
JAVA_ENGINE_URL=http://java-engine:8080
BACKEND_URL=http://backend:8000

# Performance
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
CACHE_ENABLED=True
CACHE_TTL=300
```

### Generating Secret Keys

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Local Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env

# Run application
uvicorn app.main:app --reload --port 8003
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## Docker Deployment

### Build Image

```bash
# Production image
docker build -t risk-aggregator:latest .

# Development image
docker build -f Dockerfile.dev -t risk-aggregator:dev .
```

### Run Container

```bash
docker run -d \
  --name risk-aggregator \
  -p 8003:8003 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/fraud_detection \
  -e ANOMALY_DETECTION_URL=http://anomaly-detection:8002 \
  risk-aggregator:latest
```

## Docker Compose Deployment

### Configuration

Edit `docker-compose.yml` with your settings.

### Deploy

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f risk-aggregator

# Stop services
docker-compose down

# Restart service
docker-compose restart risk-aggregator
```

## Kubernetes Deployment

### Create ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: risk-aggregator-config
data:
  ENVIRONMENT: "production"
  PORT: "8003"
  LOG_LEVEL: "INFO"
  ANOMALY_DETECTION_URL: "http://anomaly-detection:8002"
  JAVA_ENGINE_URL: "http://java-engine:8080"
```

### Create Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: risk-aggregator-secrets
type: Opaque
stringData:
  SECRET_KEY: "<your-secret-key>"
  DATABASE_URL: "postgresql://user:pass@postgres:5432/fraud_detection"
```

### Create Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: risk-aggregator
  labels:
    app: risk-aggregator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: risk-aggregator
  template:
    metadata:
      labels:
        app: risk-aggregator
    spec:
      containers:
      - name: risk-aggregator
        image: risk-aggregator:latest
        ports:
        - containerPort: 8003
        envFrom:
        - configMapRef:
            name: risk-aggregator-config
        - secretRef:
            name: risk-aggregator-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/health/live
            port: 8003
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health/ready
            port: 8003
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Create Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: risk-aggregator
spec:
  selector:
    app: risk-aggregator
  ports:
  - protocol: TCP
    port: 8003
    targetPort: 8003
  type: ClusterIP
```

### Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods -l app=risk-aggregator
kubectl logs -l app=risk-aggregator -f

# Scale deployment
kubectl scale deployment risk-aggregator --replicas=5
```

## Database Setup

### Initialize Database

```bash
# Using psql
psql -h localhost -U postgres -d fraud_detection -f database/init.sql

# Or using Python
python -c "from app.models.database import init_db; init_db()"
```

### Database Migrations

For production, consider using Alembic for migrations:

```bash
# Install alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

## Monitoring and Logging

### Application Logs

Logs are output to stdout in JSON format (configurable).

View logs:
```bash
# Docker
docker logs -f risk-aggregator

# Kubernetes
kubectl logs -l app=risk-aggregator -f

# Docker Compose
docker-compose logs -f risk-aggregator
```

### Health Checks

Monitor application health:
```bash
# Health check
curl http://localhost:8003/health

# Readiness
curl http://localhost:8003/api/v1/health/ready

# Liveness
curl http://localhost:8003/api/v1/health/live
```

### Metrics

Consider integrating with Prometheus for metrics:

```python
# Add prometheus-fastapi-instrumentator
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## Performance Tuning

### Uvicorn Workers

For production, use multiple workers:

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8003 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker
```

### Gunicorn with Uvicorn Workers

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8003 \
  --access-logfile - \
  --error-logfile -
```

### Environment-Specific Settings

Production recommendations:
- `DEBUG=False`
- `LOG_LEVEL=INFO`
- `ENABLE_DOCS=False` (disable in production)
- Use proper SECRET_KEY
- Enable rate limiting
- Configure appropriate cache TTL

## Backup and Recovery

### Database Backup

```bash
# Backup
pg_dump -h localhost -U postgres fraud_detection > backup.sql

# Restore
psql -h localhost -U postgres fraud_detection < backup.sql
```

### Application State

Cache is in-memory and ephemeral. For persistent cache, consider Redis.

## Security Considerations

1. **API Keys**: Use strong API keys in production
2. **HTTPS**: Always use HTTPS in production
3. **CORS**: Configure ALLOWED_ORIGINS properly
4. **Rate Limiting**: Enable and configure appropriately
5. **Database**: Use SSL for database connections
6. **Secrets**: Use secret management (Vault, K8s secrets)
7. **Network**: Use private networks for service communication

## Troubleshooting

### Common Issues

1. **Connection refused**
   - Check service is running
   - Verify port configuration
   - Check firewall rules

2. **Database connection errors**
   - Verify DATABASE_URL
   - Check database is running
   - Verify credentials

3. **High response times**
   - Check cache configuration
   - Review database indexes
   - Monitor external service latency

4. **Memory issues**
   - Adjust worker count
   - Review cache size
   - Check for memory leaks

### Debug Mode

Enable debug mode for troubleshooting:
```bash
DEBUG=True LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

## Rollback Procedures

### Docker

```bash
# Tag previous version
docker tag risk-aggregator:latest risk-aggregator:rollback

# Deploy new version
docker build -t risk-aggregator:latest .

# If issues, rollback
docker tag risk-aggregator:rollback risk-aggregator:latest
docker-compose restart risk-aggregator
```

### Kubernetes

```bash
# Rollback to previous version
kubectl rollout undo deployment/risk-aggregator

# Rollback to specific revision
kubectl rollout undo deployment/risk-aggregator --to-revision=2

# Check rollout status
kubectl rollout status deployment/risk-aggregator
```

