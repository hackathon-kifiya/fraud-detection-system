"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field
from domain.models import DecisionConfigModel


class DecisionResponse(BaseModel):
    """API response model for decision endpoint."""
    entity_id: str
    final_score: float = Field(..., ge=0, le=1, description="Final weighted score (0-1)")
    final_score_percent: float = Field(..., description="Final score as percentage (0-100)")
    decision: str = Field(..., description="Decision recommendation")
    breakdown: dict = Field(..., description="Score breakdown by engine")
    confidence: float = Field(..., description="Decision confidence (0-1)")


class ConfigUpdateResponse(BaseModel):
    """API response model for config update."""
    success: bool
    message: str
    config: dict

