"""
Application configuration settings.
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application Info
    PROJECT_NAME: str = "Risk Aggregator Service"
    API_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8003"))

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    API_KEY: str = os.getenv("API_KEY", "")
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
    ]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "json"

    # Documentation
    ENABLE_DOCS: bool = os.getenv("ENABLE_DOCS", "True").lower() == "true"

    # External Services
    ANOMALY_DETECTION_URL: str = os.getenv(
        "ANOMALY_DETECTION_URL", "http://localhost:8002"
    )
    JAVA_ENGINE_URL: str = os.getenv("JAVA_ENGINE_URL", "http://localhost:8080")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/fraud_detection"
    )

    # Risk Aggregation Settings
    RISK_SCORE_WEIGHTS: dict = {
        "kyc": 0.25,
        "transaction": 0.30,
        "credit": 0.20,
        "loan": 0.15,
        "repayment": 0.10,
    }

    # Risk Thresholds
    HIGH_RISK_THRESHOLD: float = 0.75
    MEDIUM_RISK_THRESHOLD: float = 0.50
    LOW_RISK_THRESHOLD: float = 0.25

    # Cache Settings
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes

    class Config:
        """Pydantic configuration."""

        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()

