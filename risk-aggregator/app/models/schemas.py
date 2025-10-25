"""
Pydantic schemas for request/response models.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class RiskLevel(str, Enum):
    """Risk level enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(str, Enum):
    """Risk category enumeration."""

    KYC = "kyc"
    TRANSACTION = "transaction"
    CREDIT = "credit"
    LOAN = "loan"
    REPAYMENT = "repayment"
    BEHAVIORAL = "behavioral"
    EXTERNAL = "external"


class JobStatus(str, Enum):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# Risk Signal Models
# ============================================================================


class RiskSignal(BaseModel):
    """Individual risk signal from a data source."""

    category: RiskCategory
    score: float = Field(..., ge=0.0, le=1.0, description="Risk score between 0 and 1")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence in the signal"
    )
    source: str = Field(..., description="Source of the risk signal")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional signal details"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @validator("score")
    def validate_score(cls, v):
        """Validate score is within bounds."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score must be between 0 and 1")
        return v


# ============================================================================
# Risk Assessment Request/Response
# ============================================================================


class RiskAssessmentRequest(BaseModel):
    """Request for risk assessment."""

    entity_id: str = Field(..., description="Identifier of the entity to assess")
    entity_type: str = Field(
        default="customer", description="Type of entity (customer, transaction, etc.)"
    )
    signals: List[RiskSignal] = Field(..., description="List of risk signals")
    weights: Optional[Dict[str, float]] = Field(
        default=None, description="Custom weights for risk categories"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )


class RiskComponent(BaseModel):
    """Individual risk component in the assessment."""

    category: RiskCategory
    score: float = Field(..., ge=0.0, le=1.0)
    weight: float = Field(..., ge=0.0, le=1.0)
    weighted_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str
    details: Optional[Dict[str, Any]] = None


class RiskAssessmentResponse(BaseModel):
    """Response for risk assessment."""

    entity_id: str
    entity_type: str
    overall_risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel
    components: List[RiskComponent]
    confidence: float = Field(..., ge=0.0, le=1.0)
    assessed_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Customer Risk Assessment
# ============================================================================


class CustomerRiskRequest(BaseModel):
    """Request for comprehensive customer risk assessment."""

    customer_id: str
    include_kyc: bool = True
    include_transactions: bool = True
    include_credit: bool = True
    include_loans: bool = True
    include_repayments: bool = True
    time_window_days: int = Field(default=90, description="Time window for analysis")
    force_refresh: bool = Field(
        default=False, description="Force refresh instead of using cache"
    )


class CustomerRiskProfile(BaseModel):
    """Comprehensive customer risk profile."""

    kyc_risk: Optional[RiskComponent] = None
    transaction_risk: Optional[RiskComponent] = None
    credit_risk: Optional[RiskComponent] = None
    loan_risk: Optional[RiskComponent] = None
    repayment_risk: Optional[RiskComponent] = None


class CustomerRiskResponse(BaseModel):
    """Response for customer risk assessment."""

    customer_id: str
    overall_risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel
    risk_profile: CustomerRiskProfile
    total_signals: int
    confidence: float = Field(..., ge=0.0, le=1.0)
    assessed_at: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = False
    recommendations: Optional[List[str]] = None
    alerts: Optional[List[Dict[str, Any]]] = None


# ============================================================================
# Batch Processing
# ============================================================================


class BatchEntityRequest(BaseModel):
    """Single entity in batch request."""

    entity_id: str
    entity_type: str = "customer"
    signals: List[RiskSignal]


class BatchRiskRequest(BaseModel):
    """Request for batch risk aggregation."""

    entities: List[BatchEntityRequest]
    weights: Optional[Dict[str, float]] = None
    parallel: bool = Field(
        default=True, description="Process entities in parallel"
    )


class BatchEntityResult(BaseModel):
    """Result for a single entity in batch."""

    entity_id: str
    entity_type: str
    risk_score: float
    risk_level: RiskLevel
    success: bool
    error: Optional[str] = None


class BatchRiskResponse(BaseModel):
    """Response for batch risk aggregation."""

    total_entities: int
    successful: int
    failed: int
    results: List[BatchEntityResult]
    average_risk_score: float
    processing_time_seconds: float
    processed_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Aggregation Jobs
# ============================================================================


class AggregationJobRequest(BaseModel):
    """Request to create an aggregation job."""

    job_name: str
    entity_ids: List[str]
    entity_type: str = "customer"
    include_sources: List[str] = Field(
        default=["kyc", "transaction", "credit", "loan", "repayment"]
    )
    weights: Optional[Dict[str, float]] = None
    notification_webhook: Optional[str] = None


class AggregationJobResponse(BaseModel):
    """Response for aggregation job."""

    job_id: str
    job_name: str
    status: JobStatus
    total_entities: int
    processed_entities: int = 0
    successful: int = 0
    failed: int = 0
    progress_percentage: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results_url: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# Data Source Models
# ============================================================================


class KYCData(BaseModel):
    """KYC data model."""

    customer_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    id_verified: bool = False
    document_score: float = Field(default=0.0, ge=0.0, le=1.0)
    risk_score: Optional[float] = None


class TransactionData(BaseModel):
    """Transaction data model."""

    transaction_id: str
    customer_id: str
    amount: float
    currency: str = "USD"
    transaction_type: str
    timestamp: datetime
    risk_score: Optional[float] = None


class CreditData(BaseModel):
    """Credit data model."""

    customer_id: str
    credit_score: int = Field(..., ge=300, le=850)
    outstanding_balance: float
    payment_history: str
    risk_score: Optional[float] = None


class LoanData(BaseModel):
    """Loan data model."""

    loan_id: str
    customer_id: str
    amount: float
    status: str
    interest_rate: float
    risk_score: Optional[float] = None


class RepaymentData(BaseModel):
    """Repayment data model."""

    repayment_id: str
    loan_id: str
    customer_id: str
    amount: float
    due_date: datetime
    paid_date: Optional[datetime] = None
    status: str
    risk_score: Optional[float] = None

