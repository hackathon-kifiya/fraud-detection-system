"""
Risk aggregation endpoints for batch processing.
"""

from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.core.logging import setup_logging
from app.models.schemas import (
    BatchRiskRequest,
    BatchRiskResponse,
    AggregationJobRequest,
    AggregationJobResponse,
)
from app.services.aggregation_service import AggregationService

logger = setup_logging()
router = APIRouter()


@router.post("/batch", response_model=BatchRiskResponse)
async def aggregate_batch(request: BatchRiskRequest):
    """
    Aggregate risk assessments for multiple entities.

    Args:
        request: Batch risk aggregation request

    Returns:
        BatchRiskResponse: Aggregated results for all entities
    """
    try:
        logger.info(f"Processing batch risk aggregation for {len(request.entities)} entities")

        aggregation_service = AggregationService()
        result = await aggregation_service.aggregate_batch(request)

        logger.info(
            f"Batch aggregation completed: {result.total_entities} entities processed, "
            f"{result.successful} successful, {result.failed} failed"
        )

        return result

    except Exception as e:
        logger.error(f"Error in batch aggregation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch aggregation failed: {str(e)}")


@router.post("/job", response_model=AggregationJobResponse)
async def create_aggregation_job(
    request: AggregationJobRequest, background_tasks: BackgroundTasks
):
    """
    Create a background job for large-scale risk aggregation.

    Args:
        request: Aggregation job request
        background_tasks: FastAPI background tasks

    Returns:
        AggregationJobResponse: Job information
    """
    try:
        logger.info(f"Creating aggregation job: {request.job_name}")

        aggregation_service = AggregationService()
        job = await aggregation_service.create_job(request)

        # Add background task to process the job
        background_tasks.add_task(
            aggregation_service.process_job, job.job_id
        )

        logger.info(f"Aggregation job created: {job.job_id}")

        return job

    except Exception as e:
        logger.error(f"Error creating aggregation job: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create aggregation job: {str(e)}"
        )


@router.get("/job/{job_id}", response_model=AggregationJobResponse)
async def get_aggregation_job(job_id: str):
    """
    Get status and results of an aggregation job.

    Args:
        job_id: Job identifier

    Returns:
        AggregationJobResponse: Job status and results
    """
    try:
        logger.info(f"Getting aggregation job: {job_id}")

        aggregation_service = AggregationService()
        job = await aggregation_service.get_job(job_id)

        if not job:
            raise HTTPException(
                status_code=404, detail=f"Job {job_id} not found"
            )

        return job

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting aggregation job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weights")
async def update_risk_weights(weights: dict):
    """
    Update risk weight configuration for aggregation.

    Args:
        weights: Dictionary of risk category weights

    Returns:
        JSONResponse: Updated weights confirmation
    """
    try:
        logger.info(f"Updating risk weights: {weights}")

        aggregation_service = AggregationService()
        updated_weights = await aggregation_service.update_weights(weights)

        return JSONResponse(
            content={
                "message": "Risk weights updated successfully",
                "weights": updated_weights,
            }
        )

    except Exception as e:
        logger.error(f"Error updating risk weights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weights")
async def get_risk_weights():
    """
    Get current risk weight configuration.

    Returns:
        JSONResponse: Current risk weights
    """
    try:
        aggregation_service = AggregationService()
        weights = await aggregation_service.get_weights()

        return JSONResponse(content={"weights": weights})

    except Exception as e:
        logger.error(f"Error getting risk weights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

