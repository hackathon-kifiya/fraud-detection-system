"""
API Router Configuration
Combines all endpoint routers separated by supervised and unsupervised approaches
"""
from fastapi import APIRouter

from app.api.v1.endpoints import kyc
from app.api.v1.endpoints.unsupervised import transaction as unsupervised_transaction
from app.api.v1.endpoints.unsupervised import merged as unsupervised_merged
from app.api.v1.endpoints.supervised import transaction as supervised_transaction
from app.api.v1.endpoints.supervised import merged as supervised_merged

api_router = APIRouter()

# ==================== UNSUPERVISED ENDPOINTS ====================

# Include KYC endpoints (unsupervised)
api_router.include_router(kyc.router, prefix="/unsupervised/kyc", tags=["Unsupervised - KYC"])

# Include unsupervised transaction endpoints
api_router.include_router(
    unsupervised_transaction.router, prefix="/unsupervised/transaction", tags=["Unsupervised - Transaction"]
)

# Include unsupervised merged model endpoints
api_router.include_router(
    unsupervised_merged.router, prefix="/unsupervised/merged", tags=["Unsupervised - Merged"]
)

# ==================== SUPERVISED ENDPOINTS ====================

# Include supervised transaction endpoints
api_router.include_router(
    supervised_transaction.router, prefix="/supervised/transaction", tags=["Supervised - Transaction"]
)

# Include supervised merged model endpoints
api_router.include_router(
    supervised_merged.router, prefix="/supervised/merged", tags=["Supervised - Merged"]
)
