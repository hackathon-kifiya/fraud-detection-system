"""
Risk assessment endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.core.logging import setup_logging
from app.models.schemas import (
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    CustomerRiskRequest,
    CustomerRiskResponse,
)
from app.services.risk_service import RiskService

logger = setup_logging()
router = APIRouter()


@router.post("/assess", response_model=RiskAssessmentResponse)
async def assess_risk(request: RiskAssessmentRequest):
    """
    Assess risk for a single entity based on provided signals.

    Args:
        request: Risk assessment request with multiple risk signals

    Returns:
        RiskAssessmentResponse: Aggregated risk assessment result
    """
    try:
        logger.info(f"Assessing risk for entity: {request.entity_id}")

        risk_service = RiskService()
        result = await risk_service.assess_risk(request)

        logger.info(
            f"Risk assessment completed for {request.entity_id}: "
            f"score={result.overall_risk_score:.2f}, level={result.risk_level}"
        )

        return result

    except Exception as e:
        logger.error(f"Error assessing risk for {request.entity_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")


@router.post("/customer", response_model=CustomerRiskResponse)
async def assess_customer_risk(request: CustomerRiskRequest):
    """
    Assess comprehensive risk for a customer by aggregating all available data sources.

    Args:
        request: Customer risk assessment request

    Returns:
        CustomerRiskResponse: Comprehensive customer risk profile
    """
    try:
        logger.info(f"Assessing customer risk for: {request.customer_id}")

        risk_service = RiskService()
        result = await risk_service.assess_customer_risk(request)

        logger.info(
            f"Customer risk assessment completed for {request.customer_id}: "
            f"score={result.overall_risk_score:.2f}, level={result.risk_level}"
        )

        return result

    except Exception as e:
        logger.error(
            f"Error assessing customer risk for {request.customer_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=f"Customer risk assessment failed: {str(e)}"
        )


@router.get("/customer/{customer_id}", response_model=CustomerRiskResponse)
async def get_customer_risk(customer_id: str):
    """
    Get cached risk assessment for a customer.

    Args:
        customer_id: Customer identifier

    Returns:
        CustomerRiskResponse: Customer risk profile
    """
    try:
        logger.info(f"Getting cached risk for customer: {customer_id}")

        risk_service = RiskService()
        result = await risk_service.get_customer_risk(customer_id)

        if not result:
            raise HTTPException(
                status_code=404, detail=f"No risk data found for customer {customer_id}"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer risk for {customer_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/score/{entity_id}")
async def get_risk_score(entity_id: str):
    """
    Get quick risk score for an entity.

    Args:
        entity_id: Entity identifier

    Returns:
        JSONResponse: Risk score and level
    """
    try:
        logger.info(f"Getting risk score for entity: {entity_id}")

        risk_service = RiskService()
        score = await risk_service.get_risk_score(entity_id)

        if score is None:
            raise HTTPException(
                status_code=404, detail=f"No risk score found for entity {entity_id}"
            )

        return JSONResponse(
            content={
                "entity_id": entity_id,
                "risk_score": score,
                "risk_level": risk_service.get_risk_level(score),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting risk score for {entity_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

