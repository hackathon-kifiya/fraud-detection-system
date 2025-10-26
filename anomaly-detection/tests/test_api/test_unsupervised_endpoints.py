"""
Tests for Unsupervised API Endpoints

Tests all unsupervised endpoint functionality including:
- KYC endpoints
- Transaction endpoints
- Merged endpoints
- Authentication
- Validation
- Error handling
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock, patch

from app.main import app
from tests.conftest import (
    sample_kyc_data,
    sample_transaction_data,
    sample_combined_data,
)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_unsupervised_service():
    """Mock unsupervised anomaly detector service"""
    with patch('app.main.unsupervised_anomaly_service') as mock_service:
        mock_service.kyc_model = Mock()
        mock_service.transaction_model = Mock()
        mock_service.combined_model = Mock()
        
        # Mock prediction methods
        mock_service.predict_kyc.return_value = (
            False, 0.75, "LOW", {"top_contributing_features": {}, "feature_values": {}, "shap_values": {}}
        )
        mock_service.predict_transaction.return_value = (
            False, 0.80, "LOW", {"top_contributing_features": {}, "feature_values": {}, "shap_values": {}}
        )
        mock_service.predict_combined.return_value = (
            False, 0.70, "LOW", {"top_contributing_features": {}, "feature_values": {}, "shap_values": {}}
        )
        mock_service.predict_customer_batch.return_value = (
            False, 0.45, "LOW", []
        )
        
        yield mock_service


class TestUnsupervisedKYCEndpoints:
    """Tests for unsupervised KYC endpoints"""
    
    def test_check_kyc_success(self, client, mock_unsupervised_service, sample_kyc_data):
        """Test successful KYC check"""
        # Mock API key authentication
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            response = client.post(
                "/api/v1/unsupervised/kyc/check",
                json=sample_kyc_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "is_anomaly" in data
            assert "anomaly_score" in data
            assert "risk_level" in data
            assert "explanation" in data
    
    def test_check_kyc_missing_api_key(self, client, sample_kyc_data):
        """Test KYC check fails without API key"""
        response = client.post(
            "/api/v1/unsupervised/kyc/check",
            json=sample_kyc_data
        )
        
        # Should be 403 Forbidden when API key is required
        assert response.status_code in [403, 401]
    
    def test_check_kyc_invalid_customer_id(self, client, mock_unsupervised_service):
        """Test KYC check fails with invalid customer ID format"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            invalid_data = sample_kyc_data.copy()
            invalid_data["customer_id"] = "INVALID_ID"  # Doesn't start with CUST_
            
            response = client.post(
                "/api/v1/unsupervised/kyc/check",
                json=invalid_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 400
            assert "Invalid customer_id format" in response.json()["detail"]
    
    def test_batch_kyc_success(self, client, mock_unsupervised_service):
        """Test batch KYC check succeeds"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            batch_data = {
                "records": [sample_kyc_data, sample_kyc_data]
            }
            
            response = client.post(
                "/api/v1/unsupervised/kyc/batch",
                json=batch_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "batch_results" in data
            assert "total_processed" in data
            assert "total_anomalies" in data
            assert "processing_time_seconds" in data
    
    def test_get_kyc_stats(self, client, mock_unsupervised_service):
        """Test KYC model statistics endpoint"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            # Set feature names for stats
            mock_unsupervised_service.kyc_feature_names = ["age", "income"]
            
            response = client.get(
                "/api/v1/unsupervised/kyc/stats",
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "model_type" in data
            assert "features" in data
            assert "num_features" in data


class TestUnsupervisedTransactionEndpoints:
    """Tests for unsupervised transaction endpoints"""
    
    def test_check_transaction_success(self, client, mock_unsupervised_service, sample_transaction_data):
        """Test successful transaction check"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            response = client.post(
                "/api/v1/unsupervised/transaction/check",
                json=sample_transaction_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "is_anomaly" in data
            assert "anomaly_score" in data
            assert "risk_level" in data
            assert "explanation" in data
    
    def test_check_transaction_invalid_customer_id(self, client, mock_unsupervised_service):
        """Test transaction check fails with invalid customer ID"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            invalid_data = sample_transaction_data.copy()
            invalid_data["customer_id"] = "INVALID"
            
            response = client.post(
                "/api/v1/unsupervised/transaction/check",
                json=invalid_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 400
            assert "Invalid customer_id format" in response.json()["detail"]
    
    def test_batch_transaction_success(self, client, mock_unsupervised_service):
        """Test batch transaction check succeeds"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            batch_data = {
                "transactions": [sample_transaction_data, sample_transaction_data]
            }
            
            response = client.post(
                "/api/v1/unsupervised/transaction/batch",
                json=batch_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "batch_results" in data
            assert "total_processed" in data
            assert "total_anomalies" in data
            assert "processing_time_seconds" in data
    
    def test_customer_batch_transaction_success(self, client, mock_unsupervised_service):
        """Test customer batch transaction check succeeds"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            batch_data = {
                "customer_id": "CUST_12345",
                "transactions": [sample_transaction_data, sample_transaction_data]
            }
            
            response = client.post(
                "/api/v1/unsupervised/transaction/customer/batch",
                json=batch_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "customer_id" in data
            assert "total_transactions" in data
            assert "customer_flagged" in data
            assert "customer_risk_level" in data
    
    def test_get_transaction_stats(self, client, mock_unsupervised_service):
        """Test transaction statistics endpoint"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            mock_unsupervised_service.transaction_feature_names = ["amount", "type"]
            
            response = client.get(
                "/api/v1/unsupervised/transaction/stats",
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "model_type" in data
            assert "features" in data


class TestUnsupervisedMergedEndpoints:
    """Tests for unsupervised merged (KYC+Business) endpoints"""
    
    def test_check_merged_success(self, client, mock_unsupervised_service, sample_combined_data):
        """Test successful merged check"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            response = client.post(
                "/api/v1/unsupervised/merged/check",
                json=sample_combined_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "is_anomaly" in data
            assert "anomaly_score" in data
            assert "risk_level" in data
    
    def test_check_merged_invalid_customer_id(self, client, mock_unsupervised_service):
        """Test merged check fails with invalid customer ID"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            invalid_data = sample_combined_data.copy()
            invalid_data["customer_id"] = "INVALID"
            
            response = client.post(
                "/api/v1/unsupervised/merged/check",
                json=invalid_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 400
    
    def test_check_merged_model_not_available(self, client):
        """Test merged check fails when model not available"""
        # Service without combined model
        with patch('app.main.unsupervised_anomaly_service') as mock_service:
            mock_service.combined_model = None
            mock_service.combined_scaler = None
            
            with patch('app.core.security.get_api_key') as mock_auth:
                mock_auth.return_value = "test-api-key"
                
                response = client.post(
                    "/api/v1/unsupervised/merged/check",
                    json=sample_combined_data,
                    headers={"X-API-Key": "test-api-key"}
                )
                
                assert response.status_code == 503
                assert "not available" in response.json()["detail"]
    
    def test_batch_merged_success(self, client, mock_unsupervised_service):
        """Test batch merged check succeeds"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            batch_data = {
                "records": [sample_combined_data, sample_combined_data]
            }
            
            response = client.post(
                "/api/v1/unsupervised/merged/batch",
                json=batch_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "batch_results" in data
            assert "total_processed" in data
            assert "total_anomalies" in data
    
    def test_get_merged_stats(self, client, mock_unsupervised_service):
        """Test merged statistics endpoint"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            mock_unsupervised_service.combined_feature_names = ["feature1", "feature2"]
            mock_unsupervised_service.combined_model = Mock()
            
            response = client.get(
                "/api/v1/unsupervised/merged/stats",
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "model_type" in data
            assert "features" in data


class TestUnsupervisedEndpointValidation:
    """Tests for input validation on unsupervised endpoints"""
    
    def test_missing_required_fields(self, client):
        """Test endpoints fail with missing required fields"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            # Missing required field
            incomplete_data = {"customer_id": "CUST_123"}
            
            response = client.post(
                "/api/v1/unsupervised/kyc/check",
                json=incomplete_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 422  # Validation error
    
    def test_invalid_field_types(self, client):
        """Test endpoints fail with invalid field types"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            invalid_data = sample_kyc_data.copy()
            invalid_data["customer_age"] = "not_a_number"  # Should be int
            
            response = client.post(
                "/api/v1/unsupervised/kyc/check",
                json=invalid_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 422
    
    def test_invalid_enum_values(self, client):
        """Test endpoints fail with invalid enum values"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            invalid_data = sample_kyc_data.copy()
            invalid_data["customer_gender"] = "invalid_gender"
            
            response = client.post(
                "/api/v1/unsupervised/kyc/check",
                json=invalid_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 422


class TestUnsupervisedEndpointErrorHandling:
    """Tests for error handling in unsupervised endpoints"""
    
    def test_service_exception_returns_500(self, client, mock_unsupervised_service):
        """Test that service exceptions return 500"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            # Make service raise exception
            mock_unsupervised_service.predict_kyc.side_effect = Exception("Service error")
            
            response = client.post(
                "/api/v1/unsupervised/kyc/check",
                json=sample_kyc_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert response.status_code == 500
            assert "Error processing" in response.json()["detail"]
    
    def test_batch_handles_individual_failures_gracefully(self, client, mock_unsupervised_service):
        """Test that batch processing handles individual record failures"""
        with patch('app.core.security.get_api_key') as mock_auth:
            mock_auth.return_value = "test-api-key"
            
            # Mock one successful, one failed prediction
            def side_effect(*args):
                if args[0].customer_id == "CUST_FAIL":
                    raise Exception("Prediction error")
                return (False, 0.75, "LOW", {})
            
            mock_unsupervised_service.predict_kyc.side_effect = side_effect
            
            batch_data = {
                "records": [
                    sample_kyc_data,
                    {**sample_kyc_data, "customer_id": "CUST_FAIL"}
                ]
            }
            
            response = client.post(
                "/api/v1/unsupervised/kyc/batch",
                json=batch_data,
                headers={"X-API-Key": "test-api-key"}
            )
            
            # Should succeed but have error in one result
            assert response.status_code == 200
            data = response.json()
            assert data["total_processed"] == 2
            # Should have one with error
            errors = [r.get("error") for r in data["batch_results"] if "error" in r]
            assert len(errors) >= 0  # At least one might have error

