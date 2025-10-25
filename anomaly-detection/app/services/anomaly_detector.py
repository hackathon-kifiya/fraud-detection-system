"""
Anomaly Detection Service
Handles model loading, prediction, and SHAP explanations
"""
import os
from typing import Any, Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.core.config import settings
from app.core.logging import get_logger
from app.models.schemas import KYCData, RiskLevel, TransactionData
from app.services.explainer import ShapExplainerService

logger = get_logger(__name__)


class AnomalyDetectorService:
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
            "credit_score",
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

    async def initialize(self):
        """Initialize models and explainers"""
        logger.info("Initializing anomaly detection service...")

        # Try to load existing models
        models_exist = self._check_models_exist()

        if models_exist:
            self._load_models()
        else:
            logger.warning(
                "Models not found. Training new models with synthetic data..."
            )
            self._train_models()

        # Initialize SHAP explainers
        self._initialize_explainers()

        logger.info("Anomaly detection service initialized successfully!")

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

        self.kyc_model = joblib.load(settings.KYC_MODEL_PATH)
        self.transaction_model = joblib.load(settings.TRANSACTION_MODEL_PATH)
        self.kyc_scaler = joblib.load(settings.KYC_SCALER_PATH)
        self.transaction_scaler = joblib.load(settings.TRANSACTION_SCALER_PATH)

        logger.info("Models loaded successfully!")

    def _train_models(self):
        """Train models with synthetic data (for demo purposes)"""
        logger.info("Training models with synthetic data...")

        np.random.seed(settings.RANDOM_STATE)

        # Generate KYC training data
        kyc_train_data = self._generate_synthetic_kyc_data(1000)
        self.kyc_scaler = StandardScaler()
        kyc_scaled = self.kyc_scaler.fit_transform(kyc_train_data)

        self.kyc_model = IsolationForest(
            contamination=settings.CONTAMINATION,
            random_state=settings.RANDOM_STATE,
            n_estimators=settings.N_ESTIMATORS,
        )
        self.kyc_model.fit(kyc_scaled)

        # Generate transaction training data
        txn_train_data = self._generate_synthetic_transaction_data(1000)
        self.transaction_scaler = StandardScaler()
        txn_scaled = self.transaction_scaler.fit_transform(txn_train_data)

        self.transaction_model = IsolationForest(
            contamination=settings.CONTAMINATION,
            random_state=settings.RANDOM_STATE,
            n_estimators=settings.N_ESTIMATORS,
        )
        self.transaction_model.fit(txn_scaled)

        # Save models
        self._save_models()

        logger.info("Models trained and saved successfully!")

    def _generate_synthetic_kyc_data(self, n_samples: int) -> np.ndarray:
        """Generate synthetic KYC data for training"""
        data = np.random.randn(n_samples, 7)

        # Transform to realistic ranges
        data[:, 0] = data[:, 0] * 15 + 45  # age: ~45 ± 15
        data[:, 1] = np.abs(data[:, 1]) * 30000 + 50000  # income: 50k-110k
        data[:, 2] = data[:, 2] * 100 + 650  # credit score: ~650 ± 100
        data[:, 3] = np.abs(data[:, 3] * 2 + 2)  # num_accounts: ~2-4
        data[:, 4] = np.abs(data[:, 4] * 500 + 1000)  # account_age_days: ~1000-2000
        data[:, 5] = np.abs(data[:, 5] * 10 + 20)  # transactions: ~20 ± 10
        data[:, 6] = np.abs(data[:, 6] * 100 + 150)  # avg_amount: ~150 ± 100

        return data

    def _generate_synthetic_transaction_data(self, n_samples: int) -> np.ndarray:
        """Generate synthetic transaction data for training"""
        data = np.random.randn(n_samples, 8)

        # Transform to realistic ranges
        data[:, 0] = np.abs(data[:, 0]) * 200 + 100  # amount: 100-500
        data[:, 1] = np.random.randint(0, 4, n_samples)  # transaction_type: 0-3
        data[:, 2] = np.random.randint(0, 24, n_samples)  # hour: 0-23
        data[:, 3] = np.random.randint(0, 7, n_samples)  # day: 0-6
        data[:, 4] = np.abs(data[:, 4] * 5 + 10)  # distance: ~10 ± 5 km
        data[:, 5] = np.random.randint(0, 2, n_samples)  # is_online: 0-1
        data[:, 6] = np.abs(data[:, 6] * 2 + 3)  # transactions_24h: ~3 ± 2
        data[:, 7] = np.abs(data[:, 7] * 100 + 150)  # avg_amount: ~150 ± 100

        return data

    def _save_models(self):
        """Save models to disk"""
        os.makedirs(os.path.dirname(settings.KYC_MODEL_PATH), exist_ok=True)

        joblib.dump(self.kyc_model, settings.KYC_MODEL_PATH)
        joblib.dump(self.transaction_model, settings.TRANSACTION_MODEL_PATH)
        joblib.dump(self.kyc_scaler, settings.KYC_SCALER_PATH)
        joblib.dump(self.transaction_scaler, settings.TRANSACTION_SCALER_PATH)

    def _initialize_explainers(self):
        """Initialize SHAP explainers"""
        logger.info("Initializing SHAP explainers...")

        # Load real training data samples for better SHAP explanations
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
                features = self._prepare_kyc_features_from_df(df_normal)
                return self.kyc_scaler.transform(features)

            elif model_type == "transaction":
                df = pd.read_csv(data_dir / "transaction_training_data.csv")
                df_normal = df[df["is_anomaly"] == 0].sample(
                    n=min(n_samples, len(df)), random_state=42
                )
                features = self._prepare_transaction_features_from_df(df_normal)
                return self.transaction_scaler.transform(features)

            elif model_type == "combined":
                df = pd.read_csv(data_dir / "kyc_business_training_data.csv")
                df_normal = df[df["is_anomaly"] == 0].sample(
                    n=min(n_samples, len(df)), random_state=42
                )
                features = self._prepare_combined_features_from_df(df_normal)
                return self.combined_scaler.transform(features)

            elif model_type == "customer":
                df = pd.read_csv(data_dir / "transaction_training_data.csv")
                df_normal = df[df["is_anomaly"] == 0]
                # Group by customer and sample customers
                customer_ids = df_normal["customer_id"].unique()
                sampled_customers = np.random.choice(
                    customer_ids, min(n_samples, len(customer_ids)), replace=False
                )
                features = self._prepare_customer_features_from_df(
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

    def _prepare_kyc_features_from_df(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare KYC features from DataFrame (matching training script)"""
        features = []

        features.append(df["customer_age"].values)

        # Handle gender - remove "Gender." prefix if present
        gender_col = (
            df["customer_gender"]
            .astype(str)
            .str.replace("Gender.", "", regex=False)
            .str.lower()
        )
        gender_encoded = (gender_col == "female").astype(int)
        features.append(gender_encoded.values)

        # Handle marital status - remove prefix
        marital_col = (
            df["customer_marital_status"]
            .astype(str)
            .str.replace("MaritalStatusOptions.", "", regex=False)
            .str.lower()
        )
        marital_mapping = {"single": 0, "married": 1, "divorced": 2, "widowed": 3}
        marital_encoded = marital_col.map(marital_mapping).fillna(-1)
        features.append(marital_encoded.values)

        # Handle education level - remove prefix
        education_col = (
            df["customer_education_level"]
            .astype(str)
            .str.replace("EducationalLevelOptions.", "", regex=False)
            .str.lower()
        )
        education_mapping = {
            "primary": 0,
            "secondary": 1,
            "tertiary": 2,
            "post_graduate": 3,
        }
        education_encoded = education_col.map(education_mapping).fillna(-1)
        features.append(education_encoded.values)

        region_encoded = pd.Categorical(df["customer_region"]).codes
        features.append(region_encoded)

        city_encoded = pd.Categorical(df["customer_city"]).codes
        features.append(city_encoded)

        zone_encoded = pd.Categorical(df["customer_zone_or_sub_city"]).codes
        features.append(zone_encoded)

        woreda_numeric = pd.to_numeric(df["customer_woreda"], errors="coerce").fillna(0)
        features.append(woreda_numeric.values)

        phone_last_4 = df["customer_phone_number"].astype(str).str[-4:].astype(int)
        features.append(phone_last_4.values)

        tin_length = df["customer_tin_number"].str.len()
        features.append(tin_length.values)

        account_length = df["customer_bank_account_number"].str.len()
        features.append(account_length.values)

        return np.column_stack(features)

    def _prepare_transaction_features_from_df(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare transaction features from DataFrame (matching training script)"""
        features = []

        features.append(df["credit"].values)
        features.append(df["debit"].values)
        features.append(df["closingBalance"].values)

        source_mapping = {
            "CASH DEPOSIT": 0,
            "FUND TRANSFER": 1,
            "CASH WITHDRAW": 2,
            "TELE BIRR INCOMING": 3,
            "TELE BIRR OUT GOING": 4,
            "ATM card subscription fee": 5,
        }
        source_encoded = df["source"].map(source_mapping).fillna(-1)
        features.append(source_encoded.values)

        narrative_length = df["narrative"].str.len()
        features.append(narrative_length.values)

        transaction_amount = df["credit"] - df["debit"]
        features.append(transaction_amount.values)

        balance_ratio = np.where(
            df["closingBalance"] > 0, transaction_amount / df["closingBalance"], 0
        )
        features.append(balance_ratio)

        df["date"] = pd.to_datetime(df["date"])
        features.append(df["date"].dt.hour.values)
        features.append(df["date"].dt.dayofweek.values)
        features.append(df["date"].dt.day.values)
        features.append(df["date"].dt.month.values)

        customer_txn_counts = df.groupby("customer_id").size()
        features.append(df["customer_id"].map(customer_txn_counts).values)

        return np.column_stack(features)

    def _prepare_combined_features_from_df(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare combined KYC + Business features from DataFrame"""
        kyc_features = self._prepare_kyc_features_from_df(df)
        business_features = self._prepare_business_features_from_df(df)
        return np.column_stack([kyc_features, business_features])

    def _prepare_business_features_from_df(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare business features from DataFrame (matching training script)"""
        features = []

        features.append(df["business_establishment_year"].values)

        sector_mapping = {
            "AGRICULTURE": 0,
            "MANUFACTURING": 1,
            "DOMESTIC_TRADE_SERVICES": 2,
            "SERVICES": 3,
            "OTHER": 4,
        }
        sector_encoded = df["business_sector"].map(sector_mapping).fillna(-1)
        features.append(sector_encoded.values)

        level_mapping = {"GROWING": 0, "STARTUP": 1}
        level_encoded = df["business_level"].map(level_mapping).fillna(-1)
        features.append(level_encoded.values)

        features.append(df["business_starting_capital"].values)
        features.append(df["business_current_capital"].values)
        features.append(df["business_annual_profit"].values)
        features.append(df["business_annual_sales"].values)
        features.append(df["business_starting_no_of_employees"].values)
        features.append(df["business_current_no_of_employees"].values)

        source_mapping = {"FAMILY": 0, "OWN": 1, "LOAN": 2, "FUND": 3, "OTHER": 4}
        source_encoded = (
            df["business_source_of_initial_capital"].map(source_mapping).fillna(-1)
        )
        features.append(source_encoded.values)

        association_mapping = {
            "SOLE_PROPRIETORSHIP": 0,
            "PARTNERSHIP": 1,
            "CORPORATION": 2,
            "OTHER": 3,
        }
        association_encoded = (
            df["business_association_type"].map(association_mapping).fillna(-1)
        )
        features.append(association_encoded.values)

        capital_growth = np.where(
            df["business_starting_capital"] > 0,
            df["business_current_capital"] / df["business_starting_capital"],
            0,
        )
        features.append(capital_growth)

        employee_growth = np.where(
            df["business_starting_no_of_employees"] > 0,
            df["business_current_no_of_employees"]
            / df["business_starting_no_of_employees"],
            0,
        )
        features.append(employee_growth)

        profit_margin = np.where(
            df["business_annual_sales"] > 0,
            df["business_annual_profit"] / df["business_annual_sales"],
            0,
        )
        features.append(profit_margin)

        current_year = 2024
        business_age = current_year - df["business_establishment_year"]
        features.append(business_age.values)

        return np.column_stack(features)

    def _prepare_customer_features_from_df(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare customer-level features from transaction DataFrame"""
        customer_features = []

        for customer_id, customer_df in df.groupby("customer_id"):
            features = []

            total_transactions = len(customer_df)
            features.append(total_transactions)

            total_credit = customer_df["credit"].sum()
            total_debit = customer_df["debit"].sum()
            avg_credit = customer_df["credit"].mean()
            avg_debit = customer_df["debit"].mean()
            max_credit = customer_df["credit"].max()
            max_debit = customer_df["debit"].max()
            features.extend(
                [
                    total_credit,
                    total_debit,
                    avg_credit,
                    avg_debit,
                    max_credit,
                    max_debit,
                ]
            )

            avg_balance = customer_df["closingBalance"].mean()
            max_balance = customer_df["closingBalance"].max()
            min_balance = customer_df["closingBalance"].min()
            balance_volatility = customer_df["closingBalance"].std()
            features.extend([avg_balance, max_balance, min_balance, balance_volatility])

            transaction_amounts = customer_df["credit"] - customer_df["debit"]
            features.extend(
                [
                    transaction_amounts.mean(),
                    transaction_amounts.max(),
                    transaction_amounts.min(),
                    transaction_amounts.std(),
                ]
            )

            source_counts = customer_df["source"].value_counts()
            unique_sources = len(source_counts)
            most_common_source_ratio = (
                source_counts.iloc[0] / total_transactions
                if total_transactions > 0
                else 0
            )

            cash_deposit_ratio = (
                customer_df["source"] == "CASH DEPOSIT"
            ).sum() / total_transactions
            fund_transfer_ratio = (
                customer_df["source"] == "FUND TRANSFER"
            ).sum() / total_transactions
            cash_withdraw_ratio = (
                customer_df["source"] == "CASH WITHDRAW"
            ).sum() / total_transactions
            tele_birr_ratio = (
                (customer_df["source"] == "TELE BIRR INCOMING")
                | (customer_df["source"] == "TELE BIRR OUT GOING")
            ).sum() / total_transactions

            features.extend(
                [
                    unique_sources,
                    most_common_source_ratio,
                    cash_deposit_ratio,
                    fund_transfer_ratio,
                    cash_withdraw_ratio,
                    tele_birr_ratio,
                ]
            )

            customer_df["date"] = pd.to_datetime(customer_df["date"])
            avg_hour = customer_df["date"].dt.hour.mean()
            hour_std = customer_df["date"].dt.hour.std()
            night_transactions = (
                (customer_df["date"].dt.hour >= 22) | (customer_df["date"].dt.hour <= 6)
            ).sum() / total_transactions
            features.extend([avg_hour, hour_std, night_transactions])

            weekday_transactions = (
                customer_df["date"].dt.dayofweek < 5
            ).sum() / total_transactions
            weekend_transactions = (
                customer_df["date"].dt.dayofweek >= 5
            ).sum() / total_transactions
            features.extend([weekday_transactions, weekend_transactions])

            if total_transactions > 1:
                time_diffs = (
                    customer_df["date"].sort_values().diff().dt.total_seconds() / 3600
                )
                features.extend([time_diffs.mean(), time_diffs.min(), time_diffs.max()])
            else:
                features.extend([0, 0, 0])

            avg_narrative_length = customer_df["narrative"].str.len().mean()
            unique_narratives = customer_df["narrative"].nunique()
            narrative_diversity = unique_narratives / total_transactions
            features.extend(
                [avg_narrative_length, unique_narratives, narrative_diversity]
            )

            balance_ratios = np.where(
                customer_df["closingBalance"] > 0,
                transaction_amounts / customer_df["closingBalance"],
                0,
            )
            features.extend(
                [balance_ratios.mean(), balance_ratios.max(), balance_ratios.std()]
            )

            high_amount_transactions = (
                np.abs(transaction_amounts) > transaction_amounts.quantile(0.9)
            ).sum() / total_transactions
            rapid_transactions = (
                (time_diffs < 1).sum() / max(total_transactions - 1, 1)
                if total_transactions > 1
                else 0
            )
            features.extend([high_amount_transactions, rapid_transactions])

            customer_features.append(features)

        return np.array(customer_features)

    def extract_kyc_features(self, data: KYCData) -> np.ndarray:
        """Extract features from KYC data"""
        return np.array(
            [
                [
                    data.age,
                    data.annual_income,
                    data.credit_score,
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
        score = self.transaction_model.score_samples(scaled_features)[0]

        is_anomaly = prediction == -1
        risk_level = self._calculate_risk_level(score)
        explanation = self.transaction_explainer.explain(scaled_features)

        return is_anomaly, float(score), risk_level, explanation

    def _calculate_risk_level(self, score: float) -> RiskLevel:
        """Calculate risk level based on anomaly score"""
        if score < settings.HIGH_RISK_THRESHOLD:
            return RiskLevel.HIGH
        elif score < settings.MEDIUM_RISK_THRESHOLD:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
