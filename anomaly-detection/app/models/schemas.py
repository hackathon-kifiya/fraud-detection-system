"""
Pydantic Schemas for Request/Response Models
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

# ==================== Enums ====================


class TransactionType(str, Enum):
    PURCHASE = "purchase"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    DEPOSIT = "deposit"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class MaritalStatusOptions(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class EducationalLevelOptions(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    POST_GRADUATE = "post_graduate"


class Region(str, Enum):
    ADDIS_ABABA = "ADDIS_ABABA"
    AFAR = "AFAR"
    TIGRAY = "TIGRAY"
    AMHARA = "AMHARA"
    BENISHANGUL_GUMUZ = "BENISHANGUL_GUMUZ"
    GAMBELA = "GAMBELA"
    OROMIA = "OROMIA"
    SIDAMA = "SIDAMA"
    SOMALI = "SOMALI"
    SNNP = "SNNP"
    HARAR = "HARAR"
    DIRE_DAWA = "DIRE_DAWA"
    SWEP = "SWEP"


class City(str, Enum):
    ADDIS_ABABA = "ADDIS_ABABA"
    BAHIR_DAR = "BAHIR_DAR"
    DERBA = "DERBA"
    GONDAR = "GONDAR"
    HARRAR = "HARRAR"
    JIMMA = "JIMMA"
    LALIBELA = "LALIBELA"
    MEKELLE = "MEKELLE"


class ZoneOrSubCity(str, Enum):
    ZONE_1 = "ZONE_1"
    ZONE_2 = "ZONE_2"
    ZONE_3 = "ZONE_3"
    ZONE_4 = "ZONE_4"
    ZONE_5 = "ZONE_5"
    ZONE_6 = "ZONE_6"
    ZONE_7 = "ZONE_7"
    ZONE_8 = "ZONE_8"
    ZONE_9 = "ZONE_9"
    ZONE_10 = "ZONE_10"
    ZONE_11 = "ZONE_11"
    BOLE = "BOLE"
    ARADA = "ARADA"
    GULELE = "GULELE"
    ZONE_12 = "ZONE_12"
    ZONE_13 = "ZONE_13"


class SourceOfInitialCapital(str, Enum):
    FAMILY = "FAMILY"
    OWN = "OWN"
    LOAN = "LOAN"
    FUND = "FUND"
    OTHER = "OTHER"


class AssociationType(str, Enum):
    SOLE_PROPRIETORSHIP = "SOLE_PROPRIETORSHIP"
    PARTNERSHIP = "PARTNERSHIP"
    CORPORATION = "CORPORATION"
    OTHER = "OTHER"


class BusinessSector(str, Enum):
    AGRICULTURE = "AGRICULTURE"
    MANUFACTURING = "MANUFACTURING"
    DOMESTIC_TRADE_SERVICES = "DOMESTIC_TRADE_SERVICES"
    SERVICES = "SERVICES"
    OTHER = "OTHER"


class BusinessLevel(str, Enum):
    GROWING = "GROWING"
    STARTUP = "STARTUP"


# ==================== Request Schemas ====================


class KYCData(BaseModel):
    """KYC customer data schema"""

    customer_id: str = Field(..., min_length=1, max_length=100)
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_phone_number: int = Field(
        ..., ge=1000000000, le=9999999999, description="Customer phone number"
    )
    customer_age: int = Field(..., ge=18, le=120, description="Customer age")
    customer_gender: Gender = Field(..., description="Customer gender")
    customer_marital_status: MaritalStatusOptions = Field(
        ..., description="Customer marital status"
    )
    customer_education_level: EducationalLevelOptions = Field(
        ..., description="Customer education level"
    )
    customer_tin_number: str = Field(
        ..., min_length=1, max_length=100, description="Customer TIN number"
    )
    customer_bank_account_number: str = Field(
        ..., min_length=1, max_length=100, description="Customer bank account number"
    )
    customer_region: Region = Field(..., description="Customer region")
    customer_city: City = Field(..., description="Customer city")
    customer_zone_or_sub_city: ZoneOrSubCity = Field(
        ..., description="Customer zone or sub city"
    )
    customer_woreda: int = Field(description="Customer woreda")
    customerId: str = Field(
        ..., min_length=1, max_length=100, description="Customer ID"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CUST_12345",
                "customer_name": "John Doe",
                "customer_phone_number": 9123456789,
                "customer_age": 35,
                "customer_gender": "male",
                "customer_marital_status": "single",
                "customer_education_level": "primary",
                "customer_tin_number": "1234567890",
                "customer_bank_account_number": "1234567890",
                "customer_region": "ADDIS_ABABA",
                "customer_city": "ADDIS_ABABA",
                "customer_zone_or_sub_city": "ZONE_1",
                "customer_woreda": "01",
                "customerId": "CUST_12345",
            }
        }


class BusinessInformation(BaseModel):
    """Business information schema"""

    business_id: str = Field(..., min_length=1, max_length=100)
    business_name: str = Field(..., min_length=1, max_length=100)
    business_tin_number: str = Field(
        ..., min_length=1, max_length=100, description="Business TIN number"
    )
    business_city: City = Field(..., description="Business city")
    business_zone_or_sub_city: ZoneOrSubCity = Field(
        ..., description="Business zone or sub city"
    )
    business_woreda: str = Field(
        ..., min_length=1, max_length=100, description="Business woreda"
    )
    business_establishment_year: int = Field(
        ..., ge=1900, le=2025, description="Business establishment year"
    )
    business_sector: BusinessSector = Field(..., description="Business sector")
    business_level: BusinessLevel = Field(..., description="Business level")
    business_starting_capital: float = Field(
        ..., ge=0, description="Business starting capital"
    )
    business_current_capital: float = Field(
        ..., ge=0, description="Business current capital"
    )
    business_annual_profit: float = Field(
        ..., ge=0, description="Business annual profit"
    )
    business_annual_sales: float = Field(..., ge=0, description="Business annual sales")
    business_current_no_of_employees: int = Field(
        ..., ge=0, description="Business current number of employees"
    )
    business_starting_no_of_employees: int = Field(
        ..., ge=0, description="Business starting number of employees"
    )
    business_source_of_initial_capital: SourceOfInitialCapital = Field(
        ..., description="Business source of initial capital"
    )
    business_association_type: AssociationType = Field(
        ..., description="Business association type"
    )
    customer_id: str = Field(..., min_length=1, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "business_id": "BUS_12345",
                "business_name": "Business Name",
                "business_tin_number": "1234567890",
                "business_city": "ADDIS_ABABA",
                "business_zone_or_sub_city": "ZONE_1",
                "business_woreda": "01",
                "business_establishment_year": 2020,
                "business_sector": "AGRICULTURE",
                "business_level": "GROWING",
                "business_starting_capital": 100000.0,
                "business_current_capital": 100000.0,
                "business_annual_profit": 100000.0,
                "business_annual_sales": 100000.0,
                "business_current_no_of_employees": 10,
                "business_starting_no_of_employees": 10,
                "business_source_of_initial_capital": "FAMILY",
                "business_association_type": "SOLE_PROPRIETORSHIP",
                "customer_id": "CUST_12345",
                "businessId": "BUS_12345",
            }
        }


class TransactionData(BaseModel):
    """Transaction data schema - matches training data structure"""

    customer_id: str = Field(..., min_length=1, max_length=100)
    date: str = Field(..., description="Transaction date in ISO format")
    credit: Optional[float] = 0.0
    debit: Optional[float] = 0.0
    closingBalance: Optional[float] = 0.0
    narrative: str = Field(
        ..., min_length=1, max_length=200, description="Transaction narrative"
    )
    source: str = Field(
        ..., min_length=1, max_length=50, description="Transaction source"
    )
    is_anomaly: Optional[int] = Field(
        None, ge=0, le=1, description="Anomaly flag (0=normal, 1=anomaly)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CUST_12345",
                "date": "2024-10-25T14:30:00",
                "credit": 1000.0,
                "debit": 0.0,
                "closingBalance": 5000.0,
                "narrative": "Cash Deposit BY SELF",
                "source": "CASH DEPOSIT",
                "is_anomaly": 0,
            }
        }


class BatchKYCRequest(BaseModel):
    """Batch KYC request schema"""

    records: List[KYCData] = Field(..., min_items=1, max_items=100)


class BatchTransactionRequest(BaseModel):
    """Batch transaction request schema"""

    transactions: List[TransactionData] = Field(..., min_items=1, max_items=100)


class CustomerBatchTransactionRequest(BaseModel):
    """Customer-based batch transaction request schema"""

    customer_id: str = Field(
        ..., min_length=1, max_length=100, description="Customer ID to process"
    )
    transactions: List[TransactionData] = Field(
        ...,
        min_items=1,
        max_items=1000,
        description="All transactions for this customer",
    )


class CombinedKYCBusinessData(BaseModel):
    """Combined KYC and Business data schema"""

    # KYC fields
    customer_id: str = Field(..., min_length=1, max_length=100)
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_phone_number: int = Field(
        ..., ge=1000000000, le=9999999999, description="Customer phone number"
    )
    customer_age: int = Field(..., ge=18, le=120, description="Customer age")
    customer_gender: Gender = Field(..., description="Customer gender")
    customer_marital_status: MaritalStatusOptions = Field(
        ..., description="Customer marital status"
    )
    customer_education_level: EducationalLevelOptions = Field(
        ..., description="Customer education level"
    )
    customer_tin_number: str = Field(
        ..., min_length=1, max_length=100, description="Customer TIN number"
    )
    customer_bank_account_number: str = Field(
        ..., min_length=1, max_length=100, description="Customer bank account number"
    )
    customer_region: Region = Field(..., description="Customer region")
    customer_city: City = Field(..., description="Customer city")
    customer_zone_or_sub_city: ZoneOrSubCity = Field(
        ..., description="Customer zone or sub city"
    )
    customer_woreda: int = Field(..., description="Customer woreda")
    customerId: str = Field(
        ..., min_length=1, max_length=100, description="Customer ID"
    )

    # Business fields
    business_id: str = Field(..., min_length=1, max_length=100)
    business_name: str = Field(..., min_length=1, max_length=100)
    business_tin_number: str = Field(
        ..., min_length=1, max_length=100, description="Business TIN number"
    )
    business_city: City = Field(..., description="Business city")
    business_zone_or_sub_city: ZoneOrSubCity = Field(
        ..., description="Business zone or sub city"
    )
    business_woreda: str = Field(
        ..., min_length=1, max_length=100, description="Business woreda"
    )
    business_establishment_year: int = Field(
        ..., ge=1900, le=2025, description="Business establishment year"
    )
    business_sector: BusinessSector = Field(..., description="Business sector")
    business_level: BusinessLevel = Field(..., description="Business level")
    business_starting_capital: float = Field(
        ..., ge=0, description="Business starting capital"
    )
    business_current_capital: float = Field(
        ..., ge=0, description="Business current capital"
    )
    business_annual_profit: float = Field(
        ..., ge=0, description="Business annual profit"
    )
    business_annual_sales: float = Field(..., ge=0, description="Business annual sales")
    business_current_no_of_employees: int = Field(
        ..., ge=0, description="Business current number of employees"
    )
    business_starting_no_of_employees: int = Field(
        ..., ge=0, description="Business starting number of employees"
    )
    business_source_of_initial_capital: SourceOfInitialCapital = Field(
        ..., description="Business source of initial capital"
    )
    business_association_type: AssociationType = Field(
        ..., description="Business association type"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CUST_12345",
                "customer_name": "John Doe",
                "customer_phone_number": 9123456789,
                "customer_age": 35,
                "customer_gender": "male",
                "customer_marital_status": "single",
                "customer_education_level": "primary",
                "customer_tin_number": "1234567890",
                "customer_bank_account_number": "1234567890",
                "customer_region": "ADDIS_ABABA",
                "customer_city": "ADDIS_ABABA",
                "customer_zone_or_sub_city": "ZONE_1",
                "customer_woreda": 1,
                "customerId": "CUST_12345",
                "business_id": "BUS_12345",
                "business_name": "John's Business",
                "business_tin_number": "9876543210",
                "business_city": "ADDIS_ABABA",
                "business_zone_or_sub_city": "ZONE_1",
                "business_woreda": "01",
                "business_establishment_year": 2020,
                "business_sector": "AGRICULTURE",
                "business_level": "GROWING",
                "business_starting_capital": 100000.0,
                "business_current_capital": 150000.0,
                "business_annual_profit": 25000.0,
                "business_annual_sales": 200000.0,
                "business_current_no_of_employees": 5,
                "business_starting_no_of_employees": 2,
                "business_source_of_initial_capital": "FAMILY",
                "business_association_type": "SOLE_PROPRIETORSHIP",
            }
        }


class BatchCombinedRequest(BaseModel):
    """Batch combined KYC+Business request schema"""

    records: List[CombinedKYCBusinessData] = Field(..., min_items=1, max_items=100)


# ==================== Response Schemas ====================


class ShapExplanation(BaseModel):
    """SHAP explanation details"""

    top_contributing_features: Dict[str, float]
    feature_values: Dict[str, float]
    shap_values: Dict[str, float]


class AnomalyResponse(BaseModel):
    """Anomaly detection response"""

    is_anomaly: bool = Field(..., description="Whether the record is anomalous")
    anomaly_score: float = Field(
        ..., description="Anomaly score (lower is more anomalous)"
    )
    risk_level: RiskLevel = Field(..., description="Risk level classification")
    explanation: ShapExplanation = Field(..., description="SHAP explanation")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class BatchCombinedResult(BaseModel):
    """Single combined result in batch"""

    customer_id: str
    business_id: str
    result: Optional[AnomalyResponse] = None
    error: Optional[str] = None


class BatchCombinedResponse(BaseModel):
    """Batch combined response"""

    batch_results: List[BatchCombinedResult]
    total_processed: int
    total_anomalies: int
    processing_time_seconds: float


class BatchKYCResult(BaseModel):
    """Single KYC result in batch"""

    customer_id: str
    result: Optional[AnomalyResponse] = None
    error: Optional[str] = None


class BatchTransactionResult(BaseModel):
    """Single transaction result in batch"""

    customer_id: str
    result: Optional[AnomalyResponse] = None
    error: Optional[str] = None


class BatchKYCResponse(BaseModel):
    """Batch KYC response"""

    batch_results: List[BatchKYCResult]
    total_processed: int
    total_anomalies: int
    processing_time_seconds: float


class BatchTransactionResponse(BaseModel):
    """Batch transaction response"""

    batch_results: List[BatchTransactionResult]
    total_processed: int
    total_anomalies: int
    processing_time_seconds: float


class CustomerBatchTransactionResult(BaseModel):
    """Single customer batch result"""

    customer_id: str
    total_transactions: int
    anomaly_count: int
    customer_risk_level: RiskLevel
    customer_anomaly_score: float
    transaction_results: List[BatchTransactionResult]
    customer_flagged: bool = Field(
        ..., description="Whether the customer is flagged as fraudulent"
    )


class CustomerBatchTransactionResponse(BaseModel):
    """Customer batch transaction response"""

    customer_id: str
    total_transactions: int
    anomaly_count: int
    customer_risk_level: RiskLevel
    customer_anomaly_score: float
    customer_flagged: bool
    transaction_results: List[BatchTransactionResult]
    processing_time_seconds: float


class ErrorResponse(BaseModel):
    """Error response schema"""

    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
