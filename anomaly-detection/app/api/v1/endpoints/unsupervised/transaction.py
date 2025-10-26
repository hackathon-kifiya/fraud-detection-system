"""
Transaction Endpoints
"""
import time

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.v1.dependencies import get_anomaly_service
from app.core.logging import logger
from app.core.security import AuditLogger, InputSanitizer, get_api_key
from app.models.schemas import (
    AnomalyResponse,
    BatchTransactionRequest,
    BatchTransactionResponse,
    BatchTransactionResult,
    CustomerBatchTransactionRequest,
    CustomerBatchTransactionResponse,
    ShapExplanation,
    TransactionData,
)
from app.services.unsupervised_anomaly_detector import UnsupervisedAnomalyDetectorService

router = APIRouter()


@router.post("/check", response_model=AnomalyResponse, tags=["Transaction"])
async def check_transaction(
    data: TransactionData,
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    _: str = Depends(get_api_key),
):
    """
    Check a single transaction for anomalies

    Returns anomaly detection result with SHAP explanation

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
            "Processing transaction check for customer: %s on date: %s",
            data.customer_id,
            data.date,
        )

        # Predict anomaly
        is_anomaly, score, risk_level, explanation = service.predict_transaction(data)

        # Audit log the anomaly detection
        AuditLogger.log_anomaly_detection(
            customer_id=data.customer_id,
            model_type="transaction",
            is_anomaly=is_anomaly,
            risk_level=risk_level,
            score=score,
        )

        logger.info(
            "Transaction check complete for %s: anomaly=%s, risk=%s, score=%.3f",
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
        logger.error("Error processing transaction check: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing transaction check: {str(e)}"
        ) from e


@router.post("/batch", response_model=BatchTransactionResponse, tags=["Transaction"])
async def batch_transaction_check(
    request: BatchTransactionRequest,
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    _: str = Depends(get_api_key),
):
    """
    Batch transaction anomaly detection

    Process multiple transactions (from different customers) at once

    Requires API key authentication via X-API-Key header
    """
    start_time = time.time()
    results = []
    anomaly_count = 0

    logger.info("Processing batch transaction check for %d records", len(request.transactions))

    for transaction in request.transactions:
        try:
            # Validate customer ID format
            if not InputSanitizer.validate_customer_id(transaction.customer_id):
                logger.warning("Invalid customer_id format: %s", transaction.customer_id)
                results.append(
                    BatchTransactionResult(
                        customer_id=transaction.customer_id,
                        error="Invalid customer_id format",
                    )
                )
                continue

            is_anomaly, score, risk_level, explanation = service.predict_transaction(
                transaction
            )

            if is_anomaly:
                anomaly_count += 1

            # Audit log each anomaly detection
            AuditLogger.log_anomaly_detection(
                customer_id=transaction.customer_id,
                model_type="transaction",
                is_anomaly=is_anomaly,
                risk_level=risk_level,
                score=score,
            )

            results.append(
                BatchTransactionResult(
                    customer_id=transaction.customer_id,
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
                "Error processing transaction for customer %s: %s",
                transaction.customer_id,
                str(e),
            )
            results.append(
                BatchTransactionResult(customer_id=transaction.customer_id, error=str(e))
            )

    processing_time = time.time() - start_time

    logger.info(
        "Batch transaction check complete: %d processed, %d anomalies, %.2fs",
        len(results),
        anomaly_count,
        processing_time,
    )

    return BatchTransactionResponse(
        batch_results=results,
        total_processed=len(results),
        total_anomalies=anomaly_count,
        processing_time_seconds=processing_time,
    )


@router.get("/stats", tags=["Transaction"])
async def get_transaction_stats(
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key),
):
    """
    Get transaction model statistics

    Requires API key authentication via X-API-Key header
    """
    return {
        "model_type": "Isolation Forest",
        "features": service.transaction_feature_names,
        "num_features": len(service.transaction_feature_names),
        "contamination": service.transaction_model.contamination
        if service.transaction_model
        else None,
        "n_estimators": service.transaction_model.n_estimators
        if service.transaction_model
        else None,
    }


@router.post(
    "/customer/batch", response_model=CustomerBatchTransactionResponse, tags=["Transaction"]
)
async def batch_customer_transactions(
    request: CustomerBatchTransactionRequest,
    service: UnsupervisedAnomalyDetectorService = Depends(get_anomaly_service),
    api_key: str = Depends(get_api_key),
):
    """
    Batch transaction anomaly detection for a single customer

    Process all transactions for a specific customer and generate a customer-level
    risk assessment based on aggregate transaction anomalies

    Requires API key authentication via X-API-Key header
    """
    try:
        start_time = time.time()

        # Validate customer ID format
        if not InputSanitizer.validate_customer_id(request.customer_id):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid customer_id format. Must start with 'CUST_' "
                    "and contain only alphanumeric characters and underscores"
                ),
            )

        logger.info(
            "Processing customer batch transactions for customer: %s with %d transactions",
            request.customer_id,
            len(request.transactions),
        )

        # Predict customer-level anomalies
        (
            customer_flagged,
            customer_anomaly_score,
            customer_risk_level,
            transaction_results,
        ) = service.predict_customer_batch(request.customer_id, request.transactions)

        # Convert transaction results to BatchTransactionResult objects
        batch_transaction_results = []
        anomaly_count = 0

        for idx, (is_anomaly, score, risk_level, explanation) in enumerate(
            transaction_results
        ):
            if is_anomaly:
                anomaly_count += 1

            batch_transaction_results.append(
                BatchTransactionResult(
                    customer_id=request.customer_id,
                    result=AnomalyResponse(
                        is_anomaly=is_anomaly,
                        anomaly_score=score,
                        risk_level=risk_level,
                        explanation=ShapExplanation(**explanation),
                    ),
                )
            )

        # Audit log the customer-level detection
        AuditLogger.log_anomaly_detection(
            customer_id=request.customer_id,
            model_type="customer_transaction",
            is_anomaly=customer_flagged,
            risk_level=customer_risk_level,
            score=customer_anomaly_score,
        )

        processing_time = time.time() - start_time

        logger.info(
            "Customer batch transactions complete for %s: flagged=%s, anomalies=%d/%d, risk=%s, score=%.3f, time=%.2fs",
            request.customer_id,
            customer_flagged,
            anomaly_count,
            len(request.transactions),
            customer_risk_level,
            customer_anomaly_score,
            processing_time,
        )

        return CustomerBatchTransactionResponse(
            customer_id=request.customer_id,
            total_transactions=len(request.transactions),
            anomaly_count=anomaly_count,
            customer_risk_level=customer_risk_level,
            customer_anomaly_score=customer_anomaly_score,
            customer_flagged=customer_flagged,
            transaction_results=batch_transaction_results,
            processing_time_seconds=processing_time,
        )

    except ValueError as e:
        logger.error("Validation error in customer batch: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(
            "Error processing customer batch transactions for %s: %s",
            request.customer_id,
            str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error processing customer batch transactions: {str(e)}",
        ) from e
