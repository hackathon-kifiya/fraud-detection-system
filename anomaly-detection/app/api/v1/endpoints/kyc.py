"""
KYC Endpoints
"""
import time

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.v1.dependencies import get_anomaly_service
from app.core.logging import logger
from app.core.security import AuditLogger, get_api_key
from app.models.schemas import (
    AnomalyResponse,
    BatchCombinedRequest,
    BatchCombinedResponse,
    BatchCombinedResult,
    BatchKYCRequest,
    BatchKYCResponse,
    BatchKYCResult,
    CombinedKYCBusinessData,
    KYCData,
    ShapExplanation,
)
from app.api.v1.dependencies import get_unsupervised_anomaly_detector_service
from app.services.unsupervised_anomaly_detector import UnsupervisedAnomalyDetectorService

router = APIRouter()

@router.post("/check", response_model=AnomalyResponse, tags=["KYC"])
async def check_kyc(
    data: KYCData,
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    _: str = Depends(get_api_key),
):
    """
    Check KYC data for anomalies

    Returns anomaly detection result with SHAP explanation

    Requires API key authentication via X-API-Key header
    """
    try:
        logger.info("Processing KYC check for customer: %s", data.customer_id)

        # Predict anomaly
        is_anomaly, score, risk_level, explanation = service.predict_kyc(data)

        # Audit log the anomaly detection
        AuditLogger.log_anomaly_detection(
            customer_id=data.customer_id,
            model_type="kyc",
            is_anomaly=is_anomaly,
            risk_level=risk_level,
            score=score,
        )

        logger.info(
            "KYC check complete for %s: anomaly=%s, risk=%s, score=%.3f",
            data.customer_id,
            is_anomaly,
            risk_level,
            score,
        )

        return AnomalyResponse(
            is_anomaly=is_anomaly,
            anomaly_score=score,
            risk_level=risk_level,
            explanation=ShapExplanation(**explanation),
        )

    except Exception as e:
        logger.error("Error processing KYC check: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing KYC check: {str(e)}"
        ) from e


@router.post("/batch", response_model=BatchKYCResponse, tags=["KYC"])
async def batch_kyc_check(
    request: BatchKYCRequest,
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    _: str = Depends(get_api_key),
):
    """
    Batch KYC anomaly detection

    Process multiple KYC records at once

    Requires API key authentication via X-API-Key header
    """
    start_time = time.time()
    results = []
    anomaly_count = 0

    logger.info("Processing batch KYC check for %d records", len(request.records))

    for record in request.records:
        try:
            is_anomaly, score, risk_level, explanation = service.predict_kyc(record)

            if is_anomaly:
                anomaly_count += 1

            # Audit log each anomaly detection
            AuditLogger.log_anomaly_detection(
                customer_id=record.customer_id,
                model_type="kyc",
                is_anomaly=is_anomaly,
                risk_level=risk_level,
                score=score,
            )

            results.append(
                BatchKYCResult(
                    customer_id=record.customer_id,
                    result=AnomalyResponse(
                        is_anomaly=is_anomaly,
                        anomaly_score=score,
                        risk_level=risk_level,
                        explanation=ShapExplanation(**explanation),
                    ),
                )
            )

        except Exception as e:
            logger.error("Error processing customer %s: %s", record.customer_id, str(e))
            results.append(BatchKYCResult(customer_id=record.customer_id, error=str(e)))

    processing_time = time.time() - start_time

    logger.info(
        "Batch KYC check complete: %d processed, %d anomalies, %.2fs",
        len(results),
        anomaly_count,
        processing_time,
    )

    return BatchKYCResponse(
        batch_results=results,
        total_processed=len(results),
        total_anomalies=anomaly_count,
        processing_time_seconds=processing_time,
    )


@router.get("/stats", tags=["KYC"])
async def get_kyc_stats(
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key),
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
        "n_estimators": service.kyc_model.n_estimators if service.kyc_model else None,
    }


