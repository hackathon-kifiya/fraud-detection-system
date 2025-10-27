"""
Aggregation service for batch risk processing.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import time

from app.core.config import settings
from app.core.logging import setup_logging
from app.models.schemas import (
    BatchRiskRequest,
    BatchRiskResponse,
    BatchEntityResult,
    AggregationJobRequest,
    AggregationJobResponse,
    JobStatus,
    RiskAssessmentRequest,
)
from app.services.risk_service import RiskService

logger = setup_logging()


class AggregationService:
    """Service for batch risk aggregation operations."""

    def __init__(self):
        """Initialize aggregation service."""
        self.risk_service = RiskService()
        self.jobs: Dict[str, AggregationJobResponse] = {}
        self.weights = settings.RISK_SCORE_WEIGHTS.copy()

    async def aggregate_batch(self, request: BatchRiskRequest) -> BatchRiskResponse:
        """
        Aggregate risk assessments for multiple entities.

        Args:
            request: Batch risk request

        Returns:
            BatchRiskResponse: Batch aggregation results
        """
        start_time = time.time()
        results: List[BatchEntityResult] = []

        if request.parallel:
            # Process entities in parallel
            tasks = [
                self._process_entity(entity, request.weights)
                for entity in request.entities
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    entity = request.entities[i]
                    processed_results.append(
                        BatchEntityResult(
                            entity_id=entity.entity_id,
                            entity_type=entity.entity_type,
                            risk_score=0.0,
                            risk_level="low",
                            success=False,
                            error=str(result),
                        )
                    )
                else:
                    processed_results.append(result)
            results = processed_results
        else:
            # Process entities sequentially
            for entity in request.entities:
                result = await self._process_entity(entity, request.weights)
                results.append(result)

        # Calculate statistics
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        risk_scores = [r.risk_score for r in results if r.success]
        average_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.0

        processing_time = time.time() - start_time

        return BatchRiskResponse(
            total_entities=len(request.entities),
            successful=successful,
            failed=failed,
            results=results,
            average_risk_score=average_risk,
            processing_time_seconds=processing_time,
            processed_at=datetime.utcnow(),
        )

    async def _process_entity(
        self, entity, custom_weights: Optional[Dict[str, float]] = None
    ) -> BatchEntityResult:
        """
        Process a single entity for batch aggregation.

        Args:
            entity: Entity to process
            custom_weights: Optional custom weights

        Returns:
            BatchEntityResult: Processing result
        """
        try:
            assessment_request = RiskAssessmentRequest(
                entity_id=entity.entity_id,
                entity_type=entity.entity_type,
                signals=entity.signals,
                weights=custom_weights,
            )

            assessment = await self.risk_service.assess_risk(assessment_request)

            return BatchEntityResult(
                entity_id=entity.entity_id,
                entity_type=entity.entity_type,
                risk_score=assessment.overall_risk_score,
                risk_level=assessment.risk_level,
                success=True,
            )

        except Exception as e:
            logger.error(f"Error processing entity {entity.entity_id}: {str(e)}")
            return BatchEntityResult(
                entity_id=entity.entity_id,
                entity_type=entity.entity_type,
                risk_score=0.0,
                risk_level="low",
                success=False,
                error=str(e),
            )

    async def create_job(
        self, request: AggregationJobRequest
    ) -> AggregationJobResponse:
        """
        Create an aggregation job.

        Args:
            request: Job creation request

        Returns:
            AggregationJobResponse: Created job information
        """
        job_id = str(uuid.uuid4())

        job = AggregationJobResponse(
            job_id=job_id,
            job_name=request.job_name,
            status=JobStatus.PENDING,
            total_entities=len(request.entity_ids),
            created_at=datetime.utcnow(),
        )

        # Store job
        self.jobs[job_id] = job

        logger.info(f"Created aggregation job {job_id}: {request.job_name}")

        return job

    async def process_job(self, job_id: str):
        """
        Process an aggregation job in the background.

        Args:
            job_id: Job identifier
        """
        if job_id not in self.jobs:
            logger.error(f"Job {job_id} not found")
            return

        job = self.jobs[job_id]

        try:
            # Update job status
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()

            logger.info(f"Starting job {job_id}: {job.job_name}")

            # TODO: Implement actual job processing
            # This would involve:
            # 1. Fetching data for all entity_ids
            # 2. Processing each entity
            # 3. Updating progress
            # 4. Storing results

            # Simulate processing
            await asyncio.sleep(1)

            # Update job status
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.processed_entities = job.total_entities
            job.successful = job.total_entities
            job.progress_percentage = 100.0

            logger.info(f"Completed job {job_id}")

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {str(e)}")
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()

    async def get_job(self, job_id: str) -> Optional[AggregationJobResponse]:
        """
        Get job status and results.

        Args:
            job_id: Job identifier

        Returns:
            Optional[AggregationJobResponse]: Job information if found
        """
        return self.jobs.get(job_id)

    async def update_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Update risk weight configuration.

        Args:
            weights: New weight configuration

        Returns:
            Dict[str, float]: Updated weights
        """
        # Validate weights
        total = sum(weights.values())
        if total <= 0:
            raise ValueError("Total weight must be positive")

        # Normalize weights
        normalized = {k: v / total for k, v in weights.items()}

        # Update weights
        self.weights.update(normalized)

        logger.info(f"Updated risk weights: {normalized}")

        return self.weights

    async def get_weights(self) -> Dict[str, float]:
        """
        Get current risk weight configuration.

        Returns:
            Dict[str, float]: Current weights
        """
        return self.weights.copy()

