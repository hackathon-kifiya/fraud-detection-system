"""
Transaction Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
import time

from app.models.schemas import (
    TransactionData,
    AnomalyResponse,
    BatchTransactionRequest,
    BatchTransactionResponse,
    BatchTransactionResult,
    ShapExplanation
)
from app.services.anomaly_detector import AnomalyDetectorService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def get_anomaly_service(request: Request) -> AnomalyDetectorService:
    """Dependency to get anomaly service from app state"""
    return request.app.state.anomaly_service


@router.post("/check", response_model=AnomalyResponse, tags=["Transaction"])
async def check_transaction(
    data: TransactionData,
    service: AnomalyDetectorService = Depends(get_anomaly_service)
):
    """
    Check transaction for anomalies
    
    Returns anomaly detection result with SHAP explanation
    """
    try:
        logger.info(f"Processing transaction check for: {data.transaction_id}")
        
        # Predict anomaly
        is_anomaly, score, risk_level, explanation = service.predict_transaction(data)
        
        logger.info(
            f"Transaction check complete for {data.transaction_id}: "
            f"anomaly={is_anomaly}, risk={risk_level}, score={score:.3f}"
        )
        
        return AnomalyResponse(
            is_anomaly=is_anomaly,
            anomaly_score=score,
            risk_level=risk_level,
            explanation=ShapExplanation(**explanation)
        )
        
    except Exception as e:
        logger.error(f"Error processing transaction check: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing transaction check: {str(e)}"
        )


@router.post("/batch", response_model=BatchTransactionResponse, tags=["Transaction"])
async def batch_transaction_check(
    request: BatchTransactionRequest,
    service: AnomalyDetectorService = Depends(get_anomaly_service)
):
    """
    Batch transaction anomaly detection
    
    Process multiple transactions at once
    """
    start_time = time.time()
    results = []
    anomaly_count = 0
    
    logger.info(f"Processing batch transaction check for {len(request.transactions)} transactions")
    
    for transaction in request.transactions:
        try:
            is_anomaly, score, risk_level, explanation = service.predict_transaction(transaction)
            
            if is_anomaly:
                anomaly_count += 1
            
            results.append(BatchTransactionResult(
                customer_id=transaction.customer_id,
                result=AnomalyResponse(
                    is_anomaly=is_anomaly,
                    anomaly_score=score,
                    risk_level=risk_level,
                    explanation=ShapExplanation(**explanation)
                )
            ))
            
        except Exception as e:
            logger.error(f"Error processing transaction {transaction.customer_id}: {str(e)}")
            results.append(BatchTransactionResult(
                customer_id=transaction.customer_id,
                error=str(e)
            ))
    
    processing_time = time.time() - start_time
    
    logger.info(
        f"Batch transaction check complete: {len(results)} processed, "
        f"{anomaly_count} anomalies, {processing_time:.2f}s"
    )
    
    return BatchTransactionResponse(
        batch_results=results,
        total_processed=len(results),
        total_anomalies=anomaly_count,
        processing_time_seconds=processing_time
    )


@router.get("/stats", tags=["Transaction"])
async def get_transaction_stats(
    service: AnomalyDetectorService = Depends(get_anomaly_service)
):
    """
    Get transaction model statistics
    """
    return {
        "model_type": "Isolation Forest",
        "features": service.transaction_feature_names,
        "num_features": len(service.transaction_feature_names),
        "contamination": service.transaction_model.contamination if service.transaction_model else None,
        "n_estimators": service.transaction_model.n_estimators if service.transaction_model else None
    }