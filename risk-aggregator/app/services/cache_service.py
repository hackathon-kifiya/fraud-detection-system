"""
Cache service for storing and retrieving risk assessments.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import json

from app.core.config import settings
from app.core.logging import setup_logging
from app.models.schemas import (
    RiskAssessmentResponse,
    CustomerRiskResponse,
)

logger = setup_logging()


class CacheService:
    """Service for caching risk assessments."""

    def __init__(self):
        """Initialize cache service."""
        self.cache: Dict[str, tuple] = {}  # key: (data, expiry_time)
        self.ttl = settings.CACHE_TTL
        self.enabled = settings.CACHE_ENABLED

    async def set_risk_assessment(
        self, entity_id: str, assessment: RiskAssessmentResponse
    ):
        """
        Cache a risk assessment.

        Args:
            entity_id: Entity identifier
            assessment: Risk assessment to cache
        """
        if not self.enabled:
            return

        cache_key = f"risk_assessment:{entity_id}"
        expiry = datetime.utcnow() + timedelta(seconds=self.ttl)

        self.cache[cache_key] = (assessment, expiry)
        logger.debug(f"Cached risk assessment for {entity_id}")

    async def get_risk_assessment(
        self, entity_id: str
    ) -> Optional[RiskAssessmentResponse]:
        """
        Get cached risk assessment.

        Args:
            entity_id: Entity identifier

        Returns:
            Optional[RiskAssessmentResponse]: Cached assessment if available
        """
        if not self.enabled:
            return None

        cache_key = f"risk_assessment:{entity_id}"

        if cache_key not in self.cache:
            return None

        data, expiry = self.cache[cache_key]

        # Check if expired
        if datetime.utcnow() > expiry:
            del self.cache[cache_key]
            logger.debug(f"Expired cache for {entity_id}")
            return None

        logger.debug(f"Cache hit for {entity_id}")
        return data

    async def set_customer_risk(
        self, customer_id: str, risk: CustomerRiskResponse
    ):
        """
        Cache customer risk assessment.

        Args:
            customer_id: Customer identifier
            risk: Customer risk assessment to cache
        """
        if not self.enabled:
            return

        cache_key = f"customer_risk:{customer_id}"
        expiry = datetime.utcnow() + timedelta(seconds=self.ttl)

        self.cache[cache_key] = (risk, expiry)
        logger.debug(f"Cached customer risk for {customer_id}")

    async def get_customer_risk(
        self, customer_id: str
    ) -> Optional[CustomerRiskResponse]:
        """
        Get cached customer risk assessment.

        Args:
            customer_id: Customer identifier

        Returns:
            Optional[CustomerRiskResponse]: Cached risk if available
        """
        if not self.enabled:
            return None

        cache_key = f"customer_risk:{customer_id}"

        if cache_key not in self.cache:
            return None

        data, expiry = self.cache[cache_key]

        # Check if expired
        if datetime.utcnow() > expiry:
            del self.cache[cache_key]
            logger.debug(f"Expired customer risk cache for {customer_id}")
            return None

        logger.debug(f"Customer risk cache hit for {customer_id}")
        return data

    async def get_risk_score(self, entity_id: str) -> Optional[float]:
        """
        Get cached risk score.

        Args:
            entity_id: Entity identifier

        Returns:
            Optional[float]: Cached risk score if available
        """
        # Try risk assessment cache first
        assessment = await self.get_risk_assessment(entity_id)
        if assessment:
            return assessment.overall_risk_score

        # Try customer risk cache
        customer_risk = await self.get_customer_risk(entity_id)
        if customer_risk:
            return customer_risk.overall_risk_score

        return None

    async def invalidate(self, entity_id: str):
        """
        Invalidate cache for an entity.

        Args:
            entity_id: Entity identifier
        """
        keys_to_delete = [
            f"risk_assessment:{entity_id}",
            f"customer_risk:{entity_id}",
        ]

        for key in keys_to_delete:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Invalidated cache: {key}")

    async def clear_expired(self):
        """Clear all expired cache entries."""
        now = datetime.utcnow()
        expired_keys = [
            key for key, (data, expiry) in self.cache.items() if now > expiry
        ]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")

