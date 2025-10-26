"""PostgreSQL repository implementation for decision configuration."""

from typing import ContextManager
from contextlib import contextmanager
import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from domain.models import DecisionConfigModel
from domain.repository import DecisionConfigRepository

logger = logging.getLogger(__name__)


class PostgreSQLConfigRepository(DecisionConfigRepository):
    """PostgreSQL implementation of configuration repository."""
    
    def __init__(self):
        self._pool = None
    
    @property
    def pool(self):
        """Lazy initialization of connection pool."""
        if self._pool is None:
            db_url = os.getenv('DATABASE_URL', 'postgresql://frauduser:fraudpass@postgres:5432/frauddb')
            self._pool = SimpleConnectionPool(1, 10, db_url)
        return self._pool
    
    @contextmanager
    def get_db(self):
        """Get database connection from pool."""
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.putconn(conn)
    
    def initialize_schema(self):
        """Initialize database table."""
        try:
            with self.get_db() as conn:
                cur = conn.cursor()
                
                # Create decision_config table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS decision_config (
                        id SERIAL PRIMARY KEY,
                        model_based_thresholds BOOLEAN DEFAULT FALSE,
                        auto_approve_threshold FLOAT DEFAULT 25.0,
                        auto_reject_threshold FLOAT DEFAULT 85.0,
                        model_based_scoring BOOLEAN DEFAULT FALSE,
                        rule_engine_weight FLOAT DEFAULT 40.0,
                        anomaly_detection_weight FLOAT DEFAULT 35.0,
                        predictive_engine_weight FLOAT DEFAULT 25.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Check if config exists, if not create default
                cur.execute("SELECT COUNT(*) FROM decision_config")
                count = cur.fetchone()[0]
                
                if count == 0:
                    cur.execute("""
                        INSERT INTO decision_config (
                            model_based_thresholds, auto_approve_threshold, auto_reject_threshold,
                            model_based_scoring, rule_engine_weight, anomaly_detection_weight, predictive_engine_weight
                        ) VALUES (
                            FALSE, 25.0, 85.0, FALSE, 40.0, 35.0, 25.0
                        )
                    """)
                    logger.info("Created default decision configuration")
                
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_config(self) -> DecisionConfigModel:
        """Retrieve current configuration from database."""
        with self.get_db() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT * FROM decision_config ORDER BY id DESC LIMIT 1
            """)
            row = cur.fetchone()
            if row:
                return DecisionConfigModel(**row)
            else:
                # Return default config if none exists
                return DecisionConfigModel()
    
    def update_config(self, config: DecisionConfigModel) -> dict:
        """Update configuration in database."""
        with self.get_db() as conn:
            cur = conn.cursor()
            
            # Get current config to update
            cur.execute("SELECT * FROM decision_config ORDER BY id DESC LIMIT 1")
            existing = cur.fetchone()
            
            if existing:
                # Update existing config
                cur.execute("""
                    UPDATE decision_config
                    SET model_based_thresholds = %s,
                        auto_approve_threshold = %s,
                        auto_reject_threshold = %s,
                        model_based_scoring = %s,
                        rule_engine_weight = %s,
                        anomaly_detection_weight = %s,
                        predictive_engine_weight = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    config.model_based_thresholds,
                    config.auto_approve_threshold,
                    config.auto_reject_threshold,
                    config.model_based_scoring,
                    config.rule_engine_weight,
                    config.anomaly_detection_weight,
                    config.predictive_engine_weight,
                    existing[0]  # id
                ))
            else:
                # Insert new config
                cur.execute("""
                    INSERT INTO decision_config (
                        model_based_thresholds, auto_approve_threshold, auto_reject_threshold,
                        model_based_scoring, rule_engine_weight, anomaly_detection_weight, predictive_engine_weight
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    config.model_based_thresholds,
                    config.auto_approve_threshold,
                    config.auto_reject_threshold,
                    config.model_based_scoring,
                    config.rule_engine_weight,
                    config.anomaly_detection_weight,
                    config.predictive_engine_weight
                ))
            
            return config.dict()
    
    def initialize_config(self, config: DecisionConfigModel) -> None:
        """Initialize default configuration."""
        self.initialize_schema()

