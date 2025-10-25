"""
KYC Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Request
import time

from app.models.schemas import (
    KYCData,
    AnomalyResponse,
    BatchKYCRequest,
    BatchKYCResponse,
    BatchKYCResult,
    ShapExplanation,
    CombinedKYCBusinessData,
    BatchCombinedRequest,
    BatchCombinedResponse,
    BatchCombinedResult
)
from app.services.anomaly_detector import AnomalyDetectorService
from app.services.kyc_service import KYCService
from app.core.logging import get_logger
from app.core.security import get_api_key, InputSanitizer, AuditLogger

logger = get_logger(__name__)
router = APIRouter()

# Initialize KYC service
kyc_service = KYCService()


def get_anomaly_service(request: Request) -> AnomalyDetectorService:
    """Dependency to get anomaly service from app state"""
    return request.app.state.anomaly_service


@router.post("/check", response_model=AnomalyResponse, tags=["KYC"])
async def check_kyc(
    data: KYCData,
    request: Request,
    service: AnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key)
):
    """
    Check KYC data for anomalies

    Returns anomaly detection result with SHAP explanation

    Requires API key authentication via X-API-Key header
    """
    try:
        # Validate customer ID format
        if not InputSanitizer.validate_customer_id(data.customer_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid customer_id format. Must start with 'CUST_' and contain only alphanumeric characters and underscores"
            )

        logger.info(f"Processing KYC check for customer: {data.customer_id}")

        # Predict anomaly
        is_anomaly, score, risk_level, explanation = service.predict_kyc(data)

        # Audit log the anomaly detection
        AuditLogger.log_anomaly_detection(
            customer_id=data.customer_id,
            model_type="kyc",
            is_anomaly=is_anomaly,
            risk_level=risk_level,
            score=score
        )

        logger.info(
            f"KYC check complete for {data.customer_id}: "
            f"anomaly={is_anomaly}, risk={risk_level}, score={score:.3f}"
        )

        return AnomalyResponse(
            is_anomaly=is_anomaly,
            anomaly_score=score,
            risk_level=risk_level,
            explanation=ShapExplanation(**explanation)
        )

    except Exception as e:
        logger.error(f"Error processing KYC check: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing KYC check: {str(e)}"
        )


@router.post("/batch", response_model=BatchKYCResponse, tags=["KYC"])
async def batch_kyc_check(
    request: BatchKYCRequest,
    http_request: Request,
    service: AnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key)
):
    """
    Batch KYC anomaly detection

    Process multiple KYC records at once

    Requires API key authentication via X-API-Key header
    """
    start_time = time.time()
    results = []
    anomaly_count = 0

    logger.info(f"Processing batch KYC check for {len(request.records)} records")

    for record in request.records:
        try:
            # Validate customer ID format
            if not InputSanitizer.validate_customer_id(record.customer_id):
                logger.warning(f"Invalid customer_id format: {record.customer_id}")
                results.append(BatchKYCResult(
                    customer_id=record.customer_id,
                    error="Invalid customer_id format"
                ))
                continue

            is_anomaly, score, risk_level, explanation = service.predict_kyc(record)

            if is_anomaly:
                anomaly_count += 1

            # Audit log each anomaly detection
            AuditLogger.log_anomaly_detection(
                customer_id=record.customer_id,
                model_type="kyc",
                is_anomaly=is_anomaly,
                risk_level=risk_level,
                score=score
            )

            results.append(BatchKYCResult(
                customer_id=record.customer_id,
                result=AnomalyResponse(
                    is_anomaly=is_anomaly,
                    anomaly_score=score,
                    risk_level=risk_level,
                    explanation=ShapExplanation(**explanation)
                )
            ))

        except Exception as e:
            logger.error(f"Error processing customer {record.customer_id}: {str(e)}")
            results.append(BatchKYCResult(
                customer_id=record.customer_id,
                error=str(e)
            ))

    processing_time = time.time() - start_time

    logger.info(
        f"Batch KYC check complete: {len(results)} processed, "
        f"{anomaly_count} anomalies, {processing_time:.2f}s"
    )

    return BatchKYCResponse(
        batch_results=results,
        total_processed=len(results),
        total_anomalies=anomaly_count,
        processing_time_seconds=processing_time
    )


@router.get("/stats", tags=["KYC"])
async def get_kyc_stats(
    service: AnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key)
):
    """
    Get KYC model statistics

    Requires API key authentication via X-API-Key header
    """
    return {
        "model_type": "Isolation Forest",
        "features": service.kyc_feature_names,
        "num_features": len(service.kyc_feature_names),
        "contamination": service.kyc_model.contamination if service.kyc_model else None,
        "n_estimators": service.kyc_model.n_estimators if service.kyc_model else None
    }


@router.post("/combined/check", response_model=AnomalyResponse, tags=["KYC+Business"])
async def check_combined_kyc_business(
    data: CombinedKYCBusinessData,
    request: Request,
    service: AnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key)
):
    """
    Check combined KYC + Business data for anomalies

    Returns anomaly detection result with SHAP explanation for both customer and business information

    Requires API key authentication via X-API-Key header
    """
    try:
        # Validate customer ID format
        if not InputSanitizer.validate_customer_id(data.customer_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid customer_id format. Must start with 'CUST_' and contain only alphanumeric characters and underscores"
            )

        logger.info(f"Processing combined KYC+Business check for customer: {data.customer_id}, business: {data.business_id}")

        # Predict anomaly using combined model
        is_anomaly, score, risk_level, explanation = service.predict_combined(data)

        # Audit log the anomaly detection
        AuditLogger.log_anomaly_detection(
            customer_id=data.customer_id,
            model_type="combined_kyc_business",
            is_anomaly=is_anomaly,
            risk_level=risk_level,
            score=score
        )

        logger.info(
            f"Combined check complete for {data.customer_id}/{data.business_id}: "
            f"anomaly={is_anomaly}, risk={risk_level}, score={score:.3f}"
        )

        return AnomalyResponse(
            is_anomaly=is_anomaly,
            anomaly_score=score,
            risk_level=risk_level,
            explanation=ShapExplanation(**explanation)
        )

    except ValueError as e:
        logger.error(f"Combined model not available: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Combined model not available. Please train the combined model first."
        )
    except Exception as e:
        logger.error(f"Error processing combined check: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing combined check: {str(e)}"
        )


@router.post("/combined/batch", response_model=BatchCombinedResponse, tags=["KYC+Business"])
async def batch_combined_kyc_business_check(
    request: BatchCombinedRequest,
    http_request: Request,
    service: AnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key)
):
    """
    Batch combined KYC + Business anomaly detection

    Process multiple combined records at once

    Requires API key authentication via X-API-Key header
    """
    try:
        start_time = time.time()
        results = []
        anomaly_count = 0

        logger.info(f"Processing batch combined check for {len(request.records)} records")

        for record in request.records:
            try:
                # Validate customer ID format
                if not InputSanitizer.validate_customer_id(record.customer_id):
                    logger.warning(f"Invalid customer_id format: {record.customer_id}")
                    results.append(BatchCombinedResult(
                        customer_id=record.customer_id,
                        business_id=record.business_id,
                        error="Invalid customer_id format"
                    ))
                    continue

                is_anomaly, score, risk_level, explanation = service.predict_combined(record)

                if is_anomaly:
                    anomaly_count += 1

                # Audit log each anomaly detection
                AuditLogger.log_anomaly_detection(
                    customer_id=record.customer_id,
                    model_type="combined_kyc_business",
                    is_anomaly=is_anomaly,
                    risk_level=risk_level,
                    score=score
                )

                results.append(BatchCombinedResult(
                    customer_id=record.customer_id,
                    business_id=record.business_id,
                    result=AnomalyResponse(
                        is_anomaly=is_anomaly,
                        anomaly_score=score,
                        risk_level=risk_level,
                        explanation=ShapExplanation(**explanation)
                    )
                ))

            except Exception as e:
                logger.error(f"Error processing customer {record.customer_id}, business {record.business_id}: {str(e)}")
                results.append(BatchCombinedResult(
                    customer_id=record.customer_id,
                    business_id=record.business_id,
                    error=str(e)
                ))

        processing_time = time.time() - start_time

        logger.info(
            f"Batch combined check complete: {len(results)} processed, "
            f"{anomaly_count} anomalies, {processing_time:.2f}s"
        )

        return BatchCombinedResponse(
            batch_results=results,
            total_processed=len(results),
            total_anomalies=anomaly_count,
            processing_time_seconds=processing_time
        )

    except ValueError as e:
        logger.error(f"Combined model not available: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Combined model not available. Please train the combined model first."
        )
    except Exception as e:
        logger.error(f"Error processing batch combined check: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing batch combined check: {str(e)}"
        )


@router.get("/combined/stats", tags=["KYC+Business"])
async def get_combined_stats(
    service: AnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key)
):
    """
    Get combined KYC+Business model statistics

    Requires API key authentication via X-API-Key header
    """
    if service.combined_model is None:
        raise HTTPException(
            status_code=503,
            detail="Combined model not available. Please train the combined model first."
        )

    return {
        "model_type": "Isolation Forest (Combined KYC+Business)",
        "features": service.combined_feature_names,
        "num_features": len(service.combined_feature_names),
        "contamination": service.combined_model.contamination if service.combined_model else None,
        "n_estimators": service.combined_model.n_estimators if service.combined_model else None
    }


@router.post("/check-with-masking", tags=["KYC", "Security Demo"])
async def check_kyc_with_masking(
    data: KYCData,
    request: Request,
    mask_level: str = "partial",
    service: AnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key)
):
    """
    Check KYC data for anomalies with data masking demonstration

    This endpoint demonstrates the data masking security feature.
    The response includes both the anomaly detection result and masked customer data.

    Query Parameters:
    - mask_level: "none", "partial", or "full" (default: "partial")

    Requires API key authentication via X-API-Key header
    """
    try:
        # Validate customer ID format
        if not InputSanitizer.validate_customer_id(data.customer_id):
            raise HTTPException(
                status_code=400,
                detail="Invalid customer_id format. Must start with 'CUST_' and contain only alphanumeric characters and underscores"
            )

        # Validate mask level
        if mask_level not in ["none", "partial", "full"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid mask_level. Must be 'none', 'partial', or 'full'"
            )

        logger.info(f"Processing KYC check with masking for customer: {data.customer_id}, mask_level: {mask_level}")

        # Log data access
        kyc_service.log_kyc_access(
            user_id=api_key[:10] if api_key else "unknown",
            customer_id=data.customer_id,
            action=f"check_with_masking_{mask_level}"
        )

        # Predict anomaly
        is_anomaly, score, risk_level, explanation = service.predict_kyc(data)

        # Audit log the anomaly detection
        AuditLogger.log_anomaly_detection(
            customer_id=data.customer_id,
            model_type="kyc",
            is_anomaly=is_anomaly,
            risk_level=risk_level,
            score=score
        )

        # Convert data to dict for masking
        data_dict = data.dict()

        # Apply data masking
        masked_customer_data = kyc_service.mask_kyc_data(data_dict, mask_level=mask_level)

        logger.info(
            f"KYC check with masking complete for {data.customer_id}: "
            f"anomaly={is_anomaly}, risk={risk_level}, score={score:.3f}, mask_level={mask_level}"
        )

        return {
            "anomaly_result": {
                "is_anomaly": is_anomaly,
                "anomaly_score": score,
                "risk_level": risk_level,
                "explanation": ShapExplanation(**explanation).dict()
            },
            "masked_customer_data": masked_customer_data,
            "masking_applied": mask_level,
            "security_note": "Sensitive fields have been masked according to the specified mask level"
        }

    except Exception as e:
        logger.error(f"Error processing KYC check with masking: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing KYC check with masking: {str(e)}"
        )