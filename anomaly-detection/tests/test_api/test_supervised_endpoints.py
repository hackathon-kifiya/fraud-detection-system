"""
Tests for Supervised API Endpoints

Tests all supervised endpoint functionality including:
- Transaction endpoints
- Merged endpoints
- Authentication
- Validation
- Error handling
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from tests.conftest import (
    sample_transaction_data,
    sample_combined_data,
)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_supervised_service():
    """Mock supervised anomaly detector service"""
    with patch('app.main.supervised_anomaly_service') as mock_service:
        mock_service.transaction_model = Mock()
        mock_service.combined_model = Mock()
        
        # Mock prediction methods (supervised returns probabilities 0-1)
        mock_service.predict_transaction.return_value = (
            False, 0.25, "LOW", {"top_contributing_features": {}, "feature_values": {}, "shap_values": {}}
        )
        mock_service.predict_combined.return_value = (
            False, 0.30, "LOW", {"top_contributing_features": {}, "feature_values": {}, "shap_values": {}}
        )
        mock_service.predict_customer_batch.return_value = (
            False, 0.35, "LOW", []
        )
        
        yield mock_service


class TestSupervisedTransactionEndpoints:
    """Tests for supervised transaction endpoints"""
    
    def test_check_transaction_success(self, client, mock_supervised_service, sample_transaction_data):
        """Test successful supervised transaction check"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            response = client.post(
                "/api/v1/supervised/transaction/check",
                json=sample_transaction_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "is_anomaly" in data
            assert "anomaly_score" in data
            assert 0 <= data["anomaly_score"] <= 1  # Probability score
            assert "risk_level" in data
            assert "explanation" in data
    
    def test_check_transaction_returns_probability_score(self, client, mock_supervised_service):
        """Test that supervised models return probability scores between 0-1"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            # Mock high probability
            mock_supervised_service.predict_transaction.return_value = (
                True, 0.85, "HIGH", {}
            )
            
            response = client.post(
                "/api/v1/supervised/transaction/check",
                json=sample_transaction_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert 0 <= data["anomaly_score"] <= 1
            assert data["is_anomaly"] is True
            assert data["risk_level"] == "HIGH"
    
    def test_check_transaction_missing_api_key(self, client, sample_transaction_data):
        """Test transaction check fails without API key"""
        response = client.post(
            "/api/v1/supervised/transaction/check",
            json=sample_transaction_data
        )
        
        assert response.status_code in [403, 401]
    
    def test_check_transaction_invalid_customer_id(self, client, mock_supervised_service):
        """Test transaction check fails with invalid customer ID"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            invalid_data = sample_transaction_data.copy()
            invalid_data["customer_id"] = "INVALID"
            
            response = client.post(
                "/api/v1/supervised/transaction/check",
                json=invalid_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 400
            assert "Invalid customer_id format" in response.json()["detail"]
    
    def test_batch_transaction_success(self, client, mock_supervised_service):
        """Test batch transaction check succeeds"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            batch_data = {
                "transactions": [sample_transaction_data, sample_transaction_data]
            }
            
            response = client.post(
                "/api/v1/supervised/transaction/batch",
                json=batch_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "batch_results" in data
            assert "total_processed" in data
            assert "total_anomalies" in data
            assert "processing_time_seconds" in data
    
    def test_customer_batch_transaction_success(self, client, mock_supervised_service):
        """Test customer batch transaction check succeeds for supervised"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            batch_data = {
                "customer_id": "CUST_12345",
                "transactions": [sample_transaction_data, sample_transaction_data]
            }
            
            response = client.post(
                "/api/v1/supervised/transaction/customer/batch",
                json=batch_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "customer_id" in data
            assert "total_transactions" in data
            assert "customer_flagged" in data
            assert "customer_risk_level" in data
            assert "customer_anomaly_score" in data
            assert 0 <= data["customer_anomaly_score"] <= 1
    
    def test_get_transaction_stats_supervised(self, client, mock_supervised_service):
        """Test supervised transaction statistics endpoint"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            mock_supervised_service.transaction_feature_names = ["amount", "type"]
            
            response = client.get(
                "/api/v1/supervised/transaction/stats",
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "model_type" in data
            assert "Random Forest" in data["model_type"]
            assert "features" in data


class TestSupervisedMergedEndpoints:
    """Tests for supervised merged (KYC+Business) endpoints"""
    
    def test_check_merged_success(self, client, mock_supervised_service, sample_combined_data):
        """Test successful supervised merged check"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            response = client.post(
                "/api/v1/supervised/merged/check",
                json=sample_combined_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "is_anomaly" in data
            assert "anomaly_score" in data
            assert 0 <= data["anomaly_score"] <= 1
            assert "risk_level" in data
    
    def test_check_merged_model_not_available(self, client):
        """Test merged check fails when model not available"""
        # Service without combined model
        with patch('app.main.supervised_anomaly_service') as mock_service:
            mock_service.combined_model = None
            mock_service.combined_scaler = None
            
            with patch('app.core.security.get_api_key') as mock_auth:
                mock_auth.return_value = "test-api-key"
                
                response = client.post(
                    "/api/v1/supervised/merged/check",
                    json=sample_combined_data,
                    headers={"X-API-Key": "test-api-key"}
                )
                
                assert response.status_code == 503
                assert "not available" in response.json()["detail"]
    
    def test_batch_merged_success(self, client, mock_supervised_service):
        """Test batch merged check succeeds for supervised"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            batch_data = {
                "records": [sample_combined_data, sample_combined_data]
            }
            
            response = client.post(
                "/api/v1/supervised/merged/batch",
                json=batch_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "batch_results" in data
            assert "total_processed" in data
            assert "total_anomalies" in data
    
    def test_get_merged_stats_supervised(self, client, mock_supervised_service):
        """Test supervised merged statistics endpoint"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            mock_supervised_service.combined_feature_names = ["feature1", "feature2"]
            mock_supervised_service.combined_model = Mock()
            
            response = client.get(
                "/api/v1/supervised/merged/stats",
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "model_type" in data
            assert "Random Forest" in data["model_type"]
            assert "features" in data


class TestSupervisedEndpointValidation:
    """Tests for input validation on supervised endpoints"""
    
    def test_missing_required_fields(self, client):
        """Test endpoints fail with missing required fields"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            # Missing required fields
            incomplete_data = {"customer_id": "CUST_123"}
            
            response = client.post(
                "/api/v1/supervised/transaction/check",
                json=incomplete_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 422
    
    def test_invalid_date_format(self, client):
        """Test transaction check fails with invalid date format"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            invalid_data = sample_transaction_data.copy()
            invalid_data["date"] = "not-a-date"
            
            response = client.post(
                "/api/v1/supervised/transaction/check",
                json=invalid_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            # Should fail validation or processing
            assert response.status_code in [400, 422, 500]


class TestSupervisedEndpointErrorHandling:
    """Tests for error handling in supervised endpoints"""
    
    def test_service_exception_returns_500(self, client, mock_supervised_service):
        """Test that service exceptions return 500"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            # Make service raise exception
            mock_supervised_service.predict_transaction.side_effect = Exception("Service error")
            
            response = client.post(
                "/api/v1/supervised/transaction/check",
                json=sample_transaction_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 500
            assert "Error processing" in response.json()["detail"]
    
    def test_batch_handles_failures_gracefully(self, client, mock_supervised_service):
        """Test that batch processing handles failures gracefully"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            # Mock one failure
            def side_effect(*args):
                raise Exception("Prediction error")
            
            mock_supervised_service.predict_transaction.side_effect = side_effect
            
            batch_data = {
                "transactions": [sample_transaction_data]
            }
            
            response = client.post(
                "/api/v1/supervised/transaction/batch",
                json=batch_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            # Should still succeed with error in result
            assert response.status_code == 200
            data = response.json()
            assert data["total_processed"] == 1


class TestSupervisedVersusUnsupervisedDifference:
    """Tests to verify supervised models behave differently from unsupervised"""
    
    def test_supervised_returns_probability_not_score(self, client, mock_supervised_service):
        """Test that supervised models return probability (0-1) not score"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            mock_supervised_service.predict_transaction.return_value = (
                True, 0.75, "HIGH", {}
            )
            
            response = client.post(
                "/api/v1/supervised/transaction/check",
                json=sample_transaction_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            # Supervised returns probability between 0 and 1
            assert 0 <= data["anomaly_score"] <= 1
            # Not negative score like unsupervised
            assert data["anomaly_score"] >= 0

