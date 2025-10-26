"""Data type domain models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class DataTypeModel(BaseModel):
    """Domain model for data types."""
    data_type: str = Field(..., description="Unique identifier for the data type")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Description of the data type")
    schema_definition: Dict[str, Any] = Field(..., description="JSON schema definition")
    sample_data: Optional[Dict[str, Any]] = Field(None, description="Sample data for validation")
    status: str = Field(default="ACTIVE", description="Data type status")
    created_by: str = Field(..., description="User who created the data type")
    updated_by: Optional[str] = Field(None, description="User who last updated the data type")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data_type": "transactions",
                "name": "Transaction Data",
                "description": "Financial transaction data",
                "schema_definition": {
                    "fields": {
                        "amount": {"type": "number", "description": "Transaction amount"},
                        "merchant": {"type": "string", "description": "Merchant name"}
                    },
                    "required": ["amount"]
                },
                "sample_data": {
                    "amount": 100.50,
                    "merchant": "Store ABC"
                },
                "status": "ACTIVE",
                "created_by": "system"
            }
        }
