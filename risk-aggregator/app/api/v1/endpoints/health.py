"""
Health check endpoints.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings

router = APIRouter()


@router.get("")
async def health_check():
    """
    Check service health status.

    Returns:
        JSONResponse: Service health information
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "risk-aggregator",
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT,
        }
    )


@router.get("/ready")
async def readiness_check():
    """
    Check if service is ready to handle requests.

    Returns:
        JSONResponse: Service readiness information
    """
    # Add checks for external services if needed
    return JSONResponse(
        content={
            "status": "ready",
            "service": "risk-aggregator",
            "version": settings.API_VERSION,
        }
    )


@router.get("/live")
async def liveness_check():
    """
    Check if service is alive.

    Returns:
        JSONResponse: Service liveness information
    """
    return JSONResponse(
        content={
            "status": "alive",
            "service": "risk-aggregator",
        }
    )

