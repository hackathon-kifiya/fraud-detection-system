"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.middleware.error_handler import add_error_handlers
from app.middleware.rate_limiter import RateLimitMiddleware
from app.services.anomaly_detector import AnomalyDetectorService
from app.core.security import get_security_headers

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
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
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        headers = get_security_headers()
        for key, value in headers.items():
            response.headers[key] = value
        return response


app.add_middleware(SecurityHeadersMiddleware)

# Add error handlers
add_error_handlers(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Global service instance
anomaly_service = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global anomaly_service
    logger.info("Starting up application...")

    # Initialize anomaly detector service
    anomaly_service = AnomalyDetectorService()
    await anomaly_service.initialize()

    # Store in app state for access in endpoints
    app.state.anomaly_service = anomaly_service

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
        "health": "/health"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    service_health = {
        "status": "healthy",
        "version": settings.VERSION,
    }

    if anomaly_service:
        service_health.update({
            "kyc_model_loaded": anomaly_service.kyc_model is not None,
            "transaction_model_loaded": anomaly_service.transaction_model is not None,
        })

    return service_health


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )