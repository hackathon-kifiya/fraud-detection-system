# Data Management Service

Single source of truth for data type definitions across all fraud detection services.

## Purpose

This service manages data type schemas that are used by:
- Backend Service
- Rule Engine
- Decision Service
- Future services

## Architecture

The service provides a centralized location for data type definitions, eliminating:
- Data duplication across services
- Sync complexity and failures
- Schema inconsistencies
- Maintenance overhead

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Data Types
- `GET /data-types` - List all data types
- `GET /data-types/{data_type}` - Get specific data type
- `POST /data-types` - Create new data type
- `PUT /data-types/{data_type}` - Update data type
- `DELETE /data-types/{data_type}` - Delete data type

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Server port (default: 5004)

## Usage

Other services should fetch data type definitions from this service rather than maintaining their own copies.

## Development

```bash
pip install -r requirements.txt
python main.py
```

## Docker

```bash
docker build -t data-management-service .
docker run -p 5004:5004 data-management-service
```

