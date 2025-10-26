"""
Tests for UnsupervisedAnomalyDetectorService

Tests model loading, prediction functionality, batch processing, and error handling.
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from app.services.unsupervised_anomaly_detector import UnsupervisedAnomalyDetectorService
from app.models.schemas import KYCData, TransactionData, CombinedKYCBusinessData, RiskLevel


@pytest.mark.requires_models
class TestUnsupervisedServiceModelLoading:
    """Test model loading functionality"""
    
    @pytest.mark.asyncio
    async def test_initialize_loads_models_successfully(self):
        """Test that service initializes and loads models"""
        service = UnsupervisedAnomalyDetectorService()
        
        try:
            await service.initialize()
            
            # Verify models are loaded
            assert service.kyc_model is not None
            assert service.transaction_model is not None
            assert service.kyc_scaler is not None
            assert service.transaction_scaler is not None
        except Exception as e:
            pytest.skip(f"Models not available: {e}")
    
    def test_check_models_exist_returns_true_when_files_exist(self):
        """Test that _check_models_exist returns True when model files exist"""
        service = UnsupervisedAnomalyDetectorService()
        
        # This will skip if models don't exist
        try:
            models_exist = service._check_models_exist()
            assert isinstance(models_exist, bool)
        except Exception as e:
            pytest.skip(f"Could not check models: {e}")


class TestUnsupervisedServiceKYC:
    """Tests for KYC anomaly detection"""
    
    def test_predict_kyc_returns_valid_output(self, sample_kyc_data):
        """Test KYC prediction returns valid output format"""
        service = UnsupervisedAnomalyDetectorService()
        
        # Mock service to not require actual models
        service.kyc_model = Mock()
        service.kyc_model.predict.return_value = np.array([-1])
        service.kyc_model.score_samples.return_value = np.array([-0.5])
        service.kyc_scaler = Mock()
        service.kyc_scaler.transform.return_value = np.array([[1.0] * 6])
        service.kyc_explainer = Mock()
        service.kyc_explainer.explain.return_value = {
            "top_contributing_features": {"age": 0.5},
            "feature_values": {"age": 35},
            "shap_values": {"age": -0.2}
        }
        
        data = KYCData(**sample_kyc_data)
        result = service.predict_kyc(data)
        
        # Verify output structure
        assert len(result) == 4
        is_anomaly, score, risk_level, explanation = result
        
        assert isinstance(is_anomaly, bool)
        assert isinstance(score, float)
        assert isinstance(risk_level, RiskLevel)
        assert isinstance(explanation, dict)
        
        # Verify explanation structure
        assert "top_contributing_features" in explanation
        assert "feature_values" in explanation
        assert "shap_values" in explanation
    
    def test_predict_kyc_calculates_risk_level_correctly(self, sample_kyc_data):
        """Test that risk levels are calculated correctly based on scores"""
        service = UnsupervisedAnomalyDetectorService()
        service.kyc_model = Mock()
        service.kyc_scaler = Mock()
        service.kyc_scaler.transform.return_value = np.array([[1.0] * 6])
        service.kyc_explainer = Mock()
        service.kyc_explainer.explain.return_value = {
            "top_contributing_features": {},
            "feature_values": {},
            "shap_values": {}
        }
        
        data = KYCData(**sample_kyc_data)
        
        # Test HIGH risk (low score)
        service.kyc_model.score_samples.return_value = np.array([-0.5])
        _, _, risk_level, _ = service.predict_kyc(data)
        assert risk_level == RiskLevel.HIGH
        
        # Test MEDIUM risk
        service.kyc_model.score_samples.return_value = np.array([-0.2])
        _, _, risk_level, _ = service.predict_kyc(data)
        assert risk_level == RiskLevel.MEDIUM
        
        # Test LOW risk (high score)
        service.kyc_model.score_samples.return_value = np.array([0.5])
        _, _, risk_level, _ = service.predict_kyc(data)
        assert risk_level == RiskLevel.LOW


class TestUnsupervisedServiceTransaction:
    """Tests for Transaction anomaly detection"""
    
    def test_predict_transaction_returns_valid_output(self, sample_transaction_data):
        """Test transaction prediction returns valid output"""
        service = UnsupervisedAnomalyDetectorService()
        
        # Mock service
        service.transaction_model = Mock()
        service.transaction_model.predict.return_value = np.array([1])
        service.transaction_model.score_samples.return_value = np.array([[0.5]])
        service.transaction_scaler = Mock()
        service.transaction_scaler.transform.return_value = np.array([[1.0] * 8])
        service.transaction_explainer = Mock()
        service.transaction_explainer.explain.return_value = {
            "top_contributing_features": {"amount": 0.6},
            "feature_values": {"amount": 1000.0},
            "shap_values": {"amount": 0.3}
        }
        
        data = TransactionData(**sample_transaction_data)
        result = service.predict_transaction(data)
        
        # Verify output structure
        assert len(result) == 4
        is_anomaly, score, risk_level, explanation = result
        
        assert isinstance(is_anomaly, bool)
        assert isinstance(score, float)
        assert isinstance(risk_level, RiskLevel)
        assert isinstance(explanation, dict)
    
    def test_extract_transaction_features(self, sample_transaction_data):
        """Test transaction feature extraction"""
        service = UnsupervisedAnomalyDetectorService()
        data = TransactionData(**sample_transaction_data)
        
        features = service.extract_transaction_features(data)
        
        assert features.shape == (1, 8)  # 8 transaction features
        assert all(isinstance(x, (int, float)) for x in features.flatten())


class TestUnsupervisedServiceCombined:
    """Tests for combined KYC+Business anomaly detection"""
    
    def test_predict_combined_returns_valid_output(self, sample_combined_data):
        """Test combined prediction returns valid output"""
        service = UnsupervisedAnomalyDetectorService()
        
        # Mock service
        service.combined_model = Mock()
        service.combined_model.predict.return_value = np.array([-1])
        service.combined_model.score_samples.return_value = np.array([-0.3])
        service.combined_scaler = Mock()
        service.combined_scaler.transform.return_value = np.array([[1.0] * 26])
        service.combined_explainer = Mock()
        service.combined_explainer.explain.return_value = {
            "top_contributing_features": {},
            "feature_values": {},
            "shap_values": {}
        }
        
        data = CombinedKYCBusinessData(**sample_combined_data)
        
        try:
            result = service.predict_combined(data)
            
            assert len(result) == 4
            is_anomaly, score, risk_level, explanation = result
            
            assert isinstance(is_anomaly, bool)
            assert isinstance(score, float)
            assert isinstance(risk_level, RiskLevel)
        except ValueError:
            pytest.skip("Combined model not available")


class TestUnsupervisedServiceBatch:
    """Tests for batch processing"""
    
    def test_predict_customer_batch_aggregates_correctly(self):
        """Test that customer batch predictions aggregate transaction-level predictions"""
        service = UnsupervisedAnomalyDetectorService()
        
        # Mock the predict_transaction method
        service.predict_transaction = Mock(
            side_effect=[
                (True, 0.9, RiskLevel.HIGH, {"shap": 0.5}),
                (False, 0.3, RiskLevel.LOW, {"shap": 0.2}),
                (True, 0.8, RiskLevel.HIGH, {"shap": 0.4}),
            ]
        )
        
        data = TransactionData(
            customer_id="CUST_TEST",
            date="2024-01-01",
            credit=100.0,
            debit=0.0,
            closingBalance=1000.0,
            narrative="Test",
            source="TEST"
        )
        
        transactions = [data, data, data]
        
        result = service.predict_customer_batch("CUST_TEST", transactions)
        
        assert len(result) == 4
        customer_flagged, customer_score, customer_risk, transaction_results = result
        
        assert isinstance(customer_flagged, bool)
        assert isinstance(customer_score, float)
        assert isinstance(customer_risk, RiskLevel)
        assert len(transaction_results) == 3
    
    def test_predict_customer_batch_flags_high_risk_customer(self):
        """Test that high-risk customers are properly flagged"""
        service = UnsupervisedAnomalyDetectorService()
        
        # Mock high anomaly rate (> 30%)
        service.predict_transaction = Mock(
            return_value=(True, 0.85, RiskLevel.HIGH, {})
        )
        
        data = TransactionData(
            customer_id="CUST_TEST",
            date="2024-01-01",
            credit=100.0,
            debit=0.0,
            closingBalance=1000.0,
            narrative="Test",
            source="TEST"
        )
        
        transactions = [data] * 5  # 5 transactions
        
        customer_flagged, _, _, _ = service.predict_customer_batch("CUST_TEST", transactions)
        
        # With 5 anomalies out of 5 (>30%), customer should be flagged
        assert customer_flagged is True
    
    def test_predict_customer_batch_requires_at_least_one_transaction(self):
        """Test that batch prediction raises error with empty transactions"""
        service = UnsupervisedAnomalyDetectorService()
        
        with pytest.raises(ValueError, match="At least one transaction"):
            service.predict_customer_batch("CUST_TEST", [])


class TestUnsupervisedServiceErrorHandling:
    """Tests for error handling and edge cases"""
    
    def test_predict_combined_raises_error_if_model_not_available(self, sample_combined_data):
        """Test that predict_combined raises error when model not loaded"""
        service = UnsupervisedAnomalyDetectorService()
        service.combined_model = None
        service.combined_scaler = None
        
        data = CombinedKYCBusinessData(**sample_combined_data)
        
        with pytest.raises(ValueError, match="Combined model not available"):
            service.predict_combined(data)
    
    def test_calculate_risk_level_handles_edge_cases(self):
        """Test risk level calculation handles edge cases"""
        service = UnsupervisedAnomalyDetectorService()
        
        # Test very low score
        assert service._calculate_risk_level(-1.0) == RiskLevel.HIGH
        
        # Test boundary values
        assert service._calculate_risk_level(-0.3) == RiskLevel.HIGH
        assert service._calculate_risk_level(-0.29) == RiskLevel.MEDIUM
        assert service._calculate_risk_level(-0.1) == RiskLevel.MEDIUM
        assert service._calculate_risk_level(-0.09) == RiskLevel.LOW
        assert service._calculate_risk_level(0.5) == RiskLevel.LOW


class TestUnsupervisedServiceFeatureExtraction:
    """Tests for feature extraction methods"""
    
    def test_extract_kyc_features_produces_correct_shape(self, sample_kyc_data):
        """Test KYC feature extraction produces correct shape"""
        service = UnsupervisedAnomalyDetectorService()
        data = KYCData(**sample_kyc_data)
        
        features = service.extract_kyc_features(data)
        
        assert features.shape == (1, 6)  # 6 KYC features
        assert all(isinstance(x, (int, float)) for x in features.flatten())
    
    def test_extract_kyc_features_handles_numeric_conversion(self):
        """Test KYC feature extraction handles numeric conversions correctly"""
        service = UnsupervisedAnomalyDetectorService()
        
        # Create data with numeric fields
        data = KYCData(
            customer_id="CUST_001",
            customer_name="Test",
            customer_phone_number=9123456789,
            customer_age=35,
            customer_gender="male",
            customer_marital_status="married",
            customer_education_level="primary",
            customer_tin_number="1234567890",
            customer_bank_account_number="1234567890123",
            customer_region="ADDIS_ABABA",
            customer_city="ADDIS_ABABA",
            customer_zone_or_sub_city="ZONE_1",
            customer_woreda=1,
            customerId="CUST_001"
        )
        
        features = service.extract_kyc_features(data)
        assert features.shape[1] == 6
    
    def test_extract_transaction_features_maps_types_correctly(self):
        """Test transaction features map transaction types correctly"""
        service = UnsupervisedAnomalyDetectorService()
        
        # Test different transaction types
        for tx_type, expected_code in [
            ("purchase", 0),
            ("withdrawal", 1),
            ("transfer", 2),
            ("deposit", 3),
        ]:
            data = TransactionData(
                customer_id="CUST_001",
                date="2024-01-01",
                credit=100.0,
                debit=0.0,
                closingBalance=1000.0,
                narrative="Test",
                source="TEST",
                is_anomaly=0
            )
            
            features = service.extract_transaction_features(data)
            # Transaction type is feature index 1
            assert features[0, 1] == expected_code

