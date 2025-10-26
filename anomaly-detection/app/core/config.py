"""
Application Configuration
"""
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "KYC & Transaction Anomaly Detection API"
    PROJECT_DESCRIPTION: str = (
        "Anomaly detection service using Isolation Forest with SHAP explanations"
    )
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Security
    API_KEY_ENABLED: bool = False
    API_KEY: str = "your-secret-api-key-here"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Model Configuration
    DATA_DIR: str = "data"
    KYC_MODEL_PATH: str = "data/models/kyc_model.pkl"
    TRANSACTION_MODEL_PATH: str = "data/models/transaction_model.pkl"
    KYC_SCALER_PATH: str = "data/models/kyc_scaler.pkl"
    TRANSACTION_SCALER_PATH: str = "data/models/transaction_scaler.pkl"
    MODELS_DIR: str = "data/models"
    COMBINED_MODEL_PATH: str = "data/models/merged_model.pkl"
    COMBINED_SCALER_PATH: str = "data/models/merged_scaler.pkl"
    CUSTOMER_MODEL_PATH: str = "data/models/customer_model.pkl"
    CUSTOMER_SCALER_PATH: str = "data/models/customer_scaler.pkl"

    # Supervised Models (Random Forest)
    KYC_SUPERVISED_MODEL_PATH: str = "data/models/kyc_supervised_model.pkl"
    KYC_SUPERVISED_SCALER_PATH: str = "data/models/kyc_supervised_scaler.pkl"
    TRANSACTION_SUPERVISED_MODEL_PATH: str = "data/models/transaction_supervised_model.pkl"
    TRANSACTION_SUPERVISED_SCALER_PATH: str = "data/models/transaction_supervised_scaler.pkl"
    COMBINED_SUPERVISED_MODEL_PATH: str = "data/models/merged_supervised_model.pkl"
    COMBINED_SUPERVISED_SCALER_PATH: str = "data/models/merged_supervised_scaler.pkl"
    CUSTOMER_SUPERVISED_MODEL_PATH: str = "data/models/customer_supervised_model.pkl"
    CUSTOMER_SUPERVISED_SCALER_PATH: str = "data/models/customer_supervised_scaler.pkl"

    # Isolation Forest Parameters
    CONTAMINATION: float = 0.1
    N_ESTIMATORS: int = 100
    RANDOM_STATE: int = 42

    # Anomaly Thresholds
    HIGH_RISK_THRESHOLD: float = -0.3
    MEDIUM_RISK_THRESHOLD: float = -0.1

    # Database (Optional)
    DATABASE_URL: str = "sqlite:///./anomaly_detection.db"

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
