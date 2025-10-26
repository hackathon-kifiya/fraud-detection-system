"""Main application entry point for Data Management Service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from adapters.database.data_type_repository import PostgreSQLDataTypeRepository
from usecases.data_type_service import DataTypeService
from usecases.seed_data_types import seed_data_types
from adapters.api.routes import create_data_type_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application."""
    # Startup
    logger.info("Initializing Data Management Service...")
    
    # Initialize repository
    repository = PostgreSQLDataTypeRepository()
    
    # Initialize database
    try:
        repository.initialize_schema()
        
        # Seed data types
        logger.info("Seeding data types...")
        seed_data_types(repository)
        logger.info("Data type seeding completed")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Store repository in app state for dependency injection
    app.state.repository = repository
    
    # Setup routes after repository is initialized
    setup_routes(app)
    
    logger.info("Data Management Service initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Data Management Service...")


app = FastAPI(
    title="Data Management Service",
    description="Single source of truth for data type definitions across all fraud detection services",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection for service
def get_data_type_service(app: FastAPI) -> DataTypeService:
    """Get data type service."""
    repository = app.state.repository
    return DataTypeService(repository)


@app.get(
    "/health",
    summary="Health Check",
    description="Check the health status of the data management service",
    tags=["health"]
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "data-management-service",
        "version": "0.1.0"
    }


@app.get(
    "/",
    summary="API Information",
    description="Get API information and documentation links"
)
async def root():
    """Root endpoint."""
    return {
        "message": "Data Management Service API",
        "version": "0.1.0",
        "description": "Single source of truth for data type definitions",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "endpoints": {
            "health": "/health",
            "data_types": {
                "list": "GET /data-types",
                "get": "GET /data-types/{data_type}",
                "create": "POST /data-types",
                "update": "PUT /data-types/{data_type}",
                "delete": "DELETE /data-types/{data_type}"
            }
        }
    }


# Register routers
def setup_routes(app: FastAPI):
    """Setup API routes."""
    # Get service from app state
    service = get_data_type_service(app)
    
    # Create router
    data_type_router = create_data_type_router(service)
    
    # Register router
    app.include_router(data_type_router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5004))
    uvicorn.run(app, host="0.0.0.0", port=port)

