"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_risk_signals():
    """Sample risk signals for testing."""
    return [
        {
            "category": "kyc",
            "score": 0.7,
            "confidence": 0.9,
            "source": "test-kyc",
            "details": {"status": "verified"},
        },
        {
            "category": "transaction",
            "score": 0.5,
            "confidence": 0.8,
            "source": "test-transaction",
        },
    ]


@pytest.fixture
def sample_risk_assessment_request(sample_risk_signals):
    """Sample risk assessment request."""
    return {
        "entity_id": "test-entity-123",
        "entity_type": "customer",
        "signals": sample_risk_signals,
    }


@pytest.fixture
def sample_customer_risk_request():
    """Sample customer risk request."""
    return {
        "customer_id": "test-customer-123",
        "include_kyc": True,
        "include_transactions": True,
        "include_credit": True,
        "time_window_days": 90,
    }

