"""API route handlers."""

from fastapi import APIRouter, HTTPException, Depends, Path
from typing import Annotated, List
import logging
from domain.models import DecisionRequest, DecisionConfigModel
from domain.data_type_models import DataTypeModel
from usecases.decision_service import DecisionService, ConfigService
from adapters.api.schemas import DecisionResponse, ConfigUpdateResponse
from adapters.database.data_type_repository import PostgreSQLDataTypeRepository

logger = logging.getLogger(__name__)


# Example responses for Swagger
CONFIG_EXAMPLE = {
    "model_based_thresholds": False,
    "auto_approve_threshold": 25.0,
    "auto_reject_threshold": 85.0,
    "model_based_scoring": False,
    "rule_engine_weight": 40.0,
    "anomaly_detection_weight": 35.0,
    "predictive_engine_weight": 25.0
}

DECISION_REQUEST_EXAMPLE = {
    "entity_id": "txn_123456",
    "rule_engine_score": 0.4,
    "anomaly_detection_score": 0.6,
    "predictive_engine_score": 0.3
}

DECISION_RESPONSE_EXAMPLE = {
    "entity_id": "txn_123456",
    "final_score": 0.445,
    "final_score_percent": 44.5,
    "decision": "HUMAN_REVIEW",
    "breakdown": {
        "rule_engine": {
            "score": 0.4,
            "weight": 40.0,
            "contribution": 16.0
        },
        "anomaly_detection": {
            "score": 0.6,
            "weight": 35.0,
            "contribution": 21.0
        },
        "predictive_engine": {
            "score": 0.3,
            "weight": 25.0,
            "contribution": 7.5
        }
    },
    "confidence": 0.5
}


