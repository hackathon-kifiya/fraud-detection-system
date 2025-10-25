"""
KYC Service
Handles KYC data operations with security features like data masking
"""
from typing import Dict, Any, Optional
from app.core.security import DataMasker, AuditLogger, InputSanitizer
from app.core.logging import get_logger

logger = get_logger(__name__)


class KYCService:
    """Service for handling KYC operations with security features"""

    def __init__(self):
        self.data_masker = DataMasker()

    def mask_kyc_data(self, kyc_data: Dict[str, Any], mask_level: str = "partial") -> Dict[str, Any]:
        """
        Mask sensitive KYC data based on masking level

        Args:
            kyc_data: Raw KYC data dictionary
            mask_level: Masking level - "full", "partial", or "none"

        Returns:
            Dict with masked sensitive fields
        """
        masked_data = kyc_data.copy()

        if mask_level == "none":
            return masked_data

        # Mask phone number
        if "phone_number" in masked_data and masked_data["phone_number"]:
            masked_data["phone_number"] = self.data_masker.mask_phone(
                str(masked_data["phone_number"])
            )

        # Mask email
        if "email" in masked_data and masked_data["email"]:
            masked_data["email"] = self.data_masker.mask_email(
                masked_data["email"]
            )

        # Mask account number
        if "account_number" in masked_data and masked_data["account_number"]:
            masked_data["account_number"] = self.data_masker.mask_account(
                str(masked_data["account_number"])
            )

        # Mask TIN (Tax Identification Number)
        if "tin_number" in masked_data and masked_data["tin_number"]:
            masked_data["tin_number"] = self.data_masker.mask_tin(
                str(masked_data["tin_number"])
            )

        # For full masking, also mask additional fields
        if mask_level == "full":
            # Mask address partially
            if "address" in masked_data and masked_data["address"]:
                address = masked_data["address"]
                if len(address) > 10:
                    masked_data["address"] = f"{address[:5]}...{address[-3:]}"
                else:
                    masked_data["address"] = "***"

            # Mask date of birth (keep year, mask day/month)
            if "date_of_birth" in masked_data and masked_data["date_of_birth"]:
                dob = str(masked_data["date_of_birth"])
                # If format is YYYY-MM-DD, mask to YYYY-**-**
                if "-" in dob:
                    parts = dob.split("-")
                    masked_data["date_of_birth"] = f"{parts[0]}-**-**"

        logger.debug(f"Masked KYC data with level: {mask_level}")
        return masked_data

    def sanitize_kyc_input(self, kyc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize KYC input data

        Args:
            kyc_data: Raw input data

        Returns:
            Sanitized data
        """
        sanitized = {}

        # Sanitize string fields
        string_fields = ["first_name", "last_name", "email", "address", "business_name"]
        for field in string_fields:
            if field in kyc_data and kyc_data[field]:
                sanitized[field] = InputSanitizer.sanitize_string(
                    str(kyc_data[field]),
                    max_length=200
                )

        # Sanitize numeric fields
        numeric_fields = ["phone_number", "account_number", "tin_number", "annual_income"]
        for field in numeric_fields:
            if field in kyc_data and kyc_data[field]:
                if isinstance(kyc_data[field], (int, float)):
                    sanitized[field] = kyc_data[field]
                else:
                    sanitized[field] = InputSanitizer.sanitize_numeric(
                        str(kyc_data[field])
                    )

        # Copy other fields as-is
        for field, value in kyc_data.items():
            if field not in sanitized:
                sanitized[field] = value

        return sanitized

    def validate_kyc_data(self, kyc_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
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

    def log_kyc_access(self, user_id: str, customer_id: str, action: str):
        """
        Log KYC data access for audit trail

        Args:
            user_id: ID of user accessing data
            customer_id: ID of customer whose data is accessed
            action: Action performed (view, update, delete, etc.)
        """
        AuditLogger.log_data_access(
            user_id=user_id,
            resource=f"kyc_data/{customer_id}",
            action=action
        )
        logger.info(f"KYC access logged: user={user_id}, customer={customer_id}, action={action}")




