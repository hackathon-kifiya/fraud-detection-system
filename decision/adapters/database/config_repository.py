"""PostgreSQL repository implementation for decision configuration."""

from typing import ContextManager, Optional, List, Dict, Any
from contextlib import contextmanager
import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from datetime import datetime
from domain.models import DecisionConfigModel, DataTypeDecisionConfig, MergedDataTypeConfig
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
                
                # Create data_type_decision_configs table for type-specific overrides
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS data_type_decision_configs (
                        data_type VARCHAR(100) PRIMARY KEY,
                        auto_approve_threshold FLOAT,
                        auto_reject_threshold FLOAT,
                        rule_engine_weight FLOAT,
                        anomaly_detection_weight FLOAT,
                        predictive_engine_weight FLOAT,
                        model_based_scoring BOOLEAN,
                        model_based_thresholds BOOLEAN,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
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
    
    def get_data_type_config(self, data_type: str) -> MergedDataTypeConfig:
        """Get merged configuration for a specific data type (defaults + overrides)."""
        # Get default config
        default_config = self.get_config()
        
        with self.get_db() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT * FROM data_type_decision_configs WHERE data_type = %s
            """, (data_type,))
            override = cur.fetchone()
            
            if override:
                # Merge with defaults - only override non-null values
                merged_config = default_config.dict()
                overridden_fields = []
                
                for key, value in override.items():
                    if key not in ['data_type', 'created_at', 'updated_at'] and value is not None:
                        merged_config[key] = value
                        overridden_fields.append(key)
                
                return MergedDataTypeConfig(
                    data_type=data_type,
                    config=DecisionConfigModel(**merged_config),
                    is_custom=True,
                    overridden_fields=overridden_fields
                )
            else:
                # No overrides, return defaults
                return MergedDataTypeConfig(
                    data_type=data_type,
                    config=default_config,
                    is_custom=False,
                    overridden_fields=[]
                )
    
    def update_data_type_config(self, data_type: str, config: DataTypeDecisionConfig) -> DataTypeDecisionConfig:
        """Create or update data-type-specific configuration overrides."""
        with self.get_db() as conn:
            cur = conn.cursor()
            
            # Check if config exists
            cur.execute("SELECT COUNT(*) FROM data_type_decision_configs WHERE data_type = %s", (data_type,))
            exists = cur.fetchone()[0] > 0
            
            if exists:
                # Build dynamic UPDATE query for non-null fields only
                update_fields = []
                update_values = []
                
                if config.auto_approve_threshold is not None:
                    update_fields.append("auto_approve_threshold = %s")
                    update_values.append(config.auto_approve_threshold)
                if config.auto_reject_threshold is not None:
                    update_fields.append("auto_reject_threshold = %s")
                    update_values.append(config.auto_reject_threshold)
                if config.rule_engine_weight is not None:
                    update_fields.append("rule_engine_weight = %s")
                    update_values.append(config.rule_engine_weight)
                if config.anomaly_detection_weight is not None:
                    update_fields.append("anomaly_detection_weight = %s")
                    update_values.append(config.anomaly_detection_weight)
                if config.predictive_engine_weight is not None:
                    update_fields.append("predictive_engine_weight = %s")
                    update_values.append(config.predictive_engine_weight)
                if config.model_based_scoring is not None:
                    update_fields.append("model_based_scoring = %s")
                    update_values.append(config.model_based_scoring)
                if config.model_based_thresholds is not None:
                    update_fields.append("model_based_thresholds = %s")
                    update_values.append(config.model_based_thresholds)
                
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                update_values.append(data_type)
                
                query = f"""
                    UPDATE data_type_decision_configs
                    SET {', '.join(update_fields)}
                    WHERE data_type = %s
                """
                cur.execute(query, update_values)
            else:
                # Insert new config
                cur.execute("""
                    INSERT INTO data_type_decision_configs (
                        data_type, auto_approve_threshold, auto_reject_threshold,
                        rule_engine_weight, anomaly_detection_weight, predictive_engine_weight,
                        model_based_scoring, model_based_thresholds
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    data_type,
                    config.auto_approve_threshold,
                    config.auto_reject_threshold,
                    config.rule_engine_weight,
                    config.anomaly_detection_weight,
                    config.predictive_engine_weight,
                    config.model_based_scoring,
                    config.model_based_thresholds
                ))
            
            config.updated_at = datetime.now()
            return config
    
    def delete_data_type_config(self, data_type: str) -> bool:
        """Delete data-type-specific configuration (revert to defaults)."""
        with self.get_db() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM data_type_decision_configs WHERE data_type = %s", (data_type,))
            return cur.rowcount > 0
    
    def get_all_data_type_configs(self) -> List[Dict[str, Any]]:
        """Get all data types with custom configurations."""
        with self.get_db() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT data_type FROM data_type_decision_configs ORDER BY data_type
            """)
            rows = cur.fetchall()
            return [dict(row) for row in rows]

