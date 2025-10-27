"""Main application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from adapters.database.config_repository import PostgreSQLConfigRepository
from usecases.decision_service import DecisionService, ConfigService
from adapters.api.routes import create_config_router, create_decision_router, create_data_type_config_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application."""
    # Startup
    logger.info("Initializing decision service...")
    
    # Initialize repositories
    config_repository = PostgreSQLConfigRepository()
    
    # Initialize databases
    try:
        config_repository.initialize_schema()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Store repository in app state for dependency injection
    app.state.config_repository = config_repository
    
    # Setup routes after repository is initialized
    setup_routes()
    
    logger.info("Decision service initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down decision service...")


app = FastAPI(
    title="Decision Service",
    description="Configurable decision service that aggregates scores from rule engine, anomaly detection, and predictive engine",
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


# Dependency injection for services
def get_config_service(app: FastAPI) -> ConfigService:
    """Get configuration service."""
    config_repository = app.state.config_repository
    return ConfigService(config_repository)


def get_decision_service(app: FastAPI) -> DecisionService:
    """Get decision service."""
    config_repository = app.state.config_repository
    return DecisionService(config_repository)


@app.get(
    "/health",
    summary="Health Check",
    description="Check the health status of the decision service",
    tags=["health"]
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "decision-service",
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
        "message": "Decision Service API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "endpoints": {
            "health": "/health",
            "config_get": "GET /config",
            "config_update": "POST /config",
            "decide": "POST /decide"
        }
    }


# Register routers
def setup_routes():
    """Setup API routes."""
    # Get services from app state
    config_service = get_config_service(app)
    decision_service = get_decision_service(app)
    
    # Create routers
    config_router = create_config_router(config_service, decision_service)
    decision_router = create_decision_router(decision_service)
    data_type_config_router = create_data_type_config_router(config_service)
    
    # Register routers
    app.include_router(config_router, tags=["configuration"])
    app.include_router(decision_router, tags=["decision"])
    app.include_router(data_type_config_router, tags=["data-type-configuration"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5003))
    uvicorn.run(app, host="0.0.0.0", port=port)
