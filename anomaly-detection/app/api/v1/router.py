"""
API Router Configuration
Combines all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import kyc, transaction

api_router = APIRouter()

# Include KYC endpoints
api_router.include_router(kyc.router, prefix="/kyc", tags=["KYC"])

# Include Transaction endpoints
api_router.include_router(
    transaction.router, prefix="/transaction", tags=["Transaction"]
)
