"""
Model Performance Tests - F1 Score Validation

Tests that all trained models achieve F1 score >= 0.7 on validation data.
This is a critical requirement for production models.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import joblib

# Model paths
MODELS_DIR = Path("data/models")

# Feature preparation functions
from app.ml.preprocessing.feature_engineering.prepare_merged_data import (
    prepare_kyc_features,
    prepare_business_features,
)
from app.ml.preprocessing.feature_engineering.prepare_transaction import (
    prepare_transaction_features,
)
from app.ml.preprocessing.feature_engineering.prepare_transaction_customer_data import (
    prepare_customer_features,
)


# Minimum acceptable F1 score
MIN_F1_SCORE = 0.7


class TestUnsupervisedModelF1Scores:
    """Test unsupervised Isolation Forest models meet F1>=0.7 requirement"""
    
    @pytest.fixture
    def transaction_data(self):
        """Load transaction test data"""
        data_file = Path("data/raw/transaction_training_data.csv")
        if not data_file.exists():
            pytest.skip(f"Test data not found: {data_file}")
        
        df = pd.read_csv(data_file)
        # Use 20% for validation
        test_df = df.sample(frac=0.2, random_state=42)
        return test_df
    
    @pytest.fixture
    def merged_data(self):
        """Load merged KYC+Business test data"""
        data_file = Path("data/raw/kyc_business_training_data.csv")
        if not data_file.exists():
            pytest.skip(f"Test data not found: {data_file}")
        
        df = pd.read_csv(data_file)
        test_df = df.sample(frac=0.2, random_state=42)
        return test_df
    
    def test_transaction_model_f1_score(self, transaction_data):
        """Test transaction model F1 score >= 0.7"""
        model_path = MODELS_DIR / "transaction_model.pkl"
        scaler_path = MODELS_DIR / "transaction_scaler.pkl"
        
        if not model_path.exists():
            pytest.skip("Transaction model not trained")
        
        # Load model and scaler
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Prepare features
        X = prepare_transaction_features(transaction_data)
        X_scaled = scaler.transform(X)
        
        # Get labels if available
        if "is_anomaly" in transaction_data.columns:
            y_true = transaction_data["is_anomaly"].values
        else:
            pytest.skip("No labels in test data")
        
        # Predict
        predictions = model.predict(X_scaled)
        # Isolation Forest: -1 = anomaly, 1 = normal
        y_pred = (predictions == -1).astype(int)
        
        # Calculate F1 score
        from sklearn.metrics import f1_score
        f1 = f1_score(y_true, y_pred)
        
        print(f"\nTransaction Model F1 Score: {f1:.4f}")
        assert f1 >= MIN_F1_SCORE, f"F1 score {f1:.4f} below minimum {MIN_F1_SCORE}"
    
    def test_merged_model_f1_score(self, merged_data):
        """Test merged model F1 score >= 0.7"""
        model_path = MODELS_DIR / "merged_model.pkl"
        scaler_path = MODELS_DIR / "merged_scaler.pkl"
        
        if not model_path.exists():
            pytest.skip("Merged model not trained")
        
        # Load model and scaler
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Prepare features
        kyc_features = prepare_kyc_features(merged_data)
        biz_features = prepare_business_features(merged_data)
        X = np.column_stack([kyc_features, biz_features])
        X_scaled = scaler.transform(X)
        
        # Get labels
        if "is_anomaly" in merged_data.columns:
            y_true = merged_data["is_anomaly"].values
        else:
            pytest.skip("No labels in test data")
        
        # Predict
        predictions = model.predict(X_scaled)
        y_pred = (predictions == -1).astype(int)
        
        # Calculate F1 score
        from sklearn.metrics import f1_score
        f1 = f1_score(y_true, y_pred)
        
        print(f"\nMerged Model F1 Score: {f1:.4f}")
        assert f1 >= MIN_F1_SCORE, f"F1 score {f1:.4f} below minimum {MIN_F1_SCORE}"
    
    def test_customer_model_f1_score(self, transaction_data):
        """Test customer model F1 score >= 0.7"""
        model_path = MODELS_DIR / "customer_model.pkl"
        scaler_path = MODELS_DIR / "customer_scaler.pkl"
        
        if not model_path.exists():
            pytest.skip("Customer model not trained")
        
        # Load model and scaler
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Prepare customer-level features
        X, customer_ids = prepare_customer_features(transaction_data)
        X_scaled = scaler.transform(X)
        
        # Get customer-level labels
        if "is_anomaly" in transaction_data.columns:
            # Aggregate transaction labels to customer level
            customer_labels = transaction_data.groupby("customer_id")["is_anomaly"].max()
            y_true = np.array([customer_labels.get(cid, 0) for cid in customer_ids])
        else:
            pytest.skip("No labels in test data")
        
        # Predict
        predictions = model.predict(X_scaled)
        y_pred = (predictions == -1).astype(int)
        
        # Calculate F1 score
        from sklearn.metrics import f1_score
        f1 = f1_score(y_true, y_pred)
        
        print(f"\nCustomer Model F1 Score: {f1:.4f}")
        assert f1 >= MIN_F1_SCORE, f"F1 score {f1:.4f} below minimum {MIN_F1_SCORE}"


class TestSupervisedModelF1Scores:
    """Test supervised Random Forest models meet F1>=0.7 requirement"""
    
    @pytest.fixture
    def transaction_data(self):
        """Load transaction test data"""
        data_file = Path("data/raw/transaction_training_data.csv")
        if not data_file.exists():
            pytest.skip(f"Test data not found: {data_file}")
        
        df = pd.read_csv(data_file)
        test_df = df.sample(frac=0.2, random_state=42)
        return test_df
    
    @pytest.fixture
    def merged_data(self):
        """Load merged KYC+Business test data"""
        data_file = Path("data/raw/kyc_business_training_data.csv")
        if not data_file.exists():
            pytest.skip(f"Test data not found: {data_file}")
        
        df = pd.read_csv(data_file)
        test_df = df.sample(frac=0.2, random_state=42)
        return test_df
    
    def test_supervised_transaction_model_f1_score(self, transaction_data):
        """Test supervised transaction model F1 score >= 0.7"""
        model_path = MODELS_DIR / "transaction_supervised_model.pkl"
        scaler_path = MODELS_DIR / "transaction_supervised_scaler.pkl"
        
        if not model_path.exists():
            pytest.skip("Supervised transaction model not trained")
        
        # Load model and scaler
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Prepare features
        X = prepare_transaction_features(transaction_data)
        X_scaled = scaler.transform(X)
        
        # Get labels
        if "is_anomaly" in transaction_data.columns:
            y_true = transaction_data["is_anomaly"].values
        else:
            pytest.skip("No labels in test data")
        
        # Predict (supervised uses predict_proba)
        probabilities = model.predict_proba(X_scaled)
        y_pred = (probabilities[:, 1] > 0.5).astype(int)
        
        # Calculate F1 score
        from sklearn.metrics import f1_score
        f1 = f1_score(y_true, y_pred)
        
        print(f"\nSupervised Transaction Model F1 Score: {f1:.4f}")
        assert f1 >= MIN_F1_SCORE, f"F1 score {f1:.4f} below minimum {MIN_F1_SCORE}"
    
    def test_supervised_merged_model_f1_score(self, merged_data):
        """Test supervised merged model F1 score >= 0.7"""
        model_path = MODELS_DIR / "merged_supervised_model.pkl"
        scaler_path = MODELS_DIR / "merged_supervised_scaler.pkl"
        
        if not model_path.exists():
            pytest.skip("Supervised merged model not trained")
        
        # Load model and scaler
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Prepare features
        kyc_features = prepare_kyc_features(merged_data)
        biz_features = prepare_business_features(merged_data)
        X = np.column_stack([kyc_features, biz_features])
        X_scaled = scaler.transform(X)
        
        # Get labels
        if "is_anomaly" in merged_data.columns:
            y_true = merged_data["is_anomaly"].values
        else:
            pytest.skip("No labels in test data")
        
        # Predict
        probabilities = model.predict_proba(X_scaled)
        y_pred = (probabilities[:, 1] > 0.5).astype(int)
        
        # Calculate F1 score
        from sklearn.metrics import f1_score
        f1 = f1_score(y_true, y_pred)
        
        print(f"\nSupervised Merged Model F1 Score: {f1:.4f}")
        assert f1 >= MIN_F1_SCORE, f"F1 score {f1:.4f} below minimum {MIN_F1_SCORE}"
    
    def test_supervised_customer_model_f1_score(self, transaction_data):
        """Test supervised customer model F1 score >= 0.7"""
        model_path = MODELS_DIR / "customer_supervised_model.pkl"
        scaler_path = MODELS_DIR / "customer_supervised_scaler.pkl"
        
        if not model_path.exists():
            pytest.skip("Supervised customer model not trained")
        
        # Load model and scaler
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Prepare customer-level features
        X, customer_ids = prepare_customer_features(transaction_data)
        X_scaled = scaler.transform(X)
        
        # Get customer-level labels
        if "is_anomaly" in transaction_data.columns:
            customer_labels = transaction_data.groupby("customer_id")["is_anomaly"].max()
            y_true = np.array([customer_labels.get(cid, 0) for cid in customer_ids])
        else:
            pytest.skip("No labels in test data")
        
        # Predict
        probabilities = model.predict_proba(X_scaled)
        y_pred = (probabilities[:, 1] > 0.5).astype(int)
        
        # Calculate F1 score
        from sklearn.metrics import f1_score
        f1 = f1_score(y_true, y_pred)
        
        print(f"\nSupervised Customer Model F1 Score: {f1:.4f}")
        assert f1 >= MIN_F1_SCORE, f"F1 score {f1:.4f} below minimum {MIN_F1_SCORE}"


class TestModelPerformanceMetrics:
    """Additional performance metrics tests"""
    
    @pytest.fixture
    def transaction_data(self):
        """Load transaction test data"""
        data_file = Path("data/raw/transaction_training_data.csv")
        if not data_file.exists():
            pytest.skip(f"Test data not found: {data_file}")
        return pd.read_csv(data_file).sample(frac=0.2, random_state=42)
    
    def test_models_have_reasonable_precision_recall(self, transaction_data):
        """Test that models have balanced precision and recall"""
        from sklearn.metrics import precision_score, recall_score
        
        model_path = MODELS_DIR / "transaction_model.pkl"
        if not model_path.exists():
            pytest.skip("Transaction model not trained")
        
        model = joblib.load(model_path)
        scaler = joblib.load(MODELS_DIR / "transaction_scaler.pkl")
        
        X = prepare_transaction_features(transaction_data)
        X_scaled = scaler.transform(X)
        
        if "is_anomaly" not in transaction_data.columns:
            pytest.skip("No labels in test data")
        
        y_true = transaction_data["is_anomaly"].values
        predictions = model.predict(X_scaled)
        y_pred = (predictions == -1).astype(int)
        
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        
        print(f"\nPrecision: {precision:.4f}, Recall: {recall:.4f}")
        
        # At least one metric should be above 0.5
        assert precision >= 0.5 or recall >= 0.5, "Both precision and recall below 0.5"
    
    def test_no_model_drift_significant_features(self):
        """Test that models have feature importance distribution"""
        model_path = MODELS_DIR / "transaction_model.pkl"
        if not model_path.exists():
            pytest.skip("Transaction model not trained")
        
        model = joblib.load(model_path)
        
        # Check that model has feature_importances_ attribute (for supervised) 
        # or decision_path (for unsupervised)
        if hasattr(model, 'feature_importances_'):
            assert len(model.feature_importances_) > 0
            # At least 30% of features should have non-zero importance
            non_zero_count = np.sum(model.feature_importances_ > 0.001)
            assert non_zero_count / len(model.feature_importances_) >= 0.3
        elif hasattr(model, 'estimators_'):
            # Isolation Forest - check that estimators exist
            assert len(model.estimators_) > 0

