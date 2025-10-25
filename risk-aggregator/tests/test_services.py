"""
Service layer tests.
"""

import pytest
from app.services.risk_service import RiskService
from app.models.schemas import RiskAssessmentRequest, RiskSignal, RiskCategory


@pytest.mark.asyncio
async def test_risk_service_assess_risk(sample_risk_assessment_request):
    """Test risk service assessment."""
    service = RiskService()
    request = RiskAssessmentRequest(**sample_risk_assessment_request)
    
    result = await service.assess_risk(request)
    
    assert result.entity_id == request.entity_id
    assert 0.0 <= result.overall_risk_score <= 1.0
    assert result.risk_level in ["low", "medium", "high", "critical"]
    assert len(result.components) > 0


def test_risk_service_get_risk_level():
    """Test risk level determination."""
    service = RiskService()
    
    assert service.get_risk_level(0.1).value == "low"
    assert service.get_risk_level(0.5).value == "medium"
    assert service.get_risk_level(0.8).value == "high"
    assert service.get_risk_level(0.95).value == "critical"


@pytest.mark.asyncio
async def test_cache_service():
    """Test cache service."""
    from app.services.cache_service import CacheService
    from app.models.schemas import RiskAssessmentResponse, RiskLevel
    
    service = CacheService()
    
    # Create test assessment
    assessment = RiskAssessmentResponse(
        entity_id="test-123",
        entity_type="customer",
        overall_risk_score=0.7,
        risk_level=RiskLevel.HIGH,
        components=[],
        confidence=0.9,
    )
    
    # Set cache
    await service.set_risk_assessment("test-123", assessment)
    
    # Get from cache
    cached = await service.get_risk_assessment("test-123")
    
    assert cached is not None
    assert cached.entity_id == "test-123"
    assert cached.overall_risk_score == 0.7

