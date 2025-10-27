"""Migration script to duplicate default config for existing data types."""

import os
import sys
import logging
import requests

# Add parent directory to path to import from project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.database.config_repository import PostgreSQLConfigRepository
from domain.models import DataTypeDecisionConfig
from adapters.client.data_management_client import DataManagementClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_configs():
    """Migrate default configuration to existing data types."""
    logger.info("Starting configuration migration...")
    
    # Initialize clients
    config_repo = PostgreSQLConfigRepository()
    data_mgmt_client = DataManagementClient()
    
    try:
        # Get current default configuration
        default_config = config_repo.get_config()
        logger.info(f"Default config loaded: {default_config.dict()}")
        
        # Get all data types from data-management-service
        data_types = data_mgmt_client.get_data_types()
        logger.info(f"Found {len(data_types)} data types to migrate")
        
        # Migrate each data type
        for dt in data_types:
            data_type = dt.get('data_type')
            name = dt.get('name')
            
            logger.info(f"Migrating config for {name} ({data_type})...")
            
            # Create data-type-specific config with all values from default
            dt_config = DataTypeDecisionConfig(
                data_type=data_type,
                auto_approve_threshold=default_config.auto_approve_threshold,
                auto_reject_threshold=default_config.auto_reject_threshold,
                rule_engine_weight=default_config.rule_engine_weight,
                anomaly_detection_weight=default_config.anomaly_detection_weight,
                predictive_engine_weight=default_config.predictive_engine_weight,
                model_based_scoring=default_config.model_based_scoring,
                model_based_thresholds=default_config.model_based_thresholds
            )
            
            # Save config
            config_repo.update_data_type_config(data_type, dt_config)
            logger.info(f"✓ Migrated config for {data_type}")
        
        logger.info(f"Migration complete! Migrated configs for {len(data_types)} data types.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    migrate_configs()

