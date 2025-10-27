"""
Supervised Anomaly Detection Service using Random Forest
"""
import os
from typing import Any, Dict, Tuple, List

import joblib
import numpy as np
import pandas as pd

from app.core.config import settings
from app.core.logging import logger
from app.ml.preprocessing.feature_engineering.training_features import (
    prepare_combined_features_from_df,
    prepare_customer_features_from_df,
    prepare_kyc_features_from_df,
    prepare_transaction_features_from_df,
)
from app.models.schemas import CombinedKYCBusinessData, KYCData, RiskLevel, TransactionData
from app.services.explainer import ShapExplainerService


class SupervisedAnomalyDetectorService:
    """Service for anomaly detection using Random Forest (Supervised)"""

    def __init__(self):
        self.kyc_model = None
        self.transaction_model = None
        self.kyc_scaler = None
        self.transaction_scaler = None
        self.kyc_explainer = None
        self.transaction_explainer = None

        self.combined_model = None
        self.combined_scaler = None
        self.combined_explainer = None

        self.customer_model = None
        self.customer_scaler = None
        self.customer_explainer = None

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
        """Initialize supervised models and explainers"""
        logger.info("Initializing supervised anomaly detection service...")

        # Try to load existing models
        models_exist = self._check_models_exist()

        if models_exist:
            self._load_models()
            self._initialize_explainers()
        else:
            logger.warning(
                "Supervised models not found. Please train supervised models first..."
            )
            raise Exception(
                "Supervised models not found. Please train supervised models first..."
            )

    def _check_models_exist(self) -> bool:
        """Check if supervised model files exist"""
        # At minimum, customer/kyc models must exist
        required_files = [
            settings.KYC_SUPERVISED_MODEL_PATH,
            settings.KYC_SUPERVISED_SCALER_PATH,
        ]
        
        if not all(os.path.exists(f) for f in required_files):
            return False
        
        # Transaction models are optional
        # Combined models are optional
        return True

    def _load_models(self):
        """Load pre-trained supervised models from disk"""
        logger.info("Loading supervised models from disk...")

        try:
            # Load KYC model (required) - this is aliased to customer_rf_model
            self.kyc_model = joblib.load(settings.KYC_SUPERVISED_MODEL_PATH)
            self.kyc_scaler = joblib.load(settings.KYC_SUPERVISED_SCALER_PATH)
            
            # Customer model is the same as KYC model
            self.customer_model = self.kyc_model
            self.customer_scaler = self.kyc_scaler

            # Load transaction model if available (optional)
            if os.path.exists(settings.TRANSACTION_SUPERVISED_MODEL_PATH) and os.path.exists(settings.TRANSACTION_SUPERVISED_SCALER_PATH):
                self.transaction_model = joblib.load(
                    settings.TRANSACTION_SUPERVISED_MODEL_PATH
                )
                self.transaction_scaler = joblib.load(
                    settings.TRANSACTION_SUPERVISED_SCALER_PATH
                )
                logger.info("Transaction supervised model loaded successfully")
            else:
                logger.warning("Transaction supervised model not found, transaction predictions will not be available")
                self.transaction_model = None
                self.transaction_scaler = None

            # Load optional combined model if available
            if (
                os.path.exists(settings.COMBINED_SUPERVISED_MODEL_PATH)
                and os.path.exists(settings.COMBINED_SUPERVISED_SCALER_PATH)
            ):
                self.combined_model = joblib.load(
                    settings.COMBINED_SUPERVISED_MODEL_PATH
                )
                self.combined_scaler = joblib.load(
                    settings.COMBINED_SUPERVISED_SCALER_PATH
                )
                logger.info("Combined supervised model loaded successfully")
            else:
                logger.warning(
                    "Combined supervised model files not found, combined predictions will not be available"
                )

            # Customer model is already loaded (same as kyc_model)
            logger.info("Customer supervised model ready (shared with KYC model)")

            logger.info("Supervised models loaded successfully!")

        except Exception as e:
            logger.error(f"Error loading supervised models: {e}")
            raise

    def _initialize_explainers(self):
        """Initialize SHAP explainers for supervised models"""
        logger.info("Initializing SHAP explainers for supervised models...")

        try:
            kyc_background = self._load_background_data("kyc")
            txn_background = self._load_background_data("transaction")

            self.kyc_explainer = ShapExplainerService(
                self.kyc_model, kyc_background, self.kyc_feature_names
            )
            self.transaction_explainer = ShapExplainerService(
                self.transaction_model, txn_background, self.transaction_feature_names
            )

            # Initialize combined explainer if model exists
            if self.combined_model is not None:
                combined_background = self._load_background_data("combined")
                self.combined_explainer = ShapExplainerService(
                    self.combined_model,
                    combined_background,
                    self.combined_feature_names,
                )

            # Initialize customer explainer if model exists
            if self.customer_model is not None:
                customer_background = self._load_background_data("customer")
                self.customer_explainer = ShapExplainerService(
                    self.customer_model,
                    customer_background,
                    self.customer_feature_names,
                )

            logger.info("SHAP explainers initialized successfully!")
        except Exception as e:
            logger.error(f"Error initializing SHAP explainers: {e}")
            raise

    def _load_background_data(
        self, model_type: str, n_samples: int = 100
    ) -> np.ndarray:
        """Load background data from training files for SHAP"""
        from pathlib import Path

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
                return self.kyc_scaler.transform(features)

            elif model_type == "transaction":
                df = pd.read_csv(data_dir / "transaction_training_data.csv")
                df_normal = df[df["is_anomaly"] == 0].sample(
                    n=min(n_samples, len(df)), random_state=42
                )
                features = prepare_transaction_features_from_df(df_normal)
                return self.transaction_scaler.transform(features)

            elif model_type == "combined":
                df = pd.read_csv(data_dir / "kyc_business_training_data.csv")
                df_normal = df[df["is_anomaly"] == 0].sample(
                    n=min(n_samples, len(df)), random_state=42
                )
                features = prepare_combined_features_from_df(df_normal)
                return self.combined_scaler.transform(features)

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
                return self.customer_scaler.transform(features)

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

    def predict_kyc(
        self, data: KYCData
    ) -> Tuple[bool, float, RiskLevel, Dict[str, Any]]:
        """
        Predict KYC anomaly with explanation using supervised model
        
        Returns:
            Tuple of (is_anomaly, confidence_score, risk_level, explanation)
        """
        features = self._extract_kyc_features(data)
        scaled_features = self.kyc_scaler.transform(features)

        # Get prediction and probability
        prediction = self.kyc_model.predict(scaled_features)[0]
        probabilities = self.kyc_model.predict_proba(scaled_features)[0]

        # Probability of being anomaly (class 1)
        anomaly_probability = probabilities[1]

        is_anomaly = prediction == 1
        risk_level = self._calculate_risk_level(anomaly_probability)
        explanation = self.kyc_explainer.explain(scaled_features)

        return is_anomaly, float(anomaly_probability), risk_level, explanation

    def predict_transaction(
        self, data: TransactionData
    ) -> Tuple[bool, float, RiskLevel, Dict[str, Any]]:
        """
        Predict transaction anomaly with explanation using supervised model
        
        Returns:
            Tuple of (is_anomaly, confidence_score, risk_level, explanation)
        """
        features = self._extract_transaction_features(data)
        scaled_features = self.transaction_scaler.transform(features)

        # Get prediction and probability
        prediction = self.transaction_model.predict(scaled_features)[0]
        probabilities = self.transaction_model.predict_proba(scaled_features)[0]

        # Probability of being anomaly (class 1)
        anomaly_probability = probabilities[1]

        is_anomaly = prediction == 1
        risk_level = self._calculate_risk_level(anomaly_probability)
        explanation = self.transaction_explainer.explain(scaled_features)

        return is_anomaly, float(anomaly_probability), risk_level, explanation

    def predict_combined(
        self, data: CombinedKYCBusinessData
    ) -> Tuple[bool, float, RiskLevel, Dict[str, Any]]:
        """
        Predict anomaly for combined KYC and business data using supervised model
        
        Returns:
            Tuple of (is_anomaly, confidence_score, risk_level, explanation)
            
        Raises:
            ValueError: If combined model is not available
        """
        if self.combined_model is None or self.combined_scaler is None:
            raise ValueError(
                "Combined supervised model not available. Please train the combined model first."
            )

        if self.combined_explainer is None:
            raise ValueError(
                "Combined explainer not initialized. Please ensure the service is properly initialized."
            )

        data_dict = data.model_dump()
        df = pd.DataFrame([data_dict])

        features = prepare_combined_features_from_df(df)
        scaled_features = self.combined_scaler.transform(features)

        # Get prediction and probability
        prediction = self.combined_model.predict(scaled_features)[0]
        probabilities = self.combined_model.predict_proba(scaled_features)[0]

        # Probability of being anomaly (class 1)
        anomaly_probability = probabilities[1]

        is_anomaly = prediction == 1
        risk_level = self._calculate_risk_level(anomaly_probability)
        explanation = self.combined_explainer.explain(scaled_features)

        return is_anomaly, float(anomaly_probability), risk_level, explanation

    def predict_customer_batch(
        self, customer_id: str, transactions: list
    ) -> Tuple[bool, float, RiskLevel, List[Tuple[bool, float, RiskLevel, Dict[str, Any]]]]:
        """
        Predict anomalies for multiple transactions from a single customer
        
        Aggregates transaction-level predictions to produce customer-level risk assessment
        
        Returns:
            Tuple of:
            - customer_flagged: Boolean indicating if customer should be flagged
            - customer_anomaly_score: Aggregated anomaly probability (0-1)
            - customer_risk_level: RiskLevel enum for customer
            - transaction_results: List of tuples for each transaction
        """
        if not transactions:
            raise ValueError("At least one transaction is required for batch prediction")

        transaction_results = []
        anomaly_scores = []
        anomaly_count = 0
        high_risk_count = 0

        # Process each transaction
        for transaction in transactions:
            is_anomaly, score, risk_level, explanation = self.predict_transaction(
                transaction
            )

            transaction_results.append((is_anomaly, float(score), risk_level, explanation))
            anomaly_scores.append(float(score))

            if is_anomaly:
                anomaly_count += 1

            if risk_level == RiskLevel.HIGH:
                high_risk_count += 1

        # Calculate aggregated customer metrics
        customer_anomaly_score = float(np.mean(anomaly_scores))
        customer_risk_level = self._calculate_risk_level(customer_anomaly_score)

        # Flag customer if:
        # 1. Anomaly ratio > 30% of transactions, OR
        # 2. More than 20% of transactions are high risk, OR
        # 3. Customer risk level is HIGH
        anomaly_ratio = anomaly_count / len(transactions)
        high_risk_ratio = high_risk_count / len(transactions)

        customer_flagged = (
            anomaly_ratio > 0.3
            or high_risk_ratio > 0.2
            or customer_risk_level == RiskLevel.HIGH
        )

        return customer_flagged, customer_anomaly_score, customer_risk_level, transaction_results

    def _extract_kyc_features(self, data: KYCData) -> np.ndarray:
        """Extract KYC features using feature engineering pipeline"""
        # Convert Pydantic model to DataFrame
        data_dict = data.model_dump()
        df = pd.DataFrame([data_dict])
        
        # Use KYC feature engineering function
        features = prepare_kyc_features_from_df(df)
        return features

    def _extract_transaction_features(self, data: TransactionData) -> np.ndarray:
        """Extract transaction features using feature engineering pipeline"""
        # Convert Pydantic model to DataFrame
        data_dict = data.model_dump()
        df = pd.DataFrame([data_dict])
        
        # Use transaction feature engineering function
        features = prepare_transaction_features_from_df(df)
        return features

    def _calculate_risk_level(self, probability: float) -> RiskLevel:
        """Calculate risk level based on anomaly probability (0-1)"""
        if probability >= settings.SUPERVISED_HIGH_RISK_THRESHOLD:
            return RiskLevel.HIGH
        elif probability >= settings.SUPERVISED_MEDIUM_RISK_THRESHOLD:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

