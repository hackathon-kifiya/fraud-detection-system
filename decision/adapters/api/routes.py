"""API route handlers."""

from fastapi import APIRouter, HTTPException, Depends, Path
from typing import Annotated, List
import logging
from domain.models import DecisionRequest, DecisionConfigModel, DataTypeDecisionConfig, MergedDataTypeConfig
from usecases.decision_service import DecisionService, ConfigService
from adapters.api.schemas import DecisionResponse, ConfigUpdateResponse
from adapters.client.data_management_client import DataManagementClient

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


def create_data_type_config_router(config_service: ConfigService) -> APIRouter:
    """Create data-type-specific configuration router."""
    router = APIRouter()
    data_mgmt_client = DataManagementClient()
    
    @router.get(
        "/config/data-types",
        summary="List data types with custom configs",
        description="Get all data types that have custom configuration overrides"
    )
    async def list_data_type_configs():
        """List all data types with custom configs."""
        try:
            configs = config_service.config_repository.get_all_data_type_configs()
            return {"data_types": configs}
        except Exception as e:
            logger.error(f"Error listing data type configs: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get(
        "/config/data-types/{data_type}",
        response_model=MergedDataTypeConfig,
        summary="Get merged config for data type",
        description="Get configuration for a specific data type (defaults + overrides)"
    )
    async def get_data_type_config(data_type: str = Path(..., description="Data type identifier")):
        """Get merged configuration for a specific data type."""
        try:
            # Verify data type exists in data-management-service
            dt = data_mgmt_client.get_data_type(data_type)
            if not dt:
                raise HTTPException(status_code=404, detail=f"Data type '{data_type}' not found")
            
            merged_config = config_service.config_repository.get_data_type_config(data_type)
            return merged_config
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting data type config: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post(
        "/config/data-types/{data_type}",
        response_model=DataTypeDecisionConfig,
        summary="Create/update data-type-specific config",
        description="Create or update configuration overrides for a specific data type"
    )
    async def update_data_type_config(
        data_type: str = Path(..., description="Data type identifier"),
        config: DataTypeDecisionConfig = None
    ):
        """Create or update data-type-specific configuration."""
        try:
            # Verify data type exists in data-management-service
            dt = data_mgmt_client.get_data_type(data_type)
            if not dt:
                raise HTTPException(status_code=404, detail=f"Data type '{data_type}' not found")
            
            config.data_type = data_type
            updated_config = config_service.config_repository.update_data_type_config(data_type, config)
            return updated_config
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating data type config: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.delete(
        "/config/data-types/{data_type}",
        summary="Delete data-type-specific config",
        description="Remove configuration overrides for a data type (revert to defaults)"
    )
    async def delete_data_type_config(data_type: str = Path(..., description="Data type identifier")):
        """Delete data-type-specific configuration."""
        try:
            deleted = config_service.config_repository.delete_data_type_config(data_type)
            if deleted:
                return {"success": True, "message": f"Configuration for '{data_type}' reverted to defaults"}
            else:
                raise HTTPException(status_code=404, detail=f"No custom configuration found for '{data_type}'")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting data type config: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router

