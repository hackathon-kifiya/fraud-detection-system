"""Seed data types from JSON files."""

import os
import json
import logging
from typing import List
from pathlib import Path
from domain.data_type_models import DataTypeModel
from domain.repository import DataTypeRepository

logger = logging.getLogger(__name__)


def seed_data_types(repository: DataTypeRepository) -> None:
    """Seed data types from JSON files."""
    
    # Get the current working directory
    wd = os.getcwd()
    
    # Search for seed files in common locations
    possible_paths = [
        os.path.join(wd, "data", "seeds"),
        os.path.join(wd, "data-management-service", "data", "seeds"),
        os.path.join(wd, "..", "data-management-service", "data", "seeds"),
    ]
    
    seeds_dir = None
    for path in possible_paths:
        if os.path.exists(path):
            seeds_dir = path
            break
    
    if not seeds_dir:
        logger.warning("Could not find seeds directory, skipping data type seeding")
        return
    
    # List all JSON files in the seeds directory
    seed_files = list(Path(seeds_dir).glob("*-data-type.json"))
    
    if not seed_files:
        logger.warning("No seed files found in %s", seeds_dir)
        return
    
    logger.info("Found %d data type seed file(s)", len(seed_files))
    
    for file_path in seed_files:
        logger.info("Loading seed file: %s", file_path.name)
        
        try:
            # Read the JSON file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Create DataTypeModel from seed data
            seed_data_type = DataTypeModel(
                data_type=data['data_type'],
                name=data['name'],
                description=data['description'],
                schema_definition=data['schema_definition'],
                sample_data=data.get('sample_data'),
                status=data.get('status', 'ACTIVE'),
                created_by=data.get('created_by', 'system'),
                updated_by=data.get('updated_by')
            )
            
            # Check if data type already exists
            if repository.exists(seed_data_type.data_type):
                logger.info("Data type '%s' already exists, skipping...", seed_data_type.data_type)
                continue
            
            # Create the data type
            repository.create(seed_data_type)
            logger.info("Successfully created data type: %s", seed_data_type.data_type)
            
        except FileNotFoundError:
            logger.warning("Could not read file %s", file_path)
        except json.JSONDecodeError as e:
            logger.warning("Could not parse JSON in %s: %s", file_path, e)
        except Exception as e:
            logger.error("Error loading seed file %s: %s", file_path, e)
    
    logger.info("Data type seeding completed")