@router.post("/combined/check", response_model=AnomalyResponse, tags=["KYC+Business"])
async def check_combined_kyc_business(
    data: CombinedKYCBusinessData,
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    _: str = Depends(get_api_key),
):
    """
    Check combined KYC + Business data for anomalies

    Returns anomaly detection result with SHAP explanation for both
    customer and business information

    Requires API key authentication via X-API-Key header
    """
    try:
        logger.info(
            "Processing combined KYC+Business check for customer: %s, business: %s",
            data.customer_id,
            data.business_tin_number,
        )

        # Predict anomaly using combined model
        is_anomaly, score, risk_level, explanation = service.predict_combined(data)

        # Audit log the anomaly detection
        AuditLogger.log_anomaly_detection(
            customer_id=data.customer_id,
            model_type="combined_kyc_business",
            is_anomaly=is_anomaly,
            risk_level=risk_level,
            score=score,
        )

        logger.info(
            "Combined check complete for %s: anomaly=%s, risk=%s, score=%.3f",
            data.customer_id,
            is_anomaly,
            risk_level,
            score,
        )

        return AnomalyResponse(
            is_anomaly=is_anomaly,
            anomaly_score=score,
            risk_level=risk_level,
            explanation=ShapExplanation(**explanation),
        )

    except ValueError as e:
        logger.error("Combined model not available: %s", str(e))
        raise HTTPException(
            status_code=503,
            detail="Combined model not available. Please train the combined model first.",
        ) from e
    except Exception as e:
        logger.error("Error processing combined check: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing combined check: {str(e)}"
        ) from e


@router.post(
    "/combined/batch", response_model=BatchCombinedResponse, tags=["KYC+Business"]
)
async def batch_combined_kyc_business_check(
    request: BatchCombinedRequest,
    http_request: Request,
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key),
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

        logger.info(
            "Processing batch combined check for %d records", len(request.records)
        )

        for record in request.records:
            try:
                is_anomaly, score, risk_level, explanation = service.predict_combined(
                    record
                )

                if is_anomaly:
                    anomaly_count += 1

                # Audit log each anomaly detection
                AuditLogger.log_anomaly_detection(
                    customer_id=record.customer_id,
                    model_type="combined_kyc_business",
                    is_anomaly=is_anomaly,
                    risk_level=risk_level,
                    score=score,
                )

                results.append(
                    BatchCombinedResult(
                        customer_id=record.customer_id,
                        business_id=record.business_tin_number,
                        result=AnomalyResponse(
                            is_anomaly=is_anomaly,
                            anomaly_score=score,
                            risk_level=risk_level,
                            explanation=ShapExplanation(**explanation),
                        ),
                    )
                )

            except Exception as e:
                logger.error(
                    "Error processing customer %s, business %s: %s",
                    record.customer_id,
                    record.business_tin_number,
                    str(e),
                )
                results.append(
                    BatchCombinedResult(
                        customer_id=record.customer_id,
                        business_id=record.business_tin_number,
                        error=str(e),
                    )
                )

        processing_time = time.time() - start_time

        logger.info(
            "Batch combined check complete: %d processed, %d anomalies, %.2fs",
            len(results),
            anomaly_count,
            processing_time,
        )

        return BatchCombinedResponse(
            batch_results=results,
            total_processed=len(results),
            total_anomalies=anomaly_count,
            processing_time_seconds=processing_time,
        )

    except ValueError as e:
        logger.error("Combined model not available: %s", str(e))
        raise HTTPException(
            status_code=503,
            detail="Combined model not available. Please train the combined model first.",
        ) from e
    except Exception as e:
        logger.error("Error processing batch combined check: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing batch combined check: {str(e)}"
        ) from e


@router.get("/combined/stats", tags=["KYC+Business"])
async def get_combined_stats(
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key),
):
    """
    Get combined KYC+Business model statistics

    Requires API key authentication via X-API-Key header
    """
    if service.combined_model is None:
        raise HTTPException(
            status_code=503,
            detail="Combined model not available. Please train the combined model first.",
        )

    return {
        "model_type": "Isolation Forest (Combined KYC+Business)",
        "features": service.combined_feature_names,
        "num_features": len(service.combined_feature_names),
        "contamination": (
            service.combined_model.contamination if service.combined_model else None
        ),
        "n_estimators": (
            service.combined_model.n_estimators if service.combined_model else None
        ),
    }