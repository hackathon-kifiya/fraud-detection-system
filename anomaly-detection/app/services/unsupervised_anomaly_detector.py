import os
from typing import Any, Dict, Tuple, List

import joblib
import numpy as np
import pandas as pd
from scipy.special import expit
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.core.config import settings
from app.core.logging import logger
from app.ml.preprocessing.feature_engineering.training_features import (
    prepare_combined_features_from_df, prepare_customer_features_from_df,
    prepare_transaction_features_from_df)
# For KYC individual predictions, use utils version
from app.ml.preprocessing.feature_engineering.utils import (
    prepare_kyc_features_from_df)
from app.models.schemas import CombinedKYCBusinessData, KYCData, RiskLevel, TransactionData
from app.services.explainer import ShapExplainerService


class UnsupervisedAnomalyDetectorService:
    """Service for anomaly detection using Isolation Forest"""

    def __init__(self):
        self.kyc_model: IsolationForest = None
        self.transaction_model: IsolationForest = None
        self.kyc_scaler: StandardScaler = None
        self.transaction_scaler: StandardScaler = None
        self.kyc_explainer: ShapExplainerService = None
        self.transaction_explainer: ShapExplainerService = None

        self.combined_model: IsolationForest = None
        self.combined_scaler: StandardScaler = None
        self.combined_explainer: ShapExplainerService = None

        self.customer_model: IsolationForest = None
        self.customer_scaler: StandardScaler = None
        self.customer_explainer: ShapExplainerService = None

        self.kyc_feature_names = [
            "age",
            "annual_income",
            "num_accounts",
            "account_age_days",
            "num_transactions_last_30d",
            "avg_transaction_amount",
        ]

        self.transaction_feature_names = [
            "amount",
            "transaction_type",
            "hour_of_day",
            "day_of_week",
            "distance_from_home",
            "is_online",
            "num_transactions_last_24h",
            "avg_amount_last_30d",
        ]

        self.combined_feature_names = [
            # KYC features (11 total)
            "customer_age",
            "customer_gender_encoded",
            "customer_marital_status_encoded",
            "customer_education_level_encoded",
            "customer_region_encoded",
            "customer_city_encoded",
            "customer_zone_encoded",
            "customer_woreda_numeric",
            "customer_phone_last_4",
            "customer_tin_length",
            "customer_account_length",
            # Business features (12 total)
            "business_establishment_year",
            "business_sector_encoded",
            "business_level_encoded",
            "business_starting_capital",
            "business_current_capital",
            "business_annual_profit",
            "business_annual_sales",
            "business_starting_no_of_employees",
            "business_current_no_of_employees",
            "business_source_encoded",
            "business_association_encoded",
            "capital_growth",
            "employee_growth",
            "profit_margin",
            "business_age",
        ]

        self.customer_feature_names = [
            "customer_id",
            "customer_age",
            "customer_gender_encoded",
            "customer_marital_status_encoded",
            "customer_education_level_encoded",
            "customer_region_encoded",
            "customer_city_encoded",
            "customer_zone_encoded",
            "customer_woreda_numeric",
            "customer_phone_last_4",
            "customer_tin_length",
            "customer_account_length",
        ]

    async def initialize(self):
        """Initialize models and explainers"""
        logger.info("Initializing anomaly detection service...")

        # Try to load existing models
        models_exist = self._check_models_exist()

        if models_exist:
            self._load_models()
            self._initialize_explainers()
        else:
            logger.warning(
                "Models not found. Training new models with synthetic data..."
            )
            raise Exception(
                "Models not found. Training new models with synthetic data..."
            )

    def _check_models_exist(self) -> bool:
        """Check if model files exist"""
        # Check for required models (customer and transaction)
        required_files = [
            settings.CUSTOMER_MODEL_PATH,
            settings.TRANSACTION_MODEL_PATH,
            settings.CUSTOMER_SCALER_PATH,
            settings.COMBINED_MODEL_PATH,
            settings.COMBINED_SCALER_PATH,
            settings.TRANSACTION_SCALER_PATH,
        ]
        return all(os.path.exists(f) for f in required_files)

    def _load_models(self):
        """Load pre-trained models from disk"""
        logger.info("Loading models from disk...")

        # Load required KYC/customer models (aliased to customer)
        self.kyc_model = joblib.load(settings.KYC_MODEL_PATH)  # Points to customer_model
        self.kyc_scaler = joblib.load(settings.KYC_SCALER_PATH)  # Points to customer_scaler
        
        # Also load as customer_model for batch predictions
        self.customer_model = self.kyc_model
        self.customer_scaler = self.kyc_scaler

        # Load transaction models
        self.transaction_model = joblib.load(settings.TRANSACTION_MODEL_PATH)
        self.transaction_scaler = joblib.load(settings.TRANSACTION_SCALER_PATH)

        self.combined_model = joblib.load(settings.COMBINED_MODEL_PATH)
        self.combined_scaler = joblib.load(settings.COMBINED_SCALER_PATH)

        # Customer model is already loaded (same as kyc_model)
        # The separate customer_model is for batch predictions
        logger.info("Customer model ready (shared with KYC model)")

        logger.info("Models loaded successfully!")

    def _initialize_explainers(self):
        """Initialize SHAP explainers"""
        logger.info("Initializing SHAP explainers...")

        # Try to initialize explainers, but don't fail if they can't be initialized
        try:
            logger.info("Loading background data for KYC explainer...")
            kyc_background = self._load_background_data("kyc")
            logger.info(f"KYC background data shape: {kyc_background.shape}")
            
            logger.info("Creating KYC SHAP explainer...")
            self.kyc_explainer = ShapExplainerService(
                self.kyc_model, kyc_background, self.kyc_feature_names
            )
            logger.info("KYC explainer created successfully")
        except Exception as e:
            logger.warning(f"Could not initialize KYC explainer: {e}")
            self.kyc_explainer = None

        try:
            logger.info("Loading background data for transaction explainer...")
            txn_background = self._load_background_data("transaction")
            logger.info(f"Transaction background data shape: {txn_background.shape}")
            
            logger.info("Creating transaction SHAP explainer...")
            self.transaction_explainer = ShapExplainerService(
                self.transaction_model, txn_background, self.transaction_feature_names
            )
            logger.info("Transaction explainer created successfully")
        except Exception as e:
            logger.warning(f"Could not initialize transaction explainer: {e}")
            self.transaction_explainer = None

        # Initialize combined explainer if model exists
        if self.combined_model is not None:
            try:
                logger.info("Loading background data for combined explainer...")
                combined_background = self._load_background_data("combined")
                logger.info(f"Combined background data shape: {combined_background.shape}")
                logger.info("Creating combined SHAP explainer...")
                self.combined_explainer = ShapExplainerService(
                    self.combined_model,
                    combined_background,
                    self.combined_feature_names,
                )
                logger.info("Combined explainer created successfully")
            except Exception as e:
                logger.warning(f"Could not initialize combined explainer: {e}")
                self.combined_explainer = None

        # Initialize customer explainer if model exists
        if self.customer_model is not None:
            try:
                logger.info("Loading background data for customer explainer...")
                customer_background = self._load_background_data("customer")
                logger.info(f"Customer background data shape: {customer_background.shape}")
                logger.info("Creating customer SHAP explainer...")
                self.customer_explainer = ShapExplainerService(
                    self.customer_model,
                    customer_background,
                    self.customer_feature_names,
                )
                logger.info("Customer explainer created successfully")
            except Exception as e:
                logger.warning(f"Could not initialize customer explainer: {e}")
                self.customer_explainer = None

        logger.info("SHAP explainer initialization complete!")

    def _load_background_data(
        self, model_type: str, n_samples: int = 100
    ) -> np.ndarray:
        """Load background data from training files for SHAP with caching"""
        from pathlib import Path

        # Cache directory for background data
        cache_dir = Path("data/models/unsupervised/background_cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache file path
        cache_file = cache_dir / f"{model_type}_background_{n_samples}.npy"
        
        # Try to load from cache first
        if cache_file.exists():
            try:
                logger.info(f"Loading cached background data for {model_type}...")
                return np.load(cache_file)
            except Exception as e:
                logger.warning(f"Failed to load cached background data: {e}, regenerating...")

        # If cache doesn't exist or failed, generate from raw data
        data_dir = Path("data/raw")

        try:
            if model_type == "kyc":
                # KYC model is aliased to customer model, so use customer features
                df = pd.read_csv(data_dir / "transaction_training_data.csv")
                df_normal = df[df["is_anomaly"] == 0]
                customer_ids = df_normal["customer_id"].unique()
                sampled_customers = np.random.choice(
                    customer_ids, min(n_samples, len(customer_ids)), replace=False
                )
                features = prepare_customer_features_from_df(
                    df_normal[df_normal["customer_id"].isin(sampled_customers)]
                )
                background_data = self.kyc_scaler.transform(features)
                
                # Cache the result
                np.save(cache_file, background_data)
                logger.info(f"Cached background data for {model_type}")
                return background_data

            elif model_type == "transaction":
                df = pd.read_csv(data_dir / "transaction_training_data.csv")
                df_normal = df[df["is_anomaly"] == 0].sample(
                    n=min(n_samples, len(df)), random_state=42
                )
                features = prepare_transaction_features_from_df(df_normal)
                background_data = self.transaction_scaler.transform(features)
                
                # Cache the result
                np.save(cache_file, background_data)
                logger.info(f"Cached background data for {model_type}")
                return background_data

            elif model_type == "combined":
                df = pd.read_csv(data_dir / "kyc_business_training_data.csv")
                df_normal = df[df["is_anomaly"] == 0].sample(
                    n=min(n_samples, len(df)), random_state=42
                )
                features = prepare_combined_features_from_df(df_normal)
                background_data = self.combined_scaler.transform(features)
                
                # Cache the result
                np.save(cache_file, background_data)
                logger.info(f"Cached background data for {model_type}")
                return background_data

            elif model_type == "customer":
                df = pd.read_csv(data_dir / "transaction_training_data.csv")
                df_normal = df[df["is_anomaly"] == 0]
                customer_ids = df_normal["customer_id"].unique()
                sampled_customers = np.random.choice(
                    customer_ids, min(n_samples, len(customer_ids)), replace=False
                )
                features = prepare_customer_features_from_df(
                    df_normal[df_normal["customer_id"].isin(sampled_customers)]
                )
                background_data = self.customer_scaler.transform(features)
                
                # Cache the result
                np.save(cache_file, background_data)
                logger.info(f"Cached background data for {model_type}")
                return background_data

        except FileNotFoundError:
            logger.warning(
                f"Training data not found, generating synthetic background data for {model_type}"
            )
            return self._generate_synthetic_background(model_type, n_samples)

    def _generate_synthetic_background(
        self, model_type: str, n_samples: int
    ) -> np.ndarray:
        """Fallback: Generate synthetic background data"""
        np.random.seed(42)

        if model_type == "kyc":
            # Generate synthetic KYC features
            background = np.random.randn(n_samples, len(self.kyc_feature_names))
            background[:, 0] = background[:, 0] * 15 + 45  # age
            return self.kyc_scaler.transform(background)

        elif model_type == "transaction":
            background = np.random.randn(n_samples, len(self.transaction_feature_names))
            return self.transaction_scaler.transform(background)

        elif model_type == "combined":
            background = np.random.randn(n_samples, len(self.combined_feature_names))
            return self.combined_scaler.transform(background)

        elif model_type == "customer":
            background = np.random.randn(n_samples, len(self.customer_feature_names))
            return self.customer_scaler.transform(background)

        return np.random.randn(n_samples, 10)

    def extract_kyc_features(self, data: KYCData) -> np.ndarray:
        """Extract KYC features using feature engineering pipeline"""
        # Convert Pydantic model to DataFrame
        data_dict = data.model_dump()
        df = pd.DataFrame([data_dict])
        
        # Use existing feature engineering function
        from app.ml.preprocessing.feature_engineering.prepare_merged_data import prepare_kyc_features
        features = prepare_kyc_features(df)
        return features

    def extract_transaction_features(self, data: TransactionData) -> np.ndarray:
        """Extract transaction features using feature engineering pipeline"""
        # Convert Pydantic model to DataFrame
        data_dict = data.model_dump()
        df = pd.DataFrame([data_dict])
        
        # Use existing feature engineering function
        from app.ml.preprocessing.feature_engineering.prepare_transaction import prepare_transaction_features
        features = prepare_transaction_features(df)
        return features

    def predict_kyc(
        self, data: KYCData
    ) -> Tuple[bool, float, RiskLevel, Dict[str, Any]]:
        """Predict KYC anomaly with explanation"""
        features = self.extract_kyc_features(data)
        scaled_features = self.kyc_scaler.transform(features)

        prediction = self.kyc_model.predict(scaled_features)[0]
        raw_score = self.kyc_model.score_samples(scaled_features)[0]
        # Normalize score to 0-1 range
        score = self._normalize_score(raw_score)

        is_anomaly = prediction == -1
        risk_level = self._calculate_risk_level(score)
        
        # Get explanation if explainer is available
        if self.kyc_explainer is not None:
            explanation = self.kyc_explainer.explain(scaled_features)
        else:
            # Return basic explanation without SHAP
            explanation = {
                "top_contributing_features": {
                    "Note": "SHAP explanations unavailable. Model loaded without explainers."
                },
                "feature_values": {name: float(val) for name, val in zip(self.kyc_feature_names, scaled_features[0])},
                "shap_values": {},
            }

        return is_anomaly, float(score), risk_level, explanation

    def predict_transaction(
        self, data: TransactionData
    ) -> Tuple[bool, float, RiskLevel, Dict[str, Any]]:
        """Predict transaction anomaly with explanation"""
        features = self.extract_transaction_features(data)
        scaled_features = self.transaction_scaler.transform(features)

        prediction = self.transaction_model.predict(scaled_features)[0]
        raw_score = self.transaction_model.score_samples(scaled_features)[0]
        # Normalize score to 0-1 range
        score = self._normalize_score(raw_score)

        is_anomaly = prediction == -1
        risk_level = self._calculate_risk_level(score)
        
        # Get explanation if explainer is available
        if self.transaction_explainer is not None:
            explanation = self.transaction_explainer.explain(scaled_features)
        else:
            # Return basic explanation without SHAP
            explanation = {
                "top_contributing_features": {
                    "Note": "SHAP explanations unavailable. Model loaded without explainers."
                },
                "feature_values": {name: float(val) for name, val in zip(self.transaction_feature_names, scaled_features[0])},
                "shap_values": {},
            }

        return is_anomaly, float(score), risk_level, explanation

    def predict_combined(
        self, data: CombinedKYCBusinessData
    ) -> Tuple[bool, float, RiskLevel, Dict[str, Any]]:
        """
        Predict anomaly for combined KYC and business data
        
        Args:
            data: CombinedKYCBusinessData containing both KYC and business information
            
        Returns:
            Tuple of (is_anomaly, score, risk_level, explanation)
            - is_anomaly: Boolean indicating if record is anomalous
            - score: Anomaly score from model (lower = more anomalous)
            - risk_level: RiskLevel enum (HIGH, MEDIUM, LOW)
            - explanation: SHAP explanation dictionary
            
        Raises:
            ValueError: If combined model is not available
        """
        # Check if combined model is available
        if self.combined_model is None or self.combined_scaler is None:
            raise ValueError(
                "Combined model not available. Please ensure combined model files exist and are loaded."
            )
        
        # Convert combined data to DataFrame format for feature preparation
        data_dict = data.model_dump()
        df = pd.DataFrame([data_dict])
        
        # Extract combined features (KYC + Business)
        features = prepare_combined_features_from_df(df)
        logger.debug(f"Combined features shape: {features.shape}, expected by model: {len(self.combined_feature_names)}")
        scaled_features = self.combined_scaler.transform(features)
        
        # Make predictions
        prediction = self.combined_model.predict(scaled_features)[0]
        raw_score = self.combined_model.score_samples(scaled_features)[0]
        # Normalize score to 0-1 range
        score = self._normalize_score(raw_score)
        
        is_anomaly = prediction == -1
        risk_level = self._calculate_risk_level(score)
        
        # Get explanation if explainer is available
        if self.combined_explainer is not None:
            explanation = self.combined_explainer.explain(scaled_features)
        else:
            # Return basic explanation without SHAP
            explanation = {
                "top_contributing_features": {
                    "Note": "SHAP explanations unavailable. Model loaded without explainers."
                },
                "feature_values": {name: float(val) for name, val in zip(self.combined_feature_names, scaled_features[0])},
                "shap_values": {},
            }
        
        return is_anomaly, float(score), risk_level, explanation

    def _normalize_score(self, raw_score: float) -> float:
        """
        Normalize Isolation Forest score to 0-1 range
        
        Isolation Forest returns scores where:
        - Negative values indicate anomalies
        - Positive values indicate normal behavior
        
        We normalize using sigmoid: 1 / (1 + exp(score))
        This maps negative scores (anomalies) to values closer to 1
        and positive scores (normal) to values closer to 0
        """
        # Apply sigmoid to normalize to 0-1
        normalized = expit(raw_score)
        
        # Invert so that negative scores (anomalies) map to high values
        # and positive scores (normal) map to low values
        return 1.0 - normalized

    def _calculate_risk_level(self, score: float) -> RiskLevel:
        """Calculate risk level based on normalized score (0-1 range, higher = more anomalous)"""
        # Convert threshold from raw score to normalized score
        high_threshold_normalized = self._normalize_score(settings.UNSUPERVISED_HIGH_RISK_THRESHOLD)
        medium_threshold_normalized = self._normalize_score(settings.UNSUPERVISED_MEDIUM_RISK_THRESHOLD)
        
        if score >= high_threshold_normalized:
            return RiskLevel.HIGH
        elif score >= medium_threshold_normalized:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def predict_customer_batch(
        self, customer_id: str, transactions: list
    ) -> Tuple[bool, float, RiskLevel, List[Tuple[bool, float, RiskLevel, Dict[str, Any]]]]:
        """
        Predict anomalies for multiple transactions from a single customer
        
        This method aggregates transaction-level anomalies to produce a customer-level
        risk assessment. It processes all transactions and calculates:
        - Individual transaction predictions
        - Aggregated customer anomaly score (average of transaction scores)
        - Customer-level risk classification
        - Whether customer should be flagged based on anomaly ratio
        
        Args:
            customer_id: Customer ID string
            transactions: List of TransactionData objects for the customer
            
        Returns:
            Tuple of:
            - customer_flagged: Boolean indicating if customer should be flagged
            - customer_anomaly_score: Aggregated anomaly score (0-1)
            - customer_risk_level: RiskLevel enum for customer
            - transaction_results: List of tuples (is_anomaly, score, risk_level, explanation) for each transaction
        """
        if not transactions:
            raise ValueError("At least one transaction is required for batch prediction")
        
        transaction_results = []
        anomaly_scores = []
        anomaly_count = 0
        high_risk_count = 0
        
        # Process each transaction
        for transaction in transactions:
            is_anomaly, score, risk_level, explanation = self.predict_transaction(transaction)
            
            transaction_results.append((is_anomaly, float(score), risk_level, explanation))
            anomaly_scores.append(float(score))
            
            if is_anomaly:
                anomaly_count += 1
            
            if risk_level == RiskLevel.HIGH:
                high_risk_count += 1
        
        # Calculate aggregated customer metrics
        # Use the mean of transaction scores as customer score
        customer_anomaly_score = float(np.mean(anomaly_scores))
        
        # Calculate customer risk level based on aggregated score
        customer_risk_level = self._calculate_risk_level(customer_anomaly_score)
        
        # Flag customer if:
        # 1. Anomaly ratio > 30% of transactions, OR
        # 2. More than 20% of transactions are high risk, OR
        # 3. Customer risk level is HIGH
        anomaly_ratio = anomaly_count / len(transactions)
        high_risk_ratio = high_risk_count / len(transactions)
        
        customer_flagged = (
            anomaly_ratio > 0.3 or 
            high_risk_ratio > 0.2 or 
            customer_risk_level == RiskLevel.HIGH
        )
        
        return customer_flagged, customer_anomaly_score, customer_risk_level, transaction_results
