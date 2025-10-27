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
    data_type: str = Field(None, description="Optional data type for type-specific configuration")


class DecisionResult(BaseModel):
    """Domain model for decision result."""
    entity_id: str
    final_score: float
    final_score_percent: float
    decision: str
    breakdown: dict
    confidence: float


class DataTypeDecisionConfig(BaseModel):
    """Model for data-type-specific decision configuration."""
    data_type: str
    auto_approve_threshold: float = Field(None, ge=0, le=100, description="Override for auto approve threshold")
    auto_reject_threshold: float = Field(None, ge=0, le=100, description="Override for auto reject threshold")
    rule_engine_weight: float = Field(None, ge=0, le=100, description="Override for rule engine weight")
    anomaly_detection_weight: float = Field(None, ge=0, le=100, description="Override for anomaly detection weight")
    predictive_engine_weight: float = Field(None, ge=0, le=100, description="Override for predictive engine weight")
    model_based_scoring: bool = Field(None, description="Override for model-based scoring")
    model_based_thresholds: bool = Field(None, description="Override for model-based thresholds")
    created_at: datetime = Field(None, description="Creation timestamp")
    updated_at: datetime = Field(None, description="Last update timestamp")


class MergedDataTypeConfig(BaseModel):
    """Model for merged configuration (defaults + overrides)."""
    data_type: str
    config: DecisionConfigModel
    is_custom: bool = Field(description="Whether this data type has custom overrides")
    overridden_fields: list = Field(default_factory=list, description="List of fields that are overridden")


class DecisionType:
    """Decision type constants."""
    AUTO_APPROVE = "AUTO_APPROVE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    AUTO_REJECT = "AUTO_REJECT"

