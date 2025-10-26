"""Domain models for decision service."""

from pydantic import BaseModel, Field, validator
from typing import Literal
from datetime import datetime


class DecisionConfigModel(BaseModel):
    """Domain model for decision configuration."""
    model_based_thresholds: bool = Field(default=False, description="Enable model-based decision thresholds")
    auto_approve_threshold: float = Field(default=25.0, ge=0, le=100)
    auto_reject_threshold: float = Field(default=85.0, ge=0, le=100)
    model_based_scoring: bool = Field(default=False, description="Enable model-based scoring")
    rule_engine_weight: float = Field(default=40.0, ge=0, le=100)
    anomaly_detection_weight: float = Field(default=35.0, ge=0, le=100)
    predictive_engine_weight: float = Field(default=25.0, ge=0, le=100)
    
    @validator('auto_approve_threshold')
    def validate_auto_approve(cls, v, values):
        if 'auto_reject_threshold' in values and v >= values['auto_reject_threshold']:
            raise ValueError('auto_approve_threshold must be less than auto_reject_threshold')
        return v
    
    @validator('auto_reject_threshold')
    def validate_auto_reject(cls, v, values):
        if 'auto_approve_threshold' in values and v <= values['auto_approve_threshold']:
            raise ValueError('auto_reject_threshold must be greater than auto_approve_threshold')
        return v


class DecisionRequest(BaseModel):
    """Request model for decision endpoint."""
    entity_id: str
    rule_engine_score: float = Field(..., ge=0, le=1, description="Rule engine normalized score (0-1)")
    anomaly_detection_score: float = Field(..., ge=0, le=1, description="Anomaly detection normalized score (0-1)")
    predictive_engine_score: float = Field(..., ge=0, le=1, description="Predictive engine normalized score (0-1)")


class DecisionResult(BaseModel):
    """Domain model for decision result."""
    entity_id: str
    final_score: float
    final_score_percent: float
    decision: str
    breakdown: dict
    confidence: float


class DecisionType:
    """Decision type constants."""
    AUTO_APPROVE = "AUTO_APPROVE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    AUTO_REJECT = "AUTO_REJECT"

