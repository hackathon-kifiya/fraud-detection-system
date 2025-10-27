"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class DataTypeResponse(BaseModel):
    """API response model for data types."""
    data_type: str
    name: str
    description: str
    schema_definition: Dict[str, Any]
    sample_data: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: Optional[str] = None


class CreateDataTypeRequest(BaseModel):
    """Request model for creating a data type."""
    data_type: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Description")
    schema_definition: Dict[str, Any] = Field(..., description="Schema definition")
    sample_data: Dict[str, Any] = Field(..., description="Sample data (required)")
    status: str = Field(default="ACTIVE", description="Status")
    created_by: str = Field(..., description="Creator")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data_type": "transactions",
                "name": "Transaction Data",
                "description": "Financial transactions",
                "schema_definition": {
                    "fields": {"amount": {"type": "number"}},
                    "required": ["amount"]
                },
                "sample_data": {"amount": 100.50},
                "status": "ACTIVE",
                "created_by": "system"
            }
        }


class UpdateDataTypeRequest(BaseModel):
    """Request model for updating a data type."""
    name: Optional[str] = None
    description: Optional[str] = None
    schema_definition: Optional[Dict[str, Any]] = None
    sample_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    updated_by: Optional[str] = None


class DeleteResponse(BaseModel):
    """Response model for deletion."""
    success: bool
    message: str

