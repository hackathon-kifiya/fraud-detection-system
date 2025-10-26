"""Repository interfaces for data types."""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.data_type_models import DataTypeModel


class DataTypeRepository(ABC):
    """Repository interface for data types."""
    
    @abstractmethod
    def create(self, data_type: DataTypeModel) -> DataTypeModel:
        """Create a new data type."""
        pass
    
    @abstractmethod
    def get_by_id(self, data_type: str) -> Optional[DataTypeModel]:
        """Get data type by identifier."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[DataTypeModel]:
        """Get all data types."""
        pass
    
    @abstractmethod
    def update(self, data_type: str, data_type_model: DataTypeModel) -> Optional[DataTypeModel]:
        """Update an existing data type."""
        pass
    
    @abstractmethod
    def delete(self, data_type: str) -> bool:
        """Delete a data type."""
        pass
    
    @abstractmethod
    def exists(self, data_type: str) -> bool:
        """Check if data type exists."""
        pass
