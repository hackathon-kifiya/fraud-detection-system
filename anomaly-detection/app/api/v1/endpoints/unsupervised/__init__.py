from fastapi import APIRouter
from app.api.v1.endpoints.kyc import router as unsupervised_kyc_router
router = APIRouter(prefix="/unsupervised")

router.include_router(unsupervised_kyc_router, prefix="/kyc", tags=["KYC"])
