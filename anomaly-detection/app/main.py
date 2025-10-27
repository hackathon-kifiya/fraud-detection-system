"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.error_handler import add_error_handlers
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.services.unsupervised_anomaly_detector import UnsupervisedAnomalyDetectorService
from app.services.supervised_anomaly_detector import SupervisedAnomalyDetectorService

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add error handlers
add_error_handlers(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Global service instances
unsupervised_anomaly_service = None
supervised_anomaly_service = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global unsupervised_anomaly_service, supervised_anomaly_service
    logger.info("Starting up application...")

    # Initialize unsupervised anomaly detector service
    try:
        unsupervised_anomaly_service = UnsupervisedAnomalyDetectorService()
        await unsupervised_anomaly_service.initialize()
        app.state.unsupervised_anomaly_service = unsupervised_anomaly_service
        logger.info("✓ Unsupervised anomaly detection service initialized")
    except Exception as e:
        logger.warning(f"⚠ Unsupervised models not available: {e}")
        app.state.unsupervised_anomaly_service = None

    # Initialize supervised anomaly detector service
    try:
        supervised_anomaly_service = SupervisedAnomalyDetectorService()
        await supervised_anomaly_service.initialize()
        app.state.supervised_anomaly_service = supervised_anomaly_service
        logger.info("✓ Supervised anomaly detection service initialized")
    except Exception as e:
        logger.warning(f"⚠ Supervised models not available: {e}")
        app.state.supervised_anomaly_service = None

    logger.info("Application startup complete!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application...")
    # Add cleanup logic here if needed


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    service_health = {
        "status": "healthy",
        "version": settings.VERSION,
    }

    if unsupervised_anomaly_service:
        service_health.update(
            {
                "unsupervised_kyc_model_loaded": unsupervised_anomaly_service.kyc_model is not None,
                "unsupervised_transaction_model_loaded": unsupervised_anomaly_service.transaction_model
                is not None,
                "unsupervised_combined_model_loaded": unsupervised_anomaly_service.combined_model
                is not None,
            }
        )

    if supervised_anomaly_service:
        service_health.update(
            {
                "supervised_kyc_model_loaded": supervised_anomaly_service.kyc_model is not None,
                "supervised_transaction_model_loaded": supervised_anomaly_service.transaction_model
                is not None,
                "supervised_combined_model_loaded": supervised_anomaly_service.combined_model
                is not None,
            }
        )

    return service_health


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
