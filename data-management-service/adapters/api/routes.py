"""API route handlers."""

from fastapi import APIRouter, HTTPException, Path
from typing import List
import logging
from usecases.data_type_service import DataTypeService
from adapters.api.schemas import DataTypeResponse, CreateDataTypeRequest, UpdateDataTypeRequest, DeleteResponse

logger = logging.getLogger(__name__)


def create_data_type_router(service: DataTypeService) -> APIRouter:
    """Create data type router."""
    router = APIRouter()
    
    @router.post(
        "/data-types",
        response_model=DataTypeResponse,
        summary="Create a new data type",
        description="Create a new data type schema in the data management service",
        tags=["data-types"],
        status_code=201
    )
    async def create_data_type(request: CreateDataTypeRequest):
        """Create a new data type."""
        try:
            from domain.data_type_models import CreateDataTypeRequest as DomainRequest
            domain_request = DomainRequest(**request.dict())
            created = service.create_data_type(domain_request)
            return DataTypeResponse(**created.dict())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error creating data type: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create data type: {str(e)}")
    
    @router.get(
        "/data-types",
        response_model=List[DataTypeResponse],
        summary="Get all data types",
        description="Retrieve all data types from the data management service",
        tags=["data-types"]
    )
    async def get_all_data_types():
        """Get all data types."""
        try:
            data_types = service.get_all_data_types()
            return [DataTypeResponse(**dt.dict()) for dt in data_types]
        except Exception as e:
            logger.error(f"Error getting data types: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve data types: {str(e)}")
    
    @router.get(
        "/data-types/{data_type}",
        response_model=DataTypeResponse,
        summary="Get data type by identifier",
        description="Retrieve a specific data type by its identifier",
        tags=["data-types"]
    )
    async def get_data_type(data_type: str = Path(..., description="Data type identifier")):
        """Get a specific data type."""
        try:
            dt = service.get_data_type(data_type)
            if not dt:
                raise HTTPException(status_code=404, detail=f"Data type '{data_type}' not found")
            return DataTypeResponse(**dt.dict())
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting data type: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve data type: {str(e)}")
    
    @router.put(
        "/data-types/{data_type}",
        response_model=DataTypeResponse,
        summary="Update a data type",
        description="Update an existing data type",
        tags=["data-types"]
    )
    async def update_data_type(
        request: UpdateDataTypeRequest,
        data_type: str = Path(..., description="Data type identifier")
    ):
        """Update a data type."""
        try:
            from domain.data_type_models import UpdateDataTypeRequest as DomainRequest
            domain_request = DomainRequest(**request.dict())
            updated = service.update_data_type(data_type, domain_request)
            return DataTypeResponse(**updated.dict())
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Error updating data type: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update data type: {str(e)}")
    
    @router.delete(
        "/data-types/{data_type}",
        response_model=DeleteResponse,
        summary="Delete a data type",
        description="Delete a data type from the data management service",
        tags=["data-types"]
    )
    async def delete_data_type(data_type: str = Path(..., description="Data type identifier")):
        """Delete a data type."""
        try:
            deleted = service.delete_data_type(data_type)
            if deleted:
                return DeleteResponse(success=True, message=f"Data type '{data_type}' deleted successfully")
            else:
                raise HTTPException(status_code=404, detail=f"Data type '{data_type}' not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting data type: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete data type: {str(e)}")
    
    @router.get(
        "/data-types/{data_type}/sample-data",
        summary="Get sample data for a data type",
        description="Retrieve sample data for a specific data type",
        tags=["data-types"]
    )
    async def get_sample_data(
        data_type: str = Path(..., description="Data type identifier"),
        limit: int = 5
    ):
        """Get sample data for a data type."""
        try:
            dt = service.get_data_type(data_type)
            if not dt:
                raise HTTPException(status_code=404, detail=f"Data type '{data_type}' not found")
            
            # Return the sample_data field from the data type
            sample_data = dt.sample_data if dt.sample_data else []
            
            # If sample_data is a list, limit the results
            if isinstance(sample_data, list):
                return sample_data[:limit]
            
            # If it's a dict or other type, return as-is
            return sample_data
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting sample data: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve sample data: {str(e)}")
    
    return router

