"""
API endpoint tests.
"""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Risk Aggregator Service"
    assert data["status"] == "running"


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "risk-aggregator"


def test_health_check_v1(client: TestClient):
    """Test v1 health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_readiness_check(client: TestClient):
    """Test readiness check endpoint."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_liveness_check(client: TestClient):
    """Test liveness check endpoint."""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


def test_assess_risk(client: TestClient, sample_risk_assessment_request):
    """Test risk assessment endpoint."""
    response = client.post(
        "/api/v1/risk/assess",
        json=sample_risk_assessment_request
    )
    assert response.status_code == 200
    data = response.json()
    assert "overall_risk_score" in data
    assert "risk_level" in data
    assert "components" in data
    assert data["entity_id"] == sample_risk_assessment_request["entity_id"]


def test_get_risk_weights(client: TestClient):
    """Test get risk weights endpoint."""
    response = client.get("/api/v1/aggregate/weights")
    assert response.status_code == 200
    data = response.json()
    assert "weights" in data

