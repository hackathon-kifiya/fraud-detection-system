"""Data type service use case."""

from typing import List, Optional
from domain.data_type_models import DataTypeModel, CreateDataTypeRequest, UpdateDataTypeRequest
from domain.repository import DataTypeRepository
import logging

logger = logging.getLogger(__name__)


class DataTypeService:
    """Service for managing data types."""
    
    def __init__(self, repository: DataTypeRepository):
        self.repository = repository
    
    def create_data_type(self, request: CreateDataTypeRequest) -> DataTypeModel:
        """Create a new data type."""
        # Check if data type already exists
        if self.repository.exists(request.data_type):
            raise ValueError(f"Data type '{request.data_type}' already exists")
        
        data_type = DataTypeModel(
            data_type=request.data_type,
            name=request.name,
            description=request.description,
            schema_definition=request.schema_definition,
            sample_data=request.sample_data,
            status=request.status,
            created_by=request.created_by,
            updated_by=request.created_by
        )
        
        return self.repository.create(data_type)
    
    def get_data_type(self, data_type: str) -> Optional[DataTypeModel]:
        """Get a data type by identifier."""
        return self.repository.get_by_id(data_type)
    
    def get_all_data_types(self) -> List[DataTypeModel]:
        """Get all data types."""
        return self.repository.get_all()
    
    def update_data_type(self, data_type: str, request: UpdateDataTypeRequest) -> Optional[DataTypeModel]:
        """Update a data type."""
        existing = self.repository.get_by_id(data_type)
        if not existing:
            raise ValueError(f"Data type '{data_type}' not found")
        
        # Update fields if provided
        if request.name is not None:
            existing.name = request.name
        if request.description is not None:
            existing.description = request.description
        if request.schema_definition is not None:
            existing.schema_definition = request.schema_definition
        if request.sample_data is not None:
            existing.sample_data = request.sample_data
        if request.status is not None:
            existing.status = request.status
        if request.updated_by is not None:
            existing.updated_by = request.updated_by
        
        from datetime import datetime
        existing.updated_at = datetime.now()
        
        return self.repository.update(data_type, existing)
    
    def delete_data_type(self, data_type: str) -> bool:
        """Delete a data type."""
        return self.repository.delete(data_type)

