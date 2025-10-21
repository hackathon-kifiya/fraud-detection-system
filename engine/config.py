import os
from urllib.parse import urlparse

class Config:
    """Configuration class for the fraud detection engine"""
    
    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://frauduser:fraudpass@localhost:5432/frauddb')
    
    # Parse database URL for connection parameters
    def __init__(self):
        parsed = urlparse(self.DATABASE_URL)
        self.DB_HOST = parsed.hostname or 'localhost'
        self.DB_PORT = parsed.port or 5432
        self.DB_NAME = parsed.path[1:] if parsed.path else 'frauddb'
        self.DB_USER = parsed.username or 'frauduser'
        self.DB_PASSWORD = parsed.password or 'fraudpass'
    
    # Detection thresholds
    RISK_SCORE_THRESHOLD = 70.0
    Z_SCORE_THRESHOLD = 3.0
    MULTIPLE_CREDITS_WINDOW_MINUTES = 5
    LOAN_REQUESTS_24H_LIMIT = 2
    LATE_PAYMENTS_THRESHOLD = 3
    CREDIT_SCORE_DROP_THRESHOLD = 50
    
    # Scoring weights
    STATS_WEIGHT = 0.4
    RULES_WEIGHT = 0.3
    NEW_CHECKS_WEIGHT = 0.3
    
    # Flask configuration
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 5001
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
