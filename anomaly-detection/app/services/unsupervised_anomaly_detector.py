import os
from typing import Any, Dict, Tuple, List

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.core.config import settings
from app.core.logging import logger
from app.ml.preprocessing.feature_engineering.utils import (
    prepare_combined_features_from_df, prepare_customer_features_from_df,
    prepare_kyc_features_from_df, prepare_transaction_features_from_df)
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
        required_files = [
            settings.KYC_MODEL_PATH,
            settings.TRANSACTION_MODEL_PATH,
            settings.KYC_SCALER_PATH,
            settings.TRANSACTION_SCALER_PATH,
        ]
        return all(os.path.exists(f) for f in required_files)

    def _load_models(self):
        """Load pre-trained models from disk"""
        logger.info("Loading models from disk...")

        # Load required KYC and transaction models
        self.kyc_model = joblib.load(settings.KYC_MODEL_PATH)
        self.kyc_scaler = joblib.load(settings.KYC_SCALER_PATH)

        self.transaction_model = joblib.load(settings.TRANSACTION_MODEL_PATH)
        self.transaction_scaler = joblib.load(settings.TRANSACTION_SCALER_PATH)

        # Load optional combined model if available
        try:
            if os.path.exists(settings.COMBINED_MODEL_PATH) and os.path.exists(settings.COMBINED_SCALER_PATH):
                self.combined_model = joblib.load(settings.COMBINED_MODEL_PATH)
                self.combined_scaler = joblib.load(settings.COMBINED_SCALER_PATH)
                logger.info("Combined model loaded successfully")
            else:
                logger.warning("Combined model files not found, combined predictions will not be available")
        except Exception as e:
            logger.warning(f"Failed to load combined model: {e}")
            self.combined_model = None
            self.combined_scaler = None

        try:
            if os.path.exists(settings.CUSTOMER_MODEL_PATH) and os.path.exists(settings.CUSTOMER_SCALER_PATH):
                self.customer_model = joblib.load(settings.CUSTOMER_MODEL_PATH)
                self.customer_scaler = joblib.load(settings.CUSTOMER_SCALER_PATH)
                logger.info("Customer model loaded successfully")
            else:
                logger.warning("Customer model files not found, customer predictions will not be available")
        except Exception as e:
            logger.warning(f"Failed to load customer model: {e}")
            self.customer_model = None
            self.customer_scaler = None

        logger.info("Models loaded successfully!")

    def _initialize_explainers(self):
        """Initialize SHAP explainers"""
        logger.info("Initializing SHAP explainers...")

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
                df = pd.read_csv(data_dir / "kyc_training_data.csv")
                # Sample normal records only
                df_normal = df[df["is_anomaly"] == 0].sample(
                    n=min(n_samples, len(df)), random_state=42
                )
                features = prepare_kyc_features_from_df(df_normal)
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
        """Extract features from KYC data"""
        return np.array(
            [
                [
                    data.age,
                    data.annual_income,
                    data.num_accounts,
                    data.account_age_days,
                    data.num_transactions_last_30d,
                    data.avg_transaction_amount,
                ]
            ]
        )

    def extract_transaction_features(self, data: TransactionData) -> np.ndarray:
        """Extract features from transaction data"""
        transaction_type_map = {
            "purchase": 0,
            "withdrawal": 1,
            "transfer": 2,
            "deposit": 3,
        }

        return np.array(
            [
                [
                    data.amount,
                    transaction_type_map[data.transaction_type],
                    data.hour_of_day,
                    data.day_of_week,
                    data.distance_from_home,
                    int(data.is_online),
                    data.num_transactions_last_24h,
                    data.avg_amount_last_30d,
                ]
            ]
        )

    def predict_kyc(
        self, data: KYCData
    ) -> Tuple[bool, float, RiskLevel, Dict[str, Any]]:
        """Predict KYC anomaly with explanation"""
        features = self.extract_kyc_features(data)
        scaled_features = self.kyc_scaler.transform(features)

        prediction = self.kyc_model.predict(scaled_features)[0]
        score = self.kyc_model.score_samples(scaled_features)[0]

        is_anomaly = prediction == -1
        risk_level = self._calculate_risk_level(score)
        explanation = self.kyc_explainer.explain(scaled_features)

        return is_anomaly, float(score), risk_level, explanation

    def predict_transaction(
        self, data: TransactionData
    ) -> Tuple[bool, float, RiskLevel, Dict[str, Any]]:
        """Predict transaction anomaly with explanation"""
        features = self.extract_transaction_features(data)
        scaled_features = self.transaction_scaler.transform(features)

        prediction = self.transaction_model.predict(scaled_features)[0]
        raw_score = np.array(self.transaction_model.score_samples(scaled_features)).reshape(-1,1)

        inverse_score = 1 - raw_score

        # normalize the score to be between 0 and 1 where 1 is the most anomalous
        score = (raw_score - raw_score.min()) / (raw_score.max() - raw_score.min())


        is_anomaly = prediction == -1
        risk_level = self._calculate_risk_level(score)
        explanation = self.transaction_explainer.explain(scaled_features)

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
        
        if self.combined_explainer is None:
            raise ValueError(
                "Combined explainer not initialized. Please ensure the service is properly initialized."
            )
        
        # Convert combined data to DataFrame format for feature preparation
        data_dict = data.model_dump()
        df = pd.DataFrame([data_dict])
        
        # Extract combined features (KYC + Business)
        features = prepare_combined_features_from_df(df)
        scaled_features = self.combined_scaler.transform(features)
        
        # Make predictions
        prediction = self.combined_model.predict(scaled_features)[0]
        score = self.combined_model.score_samples(scaled_features)[0]
        
        is_anomaly = prediction == -1
        risk_level = self._calculate_risk_level(score)
        explanation = self.combined_explainer.explain(scaled_features)
        
        return is_anomaly, float(score), risk_level, explanation

    def _calculate_risk_level(self, score: float) -> RiskLevel:
        """Calculate risk level based on anomaly score"""
        if score < settings.HIGH_RISK_THRESHOLD:
            return RiskLevel.HIGH
        elif score < settings.MEDIUM_RISK_THRESHOLD:
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
