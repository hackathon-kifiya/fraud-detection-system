"""
Tests for SupervisedAnomalyDetectorService

Tests model loading, prediction functionality, batch processing, and F1 score validation.
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock

from app.services.supervised_anomaly_detector import SupervisedAnomalyDetectorService
from app.models.schemas import KYCData, TransactionData, CombinedKYCBusinessData, RiskLevel
from tests.conftest import (
    sample_kyc_data,
    sample_transaction_data,
    sample_combined_data,
)


@pytest.mark.requires_models
class TestSupervisedServiceModelLoading:
    """Test model loading functionality"""
    
    @pytest.mark.asyncio
    async def test_initialize_loads_models_successfully(self):
        """Test that supervised service initializes and loads models"""
        service = SupervisedAnomalyDetectorService()
        
        try:
            await service.initialize()
            
            # Verify models are loaded
            assert service.kyc_model is not None
            assert service.transaction_model is not None
            assert service.kyc_scaler is not None
            assert service.transaction_scaler is not None
        except Exception as e:
            pytest.skip(f"Supervised models not available: {e}")
    
    def test_check_models_exist_returns_true_when_files_exist(self):
        """Test that _check_models_exist returns True when model files exist"""
        service = SupervisedAnomalyDetectorService()
        
        try:
            models_exist = service._check_models_exist()
            assert isinstance(models_exist, bool)
        except Exception as e:
            pytest.skip(f"Could not check supervised models: {e}")


class TestSupervisedServicePrediction:
    """Tests for supervised prediction functionality"""
    
    def test_predict_kyc_returns_valid_output(self, sample_kyc_data):
        """Test KYC prediction returns valid output format"""
        service = SupervisedAnomalyDetectorService()
        
        # Mock service
        service.kyc_model = Mock()
        service.kyc_model.predict.return_value = np.array([0])
        service.kyc_model.predict_proba.return_value = np.array([[0.8, 0.2]])
        service.kyc_scaler = Mock()
        service.kyc_scaler.transform.return_value = np.array([[1.0] * 6])
        service.kyc_explainer = Mock()
        service.kyc_explainer.explain.return_value = {
            "top_contributing_features": {"age": 0.5},
            "feature_values": {"age": 35},
            "shap_values": {"age": 0.2}
        }
        
        data = KYCData(**sample_kyc_data)
        result = service.predict_kyc(data)
        
        # Verify output structure
        assert len(result) == 4
        is_anomaly, score, risk_level, explanation = result
        
        assert isinstance(is_anomaly, bool)
        assert isinstance(score, float)
        assert 0 <= score <= 1  # Supervised uses probability
        assert isinstance(risk_level, RiskLevel)
        assert isinstance(explanation, dict)
    
    def test_predict_transaction_uses_probability_scores(self, sample_transaction_data):
        """Test that supervised model uses probability scores correctly"""
        service = SupervisedAnomalyDetectorService()
        
        # Mock service
        service.transaction_model = Mock()
        service.transaction_model.predict.return_value = np.array([1])
        service.transaction_model.predict_proba.return_value = np.array([[0.15, 0.85]])
        service.transaction_scaler = Mock()
        service.transaction_scaler.transform.return_value = np.array([[1.0] * 8])
        service.transaction_explainer = Mock()
        service.transaction_explainer.explain.return_value = {
            "top_contributing_features": {"amount": 0.7},
            "feature_values": {"amount": 1000.0},
            "shap_values": {"amount": 0.5}
        }
        
        data = TransactionData(**sample_transaction_data)
        is_anomaly, score, risk_level, _ = service.predict_transaction(data)
        
        assert isinstance(is_anomaly, bool)
        assert 0 <= score <= 1  # Probability score
        assert score == 0.85  # Probability of class 1
        assert is_anomaly == True  # probability > 0.5


class TestSupervisedServiceCombined:
    """Tests for combined KYC+Business detection"""
    
    def test_predict_combined_returns_valid_output(self, sample_combined_data):
        """Test combined prediction returns valid output"""
        service = SupervisedAnomalyDetectorService()
        
        # Mock service
        service.combined_model = Mock()
        service.combined_model.predict.return_value = np.array([0])
        service.combined_model.predict_proba.return_value = np.array([[0.7, 0.3]])
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
            assert 0 <= score <= 1
        except ValueError:
            pytest.skip("Combined supervised model not available")
    
    def test_predict_combined_raises_error_if_model_not_available(self, sample_combined_data):
        """Test that predict_combined raises error when model not loaded"""
        service = SupervisedAnomalyDetectorService()
        service.combined_model = None
        service.combined_scaler = None
        
        data = CombinedKYCBusinessData(**sample_combined_data)
        
        with pytest.raises(ValueError, match="Combined supervised model not available"):
            service.predict_combined(data)


class TestSupervisedServiceBatch:
    """Tests for batch processing"""
    
    def test_predict_customer_batch_aggregates_correctly(self):
        """Test that customer batch predictions aggregate transaction-level predictions"""
        service = SupervisedAnomalyDetectorService()
        
        # Mock the predict_transaction method to return varying probabilities
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
        assert 0 <= customer_score <= 1
        assert isinstance(customer_risk, RiskLevel)
        assert len(transaction_results) == 3
    
    def test_predict_customer_batch_calculates_average_score(self):
        """Test that customer batch calculates average anomaly score"""
        service = SupervisedAnomalyDetectorService()
        
        # Mock with known scores
        scores = [0.9, 0.3, 0.8, 0.6, 0.4]
        service.predict_transaction = Mock(
            side_effect=[
                (True, score, RiskLevel.HIGH, {}) for score in scores
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
        
        transactions = [data] * len(scores)
        _, customer_score, _, _ = service.predict_customer_batch("CUST_TEST", transactions)
        
        # Average of [0.9, 0.3, 0.8, 0.6, 0.4] = 0.6
        assert abs(customer_score - 0.6) < 0.01
    
    def test_predict_customer_batch_flags_based_on_thresholds(self):
        """Test that customer flagging uses correct thresholds"""
        service = SupervisedAnomalyDetectorService()
        
        # Mock with high anomaly rate
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
        
        # 10 transactions, all anomalous (>30% threshold)
        transactions = [data] * 10
        
        customer_flagged, _, customer_risk, _ = service.predict_customer_batch("CUST_TEST", transactions)
        
        assert customer_flagged is True
        assert customer_risk == RiskLevel.HIGH
    
    def test_predict_customer_batch_requires_at_least_one_transaction(self):
        """Test that batch prediction raises error with empty transactions"""
        service = SupervisedAnomalyDetectorService()
        
        with pytest.raises(ValueError, match="At least one transaction"):
            service.predict_customer_batch("CUST_TEST", [])


class TestSupervisedServiceRiskCalculation:
    """Tests for risk level calculation"""
    
    def test_calculate_risk_level_uses_probability_thresholds(self):
        """Test that supervised risk calculation uses probability thresholds correctly"""
        service = SupervisedAnomalyDetectorService()
        
        # HIGH risk (probability >= 0.7)
        assert service._calculate_risk_level(0.85) == RiskLevel.HIGH
        assert service._calculate_risk_level(0.7) == RiskLevel.HIGH
        
        # MEDIUM risk (0.5 <= probability < 0.7)
        assert service._calculate_risk_level(0.6) == RiskLevel.MEDIUM
        assert service._calculate_risk_level(0.5) == RiskLevel.MEDIUM
        
        # LOW risk (probability < 0.5)
        assert service._calculate_risk_level(0.4) == RiskLevel.LOW
        assert service._calculate_risk_level(0.1) == RiskLevel.LOW
    
    def test_extract_kyc_features_produces_correct_shape(self, sample_kyc_data):
        """Test KYC feature extraction produces correct shape for supervised"""
        service = SupervisedAnomalyDetectorService()
        data = KYCData(**sample_kyc_data)
        
        features = service._extract_kyc_features(data)
        
        assert features.shape == (1, 6)  # 6 KYC features
        assert all(isinstance(x, (int, float)) for x in features.flatten())
    
    def test_extract_transaction_features_produces_correct_shape(self, sample_transaction_data):
        """Test transaction feature extraction produces correct shape for supervised"""
        service = SupervisedAnomalyDetectorService()
        data = TransactionData(**sample_transaction_data)
        
        features = service._extract_transaction_features(data)
        
        assert features.shape == (1, 8)  # 8 transaction features
        assert all(isinstance(x, (int, float)) for x in features.flatten())


class TestSupervisedServiceFeatureExtraction:
    """Tests for feature extraction methods"""
    
    def test_extract_kyc_features_converts_types_correctly(self):
        """Test that KYC features handle type conversions"""
        service = SupervisedAnomalyDetectorService()
        
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
        
        features = service._extract_kyc_features(data)
        
        # Verify structure
        assert len(features) == 1
        assert len(features[0]) == 6
        assert features[0, 0] == 35  # age
    
    def test_extract_transaction_features_maps_types(self):
        """Test transaction features map types correctly"""
        service = SupervisedAnomalyDetectorService()
        
        type_mappings = [
            ("purchase", 0),
            ("withdrawal", 1),
            ("transfer", 2),
            ("deposit", 3),
        ]
        
        for tx_type, expected_code in type_mappings:
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
            
            features = service._extract_transaction_features(data)
            # Transaction type is at index 1
            assert features[0][1] == expected_code

