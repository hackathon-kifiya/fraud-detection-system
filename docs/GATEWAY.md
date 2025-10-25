# Traefik API Gateway Documentation

## Overview

This document describes the Traefik API Gateway implementation for the fraud detection system. The gateway provides a unified entry point for all microservices with built-in rate limiting, health checks, load balancing, and monitoring capabilities.

## Architecture

```
                    ┌─────────────────┐
                    │   Traefik       │
                    │  API Gateway    │
                    │  :80 / :8080    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐       ┌─────▼──────┐      ┌─────▼──────┐
   │ Frontend │       │Rule Engine │      │  Anomaly   │
   │  :3000   │       │   :8081    │      │   :5001    │
   └──────────┘       └────────────┘      └────────────┘
                             │
                      ┌──────▼──────┐      ┌─────▼──────┐
                      │ Prediction  │      │    Risk    │
                      │   :5002     │      │   :5003    │
                      └─────────────┘      └────────────┘
                             │                    │
        ┌────────────────────┼────────────────────┘
        │                    │
   ┌────▼─────┐              │
   │ Backend  │              │
   │   :8080  │              │
   └──────────┘              │
        │                    │
        └────────────────────┘
```

## Service Routing

| Path | Target Service | Internal URL | Features | Access |
|------|---------------|--------------|----------|---------|
| `/api/backend/*` | Backend | `http://backend:8080` | Strip prefix, health check | Frontend |
| `/api/users/*` | Backend | `http://backend:8080` | Strip prefix, health check | Frontend |
| `/api/auth/*` | Backend | `http://backend:8080` | Strip prefix, health check | Frontend |
| `/api/admin/*` | Backend | `http://backend:8080` | Strip prefix, health check | Frontend |
| `/api/audit/*` | Backend | `http://backend:8080` | Strip prefix, health check | Frontend |
| `/api/flagged-items/*` | Backend | `http://backend:8080` | Strip prefix, health check | Frontend |
| `/api/rules/*` | Rule Engine | `http://rule-engine:8081` | Strip prefix, health check | Frontend |
| `/api/evaluate/*` | Rule Engine | `http://rule-engine:8081` | Strip prefix, health check | Frontend |
| `/api/anomaly/*` | Anomaly Engine | `http://anomaly-detection-engine:5001` | Strip prefix, health check | Frontend |
| `/api/predict/*` | Prediction Engine | `http://prediction-engine:5002` | Strip prefix, health check | Frontend |
| `/api/risk/*` | Risk Aggregation | `http://risk-aggregation-engine:5003` | Strip prefix, health check | Frontend |
| `/health` | Backend | `http://backend:8080/health` | Health check | Frontend |
| `/*` | Frontend | `http://frontend:3000` | Static files | Browser |

### Direct Service Communication (Backend → Other Services)
| Service | Internal URL | Purpose |
|---------|--------------|---------|
| Rule Engine | `http://rule-engine:8081` | Rule evaluation for internal processing |
| Anomaly Detection | `http://anomaly-detection-engine:5001` | Anomaly analysis for internal processing |
| Prediction Engine | `http://prediction-engine:5002` | Fraud prediction for internal processing |
| Risk Aggregation | `http://risk-aggregation-engine:5003` | Risk scoring for internal processing |

## Configuration

### Static Configuration (`traefik/traefik.yml`)

- **Entry Points**: 
  - `web`: Port 80 (main gateway)
  - `dashboard`: Port 8080 (monitoring)
- **Providers**: Docker auto-discovery + file-based dynamic config
- **Logging**: JSON format access logs
- **Metrics**: Prometheus metrics enabled
- **Health Check**: Ping endpoint for gateway health

### Dynamic Configuration (`traefik/dynamic.yml`)

- **Error Pages**: Custom error handling
- **Middleware**: Rate limiting, CORS, compression, circuit breakers

## Middleware

### Rate Limiting
- **Limit**: 100 requests per minute per IP
- **Burst**: 50 additional requests
- **Scope**: Per IP address

### CORS
- **Origins**: `http://localhost:3001`, `http://localhost`
- **Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: Content-Type, Authorization, X-Requested-With
- **Credentials**: Enabled

### Circuit Breaker
- **Trigger**: 50% error rate
- **Expression**: `NetworkErrorRatio() > 0.5`

### Retry
- **Attempts**: 3 retries
- **Initial Interval**: 100ms
- **Max Interval**: 1s
- **Multiplier**: 2 (exponential backoff)

### Compression
- **Type**: Gzip compression for all responses

## Health Checks

All services expose `/health` endpoints:

- **Backend**: `http://backend:8080/health`
- **Rule Engine**: `http://rule-engine:8080/health`
- **Anomaly Detection**: `http://anomaly-detection-engine:5001/health`

