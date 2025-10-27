"""
Main FastAPI application entry point for Risk Aggregator Service.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.error_handler import add_exception_handlers
from app.middleware.rate_limiter import RateLimiterMiddleware

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Risk Aggregator Service...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Version: {settings.API_VERSION}")
    yield
    logger.info("Shutting down Risk Aggregator Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Risk Aggregator Service - Combine and aggregate risk signals from multiple sources",
    version=settings.API_VERSION,
    docs_url=f"{settings.API_V1_PREFIX}/docs" if settings.ENABLE_DOCS else None,
    redoc_url=f"{settings.API_V1_PREFIX}/redoc" if settings.ENABLE_DOCS else None,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if settings.ENABLE_DOCS else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimiterMiddleware)

# Add exception handlers
add_exception_handlers(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return JSONResponse(
        content={
            "service": "Risk Aggregator Service",
            "version": settings.API_VERSION,
            "status": "running",
            "docs": f"{settings.API_V1_PREFIX}/docs" if settings.ENABLE_DOCS else None,
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "risk-aggregator",
            "version": settings.API_VERSION,
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

