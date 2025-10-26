"""
Pytest Configuration and Shared Fixtures

This file provides shared fixtures for all tests across the test suite.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any

from app.models.schemas import (
    KYCData,
    TransactionData,
    CombinedKYCBusinessData,
    RiskLevel,
)


@pytest.fixture
def sample_kyc_data() -> Dict[str, Any]:
    """Sample KYC data for testing"""
    return {
        "customer_id": "CUST_TEST_001",
        "customer_name": "Test Customer",
        "customer_phone_number": 9123456789,
        "customer_age": 35,
        "customer_gender": "male",
        "customer_marital_status": "married",
        "customer_education_level": "primary",
        "customer_tin_number": "1234567890",
        "customer_bank_account_number": "1234567890123",
        "customer_region": "ADDIS_ABABA",
        "customer_city": "ADDIS_ABABA",
        "customer_zone_or_sub_city": "ZONE_1",
        "customer_woreda": "01",
        "customerId": "CUST_TEST_001",
    }


@pytest.fixture
def sample_transaction_data() -> Dict[str, Any]:
    """Sample transaction data for testing"""
    return {
        "customer_id": "CUST_TEST_001",
        "date": "2024-10-25T14:30:00",
        "credit": 1000.0,
        "debit": 0.0,
        "closingBalance": 5000.0,
        "narrative": "Cash Deposit BY SELF",
        "source": "CASH DEPOSIT",
        "is_anomaly": 0,
    }


@pytest.fixture
def sample_combined_data() -> Dict[str, Any]:
    """Sample combined KYC+Business data for testing"""
    return {
        # KYC fields
        "customer_id": "CUST_TEST_001",
        "customer_name": "Test Customer",
        "customer_phone_number": 9123456789,
        "customer_age": 35,
        "customer_gender": "male",
        "customer_marital_status": "married",
        "customer_education_level": "primary",
        "customer_tin_number": "1234567890",
        "customer_bank_account_number": "1234567890123",
        "customer_region": "ADDIS_ABABA",
        "customer_city": "ADDIS_ABABA",
        "customer_zone_or_sub_city": "ZONE_1",
        "customer_woreda": "01",
        "customerId": "CUST_TEST_001",
        # Business fields
        "business_id": "BUS_TEST_001",
        "business_name": "Test Business",
        "business_tin_number": "9876543210",
        "business_city": "ADDIS_ABABA",
        "business_zone_or_sub_city": "ZONE_1",
        "business_woreda": "01",
        "business_establishment_year": 2020,
        "business_sector": "AGRICULTURE",
        "business_level": "GROWING",
        "business_starting_capital": 100000.0,
        "business_current_capital": 150000.0,
        "business_annual_profit": 25000.0,
        "business_annual_sales": 200000.0,
        "business_current_no_of_employees": 5,
        "business_starting_no_of_employees": 2,
        "business_source_of_initial_capital": "FAMILY",
        "business_association_type": "SOLE_PROPRIETORSHIP",
    }


@pytest.fixture
def sample_kyc_object(sample_kyc_data: Dict[str, Any]) -> KYCData:
    """KYCData object for testing"""
    return KYCData(**sample_kyc_data)


@pytest.fixture
def sample_transaction_object(sample_transaction_data: Dict[str, Any]) -> TransactionData:
    """TransactionData object for testing"""
    return TransactionData(**sample_transaction_data)


@pytest.fixture
def sample_combined_object(sample_combined_data: Dict[str, Any]) -> CombinedKYCBusinessData:
    """CombinedKYCBusinessData object for testing"""
    return CombinedKYCBusinessData(**sample_combined_data)


@pytest.fixture
def transaction_test_data() -> pd.DataFrame:
    """Load transaction test data"""
    data_file = Path("data/raw/transaction_training_data.csv")
    if not data_file.exists():
        pytest.skip(f"Test data not found: {data_file}")
    return pd.read_csv(data_file)


@pytest.fixture
def merged_test_data() -> pd.DataFrame:
    """Load merged KYC+Business test data"""
    data_file = Path("data/raw/kyc_business_training_data.csv")
    if not data_file.exists():
        pytest.skip(f"Test data not found: {data_file}")
    return pd.read_csv(data_file)


@pytest.fixture
def models_dir() -> Path:
    """Path to models directory"""
    return Path("data/models")


@pytest.fixture(scope="session")
def mock_api_key() -> str:
    """Mock API key for testing"""
    return "test-api-key"


# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "requires_models: marks tests requiring trained models")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")

