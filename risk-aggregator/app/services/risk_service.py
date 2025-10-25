"""
Risk assessment service for individual entity risk evaluation.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics

from app.core.config import settings
from app.core.logging import setup_logging
from app.models.schemas import (
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    CustomerRiskRequest,
    CustomerRiskResponse,
    CustomerRiskProfile,
    RiskComponent,
    RiskLevel,
    RiskCategory,
)
from app.services.data_collector import DataCollector
from app.services.cache_service import CacheService

logger = setup_logging()


class RiskService:
    """Service for risk assessment operations."""

    def __init__(self):
        """Initialize risk service."""
        self.weights = settings.RISK_SCORE_WEIGHTS
        self.data_collector = DataCollector()
        self.cache_service = CacheService()

    async def assess_risk(
        self, request: RiskAssessmentRequest
    ) -> RiskAssessmentResponse:
        """
        Assess risk for an entity based on provided signals.

        Args:
            request: Risk assessment request

        Returns:
            RiskAssessmentResponse: Aggregated risk assessment
        """
        # Use custom weights if provided, otherwise use default
        weights = request.weights or self.weights

        # Normalize weights
        total_weight = sum(weights.get(signal.category.value, 0) for signal in request.signals)
        if total_weight == 0:
            total_weight = 1.0

        # Calculate risk components
        components: List[RiskComponent] = []
        total_weighted_score = 0.0
        total_confidence = 0.0

        for signal in request.signals:
            category_weight = weights.get(signal.category.value, 0) / total_weight
            weighted_score = signal.score * category_weight

            component = RiskComponent(
                category=signal.category,
                score=signal.score,
                weight=category_weight,
                weighted_score=weighted_score,
                confidence=signal.confidence,
                source=signal.source,
                details=signal.details,
            )
            components.append(component)

            total_weighted_score += weighted_score
            total_confidence += signal.confidence * category_weight

        # Determine risk level
        risk_level = self.get_risk_level(total_weighted_score)

        # Create response
        response = RiskAssessmentResponse(
            entity_id=request.entity_id,
            entity_type=request.entity_type,
            overall_risk_score=total_weighted_score,
            risk_level=risk_level,
            components=components,
            confidence=min(total_confidence, 1.0),
            assessed_at=datetime.utcnow(),
            metadata=request.metadata,
        )

        # Cache the result
        await self.cache_service.set_risk_assessment(request.entity_id, response)

        return response

    async def assess_customer_risk(
        self, request: CustomerRiskRequest
    ) -> CustomerRiskResponse:
        """
        Assess comprehensive risk for a customer.

        Args:
            request: Customer risk assessment request

        Returns:
            CustomerRiskResponse: Comprehensive customer risk profile
        """
        # Check cache first
        if not request.force_refresh:
            cached = await self.cache_service.get_customer_risk(request.customer_id)
            if cached:
                logger.info(f"Returning cached risk for customer {request.customer_id}")
                cached.cached = True
                return cached

        # Collect data from various sources
        signals = await self.data_collector.collect_customer_signals(
            customer_id=request.customer_id,
            include_kyc=request.include_kyc,
            include_transactions=request.include_transactions,
            include_credit=request.include_credit,
            include_loans=request.include_loans,
            include_repayments=request.include_repayments,
            time_window_days=request.time_window_days,
        )

        if not signals:
            logger.warning(f"No signals collected for customer {request.customer_id}")
            # Return default low risk if no data
            return CustomerRiskResponse(
                customer_id=request.customer_id,
                overall_risk_score=0.0,
                risk_level=RiskLevel.LOW,
                risk_profile=CustomerRiskProfile(),
                total_signals=0,
                confidence=0.0,
                assessed_at=datetime.utcnow(),
            )

        # Assess risk using collected signals
        assessment_request = RiskAssessmentRequest(
            entity_id=request.customer_id,
            entity_type="customer",
            signals=signals,
        )

        assessment = await self.assess_risk(assessment_request)

        # Build risk profile
        risk_profile = CustomerRiskProfile()
        for component in assessment.components:
            if component.category == RiskCategory.KYC:
                risk_profile.kyc_risk = component
            elif component.category == RiskCategory.TRANSACTION:
                risk_profile.transaction_risk = component
            elif component.category == RiskCategory.CREDIT:
                risk_profile.credit_risk = component
            elif component.category == RiskCategory.LOAN:
                risk_profile.loan_risk = component
            elif component.category == RiskCategory.REPAYMENT:
                risk_profile.repayment_risk = component

        # Generate recommendations
        recommendations = self._generate_recommendations(assessment)

        # Generate alerts
        alerts = self._generate_alerts(assessment)

        # Create response
        response = CustomerRiskResponse(
            customer_id=request.customer_id,
            overall_risk_score=assessment.overall_risk_score,
            risk_level=assessment.risk_level,
            risk_profile=risk_profile,
            total_signals=len(signals),
            confidence=assessment.confidence,
            assessed_at=assessment.assessed_at,
            cached=False,
            recommendations=recommendations,
            alerts=alerts,
        )

        # Cache the result
        await self.cache_service.set_customer_risk(request.customer_id, response)

        return response

    async def get_customer_risk(self, customer_id: str) -> Optional[CustomerRiskResponse]:
        """
        Get cached customer risk assessment.

        Args:
            customer_id: Customer identifier

        Returns:
            Optional[CustomerRiskResponse]: Cached risk assessment if available
        """
        return await self.cache_service.get_customer_risk(customer_id)

    async def get_risk_score(self, entity_id: str) -> Optional[float]:
        """
        Get quick risk score for an entity.

        Args:
            entity_id: Entity identifier

        Returns:
            Optional[float]: Risk score if available
        """
        cached = await self.cache_service.get_risk_score(entity_id)
        return cached

    def get_risk_level(self, score: float) -> RiskLevel:
        """
        Determine risk level from score.

        Args:
            score: Risk score (0-1)

        Returns:
            RiskLevel: Risk level classification
        """
        if score >= settings.HIGH_RISK_THRESHOLD:
            return RiskLevel.CRITICAL if score >= 0.9 else RiskLevel.HIGH
        elif score >= settings.MEDIUM_RISK_THRESHOLD:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_recommendations(
        self, assessment: RiskAssessmentResponse
    ) -> List[str]:
        """
        Generate recommendations based on risk assessment.

        Args:
            assessment: Risk assessment

        Returns:
            List[str]: List of recommendations
        """
        recommendations = []

        if assessment.overall_risk_score >= 0.75:
            recommendations.append("Require additional identity verification")
            recommendations.append("Implement transaction limits")
            recommendations.append("Enable enhanced monitoring")

        for component in assessment.components:
            if component.score >= 0.8:
                if component.category == RiskCategory.KYC:
                    recommendations.append("Review and update KYC documentation")
                elif component.category == RiskCategory.TRANSACTION:
                    recommendations.append("Investigate recent transaction patterns")
                elif component.category == RiskCategory.CREDIT:
                    recommendations.append("Review credit history and payment behavior")
                elif component.category == RiskCategory.LOAN:
                    recommendations.append("Reassess loan terms and conditions")
                elif component.category == RiskCategory.REPAYMENT:
                    recommendations.append("Monitor repayment schedule closely")

        return recommendations

    def _generate_alerts(self, assessment: RiskAssessmentResponse) -> List[Dict]:
        """
        Generate alerts based on risk assessment.

        Args:
            assessment: Risk assessment

        Returns:
            List[Dict]: List of alerts
        """
        alerts = []

        if assessment.overall_risk_score >= 0.9:
            alerts.append({
                "severity": "critical",
                "message": "Critical risk level detected - immediate action required",
                "timestamp": datetime.utcnow().isoformat(),
            })

        for component in assessment.components:
            if component.score >= 0.85:
                alerts.append({
                    "severity": "high",
                    "category": component.category.value,
                    "message": f"High risk detected in {component.category.value}",
                    "score": component.score,
                    "timestamp": datetime.utcnow().isoformat(),
                })

        return alerts

