"""
Validation utility functions.
"""

import re
from typing import Any, Dict, List


def validate_risk_score(score: float) -> bool:
    """
    Validate risk score is between 0 and 1.

    Args:
        score: Risk score

    Returns:
        bool: True if valid
    """
    return 0.0 <= score <= 1.0


def validate_confidence(confidence: float) -> bool:
    """
    Validate confidence score is between 0 and 1.

    Args:
        confidence: Confidence score

    Returns:
        bool: True if valid
    """
    return 0.0 <= confidence <= 1.0


def validate_weights(weights: Dict[str, float]) -> tuple[bool, str]:
    """
    Validate risk weights.

    Args:
        weights: Dictionary of weights

    Returns:
        tuple: (is_valid, error_message)
    """
    if not weights:
        return False, "Weights cannot be empty"

    # Check all values are non-negative
    for key, value in weights.items():
        if not isinstance(value, (int, float)):
            return False, f"Weight for {key} must be a number"
        if value < 0:
            return False, f"Weight for {key} cannot be negative"

    # Check sum is positive
    if sum(weights.values()) <= 0:
        return False, "Total weight must be positive"

    return True, ""


def validate_entity_id(entity_id: str) -> bool:
    """
    Validate entity ID format.

    Args:
        entity_id: Entity identifier

    Returns:
        bool: True if valid
    """
    if not entity_id or not isinstance(entity_id, str):
        return False

    # Check length
    if len(entity_id) < 1 or len(entity_id) > 255:
        return False

    # Allow alphanumeric, hyphens, and underscores
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, entity_id))


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address

    Returns:
        bool: True if valid
    """
    if not email or not isinstance(email, str):
        return False

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number

    Returns:
        bool: True if valid
    """
    if not phone or not isinstance(phone, str):
        return False

    # Remove common formatting characters
    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)

    # Check if it's all digits and reasonable length
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15


def validate_date_range(start_date: Any, end_date: Any) -> bool:
    """
    Validate that start date is before end date.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        bool: True if valid
    """
    try:
        return start_date < end_date
    except Exception:
        return False


def validate_positive_number(value: float) -> bool:
    """
    Validate that a number is positive.

    Args:
        value: Number to validate

    Returns:
        bool: True if positive
    """
    return isinstance(value, (int, float)) and value > 0


def validate_non_negative_number(value: float) -> bool:
    """
    Validate that a number is non-negative.

    Args:
        value: Number to validate

    Returns:
        bool: True if non-negative
    """
    return isinstance(value, (int, float)) and value >= 0