def create_config_router(
    config_service: ConfigService,
    decision_service: DecisionService
) -> APIRouter:
    """Create configuration router."""
    router = APIRouter()
    
    @router.get(
        "/config",
        response_model=DecisionConfigModel,
        summary="Get current configuration",
        description="""
        Retrieve the current decision service configuration.
        
        Returns:
        - Decision thresholds (auto_approve and auto_reject)
        - Engine weight configuration
        - Model-based settings (currently not implemented)
        """,
        responses={
            200: {
                "description": "Configuration retrieved successfully",
                "content": {
                    "application/json": {
                        "example": CONFIG_EXAMPLE
                    }
                }
            },
            500: {"description": "Internal server error"}
        }
    )
    async def get_current_config():
        """Get current configuration."""
        try:
            config = config_service.get_config()
            return config
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve configuration: {str(e)}")
    
    @router.post(
        "/config",
        response_model=ConfigUpdateResponse,
        summary="Update configuration",
        description="""
        Update the decision service configuration.
        
        **Validation Rules:**
        - `rule_engine_weight` + `anomaly_detection_weight` + `predictive_engine_weight` must equal 100
        - `auto_approve_threshold` must be less than `auto_reject_threshold`
        - All thresholds and weights must be between 0 and 100
        
        **Configuration Fields:**
        - `model_based_thresholds`: Enable/disable model-based threshold optimization (future feature)
        - `auto_approve_threshold`: Scores ≤ this value are auto-approved
        - `auto_reject_threshold`: Scores ≥ this value are auto-rejected
        - `model_based_scoring`: Enable/disable ML-based weight optimization (future feature)
        - Engine weights: Configure the relative importance of each scoring engine
        """,
        responses={
            200: {
                "description": "Configuration updated successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "success": True,
                            "message": "Configuration updated successfully",
                            "config": CONFIG_EXAMPLE
                        }
                    }
                }
            },
            400: {"description": "Invalid configuration (validation failed)"},
            500: {"description": "Internal server error"}
        }
    )
    async def update_configuration(config: DecisionConfigModel):
        """Update configuration."""
        try:
            updated_config = config_service.update_config(config)
            
            return ConfigUpdateResponse(
                success=True,
                message="Configuration updated successfully",
                config=updated_config
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")
    
    return router


def create_decision_router(decision_service: DecisionService) -> APIRouter:
    """Create decision router."""
    router = APIRouter()
    
    @router.post(
        "/decide",
        response_model=DecisionResponse,
        summary="Make a decision",
        description="""
        Make a fraud detection decision based on scores from three engines.
        
        **Input Scores (0-1 normalized):**
        - `rule_engine_score`: Business rules evaluation from rule engine
        - `anomaly_detection_score`: Statistical anomaly detection score
        - `predictive_engine_score`: Machine learning prediction score
        
        **Calculation:**
        1. Calculates weighted average: (rule × weight₁ + anomaly × weight₂ + predictive × weight₃) / 100
        2. Applies decision thresholds to determine recommendation
        3. Calculates confidence based on proximity to thresholds
        
        **Decision Outputs:**
        - `AUTO_APPROVE`: Score ≤ auto_approve_threshold
        - `HUMAN_REVIEW`: Score between auto_approve_threshold and auto_reject_threshold
        - `AUTO_REJECT`: Score ≥ auto_reject_threshold
        """,
        responses={
            200: {
                "description": "Decision calculated successfully",
                "content": {
                    "application/json": {
                        "example": DECISION_RESPONSE_EXAMPLE
                    }
                }
            },
            400: {"description": "Invalid request (scores out of range)"},
            500: {"description": "Internal server error"}
        }
    )
    async def make_decision(request: DecisionRequest):
        """
        Make a decision based on aggregated engine scores.
        
        Returns a complete decision breakdown with:
        - Final weighted score (0-1 and percentage)
        - Decision recommendation (AUTO_APPROVE, HUMAN_REVIEW, or AUTO_REJECT)
        - Score breakdown by engine
        - Decision confidence score
        """
        try:
            result = decision_service.make_decision(request)
            return DecisionResponse(**result.dict())
        except Exception as e:
            logger.error(f"Error making decision: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to make decision: {str(e)}")
    
    return router


def create_data_type_router() -> APIRouter:
    """Create data type router."""
    router = APIRouter()
    repository = PostgreSQLDataTypeRepository()
    
    @router.post(
        "/data-types",
        response_model=DataTypeModel,
        summary="Create a new data type",
        description="Create a new data type schema in the decision service",
        tags=["data-types"]
    )
    async def create_data_type(data_type: DataTypeModel):
        """Create a new data type."""
        try:
            if repository.exists(data_type.data_type):
                raise HTTPException(status_code=400, detail=f"Data type '{data_type.data_type}' already exists")
            created = repository.create(data_type)
            return created
        except Exception as e:
            logger.error(f"Error creating data type: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create data type: {str(e)}")
    
    @router.get(
        "/data-types",
        response_model=List[DataTypeModel],
        summary="Get all data types",
        description="Retrieve all data types from the decision service",
        tags=["data-types"]
    )
    async def get_all_data_types():
        """Get all data types."""
        try:
            data_types = repository.get_all()
            return data_types
        except Exception as e:
            logger.error(f"Error getting data types: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve data types: {str(e)}")
    
    @router.get(
        "/data-types/{data_type}",
        response_model=DataTypeModel,
        summary="Get data type by identifier",
        description="Retrieve a specific data type by its identifier",
        tags=["data-types"]
    )
    async def get_data_type(data_type: str = Path(..., description="Data type identifier")):
        """Get a specific data type."""
        try:
            dt = repository.get_by_id(data_type)
            if not dt:
                raise HTTPException(status_code=404, detail=f"Data type '{data_type}' not found")
            return dt
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting data type: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve data type: {str(e)}")
    
    @router.put(
        "/data-types/{data_type}",
        response_model=DataTypeModel,
        summary="Update a data type",
        description="Update an existing data type",
        tags=["data-types"]
    )
    async def update_data_type(data_type: str = Path(..., description="Data type identifier"), data_type_model: DataTypeModel = None):
        """Update a data type."""
        try:
            if not repository.exists(data_type):
                raise HTTPException(status_code=404, detail=f"Data type '{data_type}' not found")
            updated = repository.update(data_type, data_type_model)
            return updated
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating data type: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update data type: {str(e)}")
    
    @router.delete(
        "/data-types/{data_type}",
        summary="Delete a data type",
        description="Delete a data type from the decision service",
        tags=["data-types"]
    )
    async def delete_data_type(data_type: str = Path(..., description="Data type identifier")):
        """Delete a data type."""
        try:
            if not repository.exists(data_type):
                raise HTTPException(status_code=404, detail=f"Data type '{data_type}' not found")
            deleted = repository.delete(data_type)
            if deleted:
                return {"success": True, "message": f"Data type '{data_type}' deleted successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to delete data type")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting data type: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete data type: {str(e)}")
    
    return router

