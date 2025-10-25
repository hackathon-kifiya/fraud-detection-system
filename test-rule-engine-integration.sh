#!/bin/bash

# Test script for rule engine integration
echo "Testing Rule Engine Integration..."

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Test rule engine health
echo "Testing rule engine health..."
curl -f http://localhost:8082/health || echo "Rule engine not ready"

# Test backend health
echo "Testing backend health..."
curl -f http://localhost:8081/health || echo "Backend not ready"

# Test rule engine evaluation endpoint
echo "Testing rule engine evaluation..."
curl -X POST http://localhost:8082/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "dataType": "transaction",
    "facts": [{
      "entityId": "test-123",
      "amount": 1500.0,
      "accountBalance": 500.0,
      "type": "debit",
      "paymentMethod": "card"
    }]
  }' || echo "Rule engine evaluation failed"

# Test backend rule evaluation endpoint
echo "Testing backend rule evaluation..."
curl -X POST http://localhost:8081/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "dataType": "transaction",
    "data": [{
      "entityId": "test-456",
      "amount": 2000.0,
      "accountBalance": 300.0,
      "type": "debit",
      "paymentMethod": "card"
    }]
  }' || echo "Backend rule evaluation failed"

# Test custom data type
echo "Testing custom data type evaluation..."
curl -X POST http://localhost:8081/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "dataType": "payment",
    "data": [{
      "entityId": "payment-789",
      "amount": 5000.0,
      "status": "active",
      "timestamp": "2023-12-01T10:00:00Z"
    }]
  }' || echo "Custom data type evaluation failed"

echo "Integration test completed!"
