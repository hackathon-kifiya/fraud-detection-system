"""
API v1 Router - Main router for all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import risk, health, aggregation

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk Assessment"])
api_router.include_router(aggregation.router, prefix="/aggregate", tags=["Aggregation"])

