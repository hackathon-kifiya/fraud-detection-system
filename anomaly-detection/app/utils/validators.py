"""
Validation Utilities
Input validation and data verification functions
"""
from typing import Any, Dict, Optional, Tuple

from app.core.logging import get_logger
from app.core.security import InputSanitizer

logger = get_logger(__name__)


def validate_kyc_data(kyc_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate KYC data

    Args:
        kyc_data: KYC data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate customer ID
    if "customer_id" in kyc_data:
        if not InputSanitizer.validate_customer_id(kyc_data["customer_id"]):
            return False, "Invalid customer_id format"

    # Validate required fields
    required_fields = ["customer_id", "first_name", "last_name"]
    for field in required_fields:
        if field not in kyc_data or not kyc_data[field]:
            return False, f"Missing required field: {field}"

    # Validate email format (basic check)
    if "email" in kyc_data and kyc_data["email"]:
        email = kyc_data["email"]
        if "@" not in email or "." not in email:
            return False, "Invalid email format"

    return True, None


def validate_transaction_data(
    transaction_data: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """
    Validate transaction data

    Args:
        transaction_data: Transaction data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate required fields
    required_fields = ["customer_id", "date", "narrative", "source"]
    for field in required_fields:
        if field not in transaction_data or transaction_data[field] is None:
            return False, f"Missing required field: {field}"

    # Validate customer ID
    if not InputSanitizer.validate_customer_id(transaction_data["customer_id"]):
        return False, "Invalid customer_id format"

    # Validate numeric fields are non-negative if present
    numeric_fields = ["credit", "debit", "closingBalance"]
    for field in numeric_fields:
        if field in transaction_data and transaction_data[field] is not None:
            if transaction_data[field] < 0:
                return False, f"Field {field} must be non-negative"

    return True, None


def validate_business_data(business_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate business data

    Args:
        business_data: Business data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate required fields
    required_fields = ["business_id", "business_name", "customer_id"]
    for field in required_fields:
        if field not in business_data or not business_data[field]:
            return False, f"Missing required field: {field}"

    # Validate year ranges
    if "business_establishment_year" in business_data:
        year = business_data["business_establishment_year"]
        if year < 1900 or year > 2025:
            return False, "Invalid business establishment year"

    # Validate non-negative financial fields
    financial_fields = [
        "business_starting_capital",
        "business_current_capital",
        "business_annual_profit",
        "business_annual_sales",
    ]
    for field in financial_fields:
        if field in business_data and business_data[field] is not None:
            if business_data[field] < 0:
                return False, f"Field {field} must be non-negative"

    # Validate non-negative employee counts
    employee_fields = [
        "business_current_no_of_employees",
        "business_starting_no_of_employees",
    ]
    for field in employee_fields:
        if field in business_data and business_data[field] is not None:
            if business_data[field] < 0:
                return False, f"Field {field} must be non-negative"

    return True, None
