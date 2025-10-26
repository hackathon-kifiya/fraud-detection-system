"""Repository interfaces for decision service."""

from abc import ABC, abstractmethod
from domain.models import DecisionConfigModel


class DecisionConfigRepository(ABC):
    """Repository interface for decision configuration."""
    
    @abstractmethod
    def get_config(self) -> DecisionConfigModel:
        """Retrieve current configuration."""
        pass
    
    @abstractmethod
    def update_config(self, config: DecisionConfigModel) -> dict:
        """Update configuration."""
        pass
    
    @abstractmethod
    def initialize_config(self, config: DecisionConfigModel) -> None:
        """Initialize default configuration."""
        pass