Health checks run every 30 seconds and are used for:
- Load balancer health status
- Circuit breaker decisions
- Service discovery

## Monitoring Dashboard

Access the Traefik dashboard at: `http://localhost:8080/dashboard/`

### Dashboard Features
- **Real-time routing table**
- **Service health status**
- **Request metrics and statistics**
- **Middleware configuration**
- **Error rates and response times**

## Service Communication

### Frontend → Gateway → All Services
- **URL**: `http://localhost` (port 80)
- **All API calls** go through Traefik gateway
- **Direct access** to all microservices via gateway
- **CORS** handled by gateway

### Backend → Other Services (Direct)
- **Rule Engine**: `http://rule-engine:8081`
- **Anomaly Detection**: `http://anomaly-detection-engine:5001`
- **Prediction Engine**: `http://prediction-engine:5002`
- **Risk Aggregation**: `http://risk-aggregation-engine:5003`

### Service Communication Flow
1. **Frontend** → **Traefik Gateway** → **Backend** (for core business logic)
2. **Frontend** → **Traefik Gateway** → **Rule Engine** (for rule management/evaluation)
3. **Frontend** → **Traefik Gateway** → **Anomaly Detection** (for anomaly analysis)
4. **Frontend** → **Traefik Gateway** → **Prediction Engine** (for fraud prediction)
5. **Frontend** → **Traefik Gateway** → **Risk Aggregation** (for risk scoring)
6. **Backend** → **Other Services** (direct communication for internal processing)

## Deployment

### Start Services
```bash
docker-compose up -d
```

### Check Status
```bash
# Check all services
docker-compose ps

# Check Traefik logs
docker-compose logs traefik

# Check specific service logs
docker-compose logs backend
```

### Access Points
- **Application**: `http://localhost`
- **Dashboard**: `http://localhost:8080/dashboard/`
- **Health Check**: `http://localhost/health`

## Testing

### Basic Connectivity
```bash
# Test health endpoint
curl http://localhost/health

# Test API endpoint
curl http://localhost/api/users

# Test rule engine
curl http://localhost/api/rules
```

### Rate Limiting Test
```bash
# Send multiple requests to test rate limiting
for i in {1..150}; do curl -s http://localhost/health; done
```

### Service Health
```bash
# Check service health in dashboard
curl http://localhost:8080/api/http/services
```

## Troubleshooting

### Common Issues

1. **Service Not Found (404)**
   - Check if service is running: `docker-compose ps`
   - Verify Traefik labels are correct
   - Check service logs: `docker-compose logs <service>`

2. **Rate Limited (429)**
   - Wait for rate limit window to reset (1 minute)
   - Check rate limit configuration in `traefik.yml`

3. **CORS Errors**
   - Verify frontend URL is in CORS origins
   - Check browser developer tools for CORS headers

4. **Health Check Failures**
   - Ensure service has `/health` endpoint
   - Check service is responding on correct port
   - Verify health check path in service labels

### Debug Commands

```bash
# Check Traefik configuration
docker-compose exec traefik traefik version

# View Traefik logs
docker-compose logs -f traefik

# Check service discovery
curl http://localhost:8080/api/http/services

# Test specific route
curl -v http://localhost/api/rules
```

### Log Locations

- **Traefik Logs**: `/var/log/traefik/traefik.log`
- **Access Logs**: `/var/log/traefik/access.log`
- **Docker Logs**: `docker-compose logs <service>`

## Security Considerations

1. **Rate Limiting**: Prevents DoS attacks and abuse
2. **CORS**: Restricts cross-origin requests
3. **Circuit Breaker**: Prevents cascade failures
4. **Health Checks**: Ensures only healthy services receive traffic
5. **Internal Network**: Services communicate via Docker network

## Performance

- **Gateway Overhead**: ~1-2ms per request
- **Memory Usage**: ~50MB for Traefik container
- **Throughput**: Handles thousands of requests per second
- **Latency**: Minimal impact on response times

## Scaling

To scale services:

```bash
# Scale backend service
docker-compose up -d --scale backend=3

# Scale rule engine
docker-compose up -d --scale rule-engine=2
```

Traefik automatically load balances across scaled instances.

## Maintenance

### Update Configuration
1. Edit `traefik/traefik.yml` or `traefik/dynamic.yml`
2. Restart Traefik: `docker-compose restart traefik`

### Add New Service
1. Add service to `docker-compose.yml`
2. Add Traefik labels for routing
3. Deploy: `docker-compose up -d`

### Monitor Performance
- Use dashboard at `http://localhost:8080/dashboard/`
- Check Prometheus metrics
- Monitor access logs for patterns
