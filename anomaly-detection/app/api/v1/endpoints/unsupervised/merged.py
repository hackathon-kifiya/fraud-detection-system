"""
Merged Model Endpoints (KYC + Business + Customer Transaction)
"""
import time

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.v1.dependencies import get_anomaly_service
from app.core.logging import logger
from app.core.security import AuditLogger, InputSanitizer, get_api_key
from app.models.schemas import (
    AnomalyResponse,
    BatchCombinedRequest,
    BatchCombinedResponse,
    BatchCombinedResult,
    CombinedKYCBusinessData,
    ShapExplanation,
)
from app.services.unsupervised_anomaly_detector import UnsupervisedAnomalyDetectorService

router = APIRouter()


@router.post("/check", response_model=AnomalyResponse, tags=["Merged"])
async def check_merged(
    data: CombinedKYCBusinessData,
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    _: str = Depends(get_api_key),
):
    """
    Check merged KYC + Business data for anomalies

    Returns anomaly detection result with SHAP explanation for combined customer and business information

    Requires API key authentication via X-API-Key header
    """
    try:
        # Validate customer ID format
        if not InputSanitizer.validate_customer_id(data.customer_id):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid customer_id format. Must start with 'CUST_' "
                    "and contain only alphanumeric characters and underscores"
                ),
            )

        logger.info(
            "Processing merged check for customer: %s, business: %s",
            data.customer_id,
            data.business_tin_number,
        )

        # Predict anomaly using combined model
        is_anomaly, score, risk_level, explanation = service.predict_combined(data)

        # Audit log the anomaly detection
        AuditLogger.log_anomaly_detection(
            customer_id=data.customer_id,
            model_type="merged",
            is_anomaly=is_anomaly,
            risk_level=risk_level,
            score=score,
        )

        logger.info(
            "Merged check complete for %s: anomaly=%s, risk=%s, score=%.3f",
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
        logger.error("Merged model not available: %s", str(e))
        raise HTTPException(
            status_code=503,
            detail="Merged model not available. Please train the merged model first.",
        ) from e
    except Exception as e:
        logger.error("Error processing merged check: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing merged check: {str(e)}"
        ) from e


@router.post("/batch", response_model=BatchCombinedResponse, tags=["Merged"])
async def batch_merged_check(
    request: BatchCombinedRequest,
    http_request: Request,
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key),
):
    """
    Batch merged model anomaly detection

    Process multiple merged (KYC + Business) records at once

    Requires API key authentication via X-API-Key header
    """
    try:
        start_time = time.time()
        results = []
        anomaly_count = 0

        logger.info(
            "Processing batch merged check for %d records", len(request.records)
        )

        for record in request.records:
            try:
                # Validate customer ID format
                if not InputSanitizer.validate_customer_id(record.customer_id):
                    logger.warning("Invalid customer_id format: %s", record.customer_id)
                    results.append(
                        BatchCombinedResult(
                            customer_id=record.customer_id,
                            business_id=record.business_tin_number,
                            error="Invalid customer_id format",
                        )
                    )
                    continue

                is_anomaly, score, risk_level, explanation = service.predict_combined(
                    record
                )

                if is_anomaly:
                    anomaly_count += 1

                # Audit log each anomaly detection
                AuditLogger.log_anomaly_detection(
                    customer_id=record.customer_id,
                    model_type="merged",
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
            "Batch merged check complete: %d processed, %d anomalies, %.2fs",
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
        logger.error("Merged model not available: %s", str(e))
        raise HTTPException(
            status_code=503,
            detail="Merged model not available. Please train the merged model first.",
        ) from e
    except Exception as e:
        logger.error("Error processing batch merged check: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing batch merged check: {str(e)}"
        ) from e


@router.get("/stats", tags=["Merged"])
async def get_merged_stats(
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key),
):
    """
    Get merged model statistics

    Requires API key authentication via X-API-Key header
    """
    if service.combined_model is None:
        raise HTTPException(
            status_code=503,
            detail="Merged model not available. Please train the merged model first.",
        )

    return {
        "model_type": "Isolation Forest (Merged KYC+Business)",
        "features": service.combined_feature_names,
        "num_features": len(service.combined_feature_names),
        "contamination": (
            service.combined_model.contamination if service.combined_model else None
        ),
        "n_estimators": (
            service.combined_model.n_estimators if service.combined_model else None
        ),
    }

