"""
Helper utility functions.
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List


def calculate_hash(data: Any) -> str:
    """
    Calculate SHA256 hash of data.

    Args:
        data: Data to hash

    Returns:
        str: Hexadecimal hash string
    """
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    elif not isinstance(data, str):
        data = str(data)

    return hashlib.sha256(data.encode()).hexdigest()


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize weights to sum to 1.0.

    Args:
        weights: Dictionary of weights

    Returns:
        Dict[str, float]: Normalized weights
    """
    total = sum(weights.values())
    if total == 0:
        return weights

    return {k: v / total for k, v in weights.items()}


def calculate_weighted_average(
    values: List[float], weights: List[float]
) -> float:
    """
    Calculate weighted average.

    Args:
        values: List of values
        weights: List of weights

    Returns:
        float: Weighted average
    """
    if not values or not weights or len(values) != len(weights):
        return 0.0

    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(v * w for v, w in zip(values, weights))
    return weighted_sum / total_weight


def format_timestamp(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime as string.

    Args:
        dt: Datetime object
        fmt: Format string

    Returns:
        str: Formatted datetime string
    """
    return dt.strftime(fmt)


def parse_timestamp(timestamp_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse timestamp string to datetime.

    Args:
        timestamp_str: Timestamp string
        fmt: Format string

    Returns:
        datetime: Parsed datetime object
    """
    return datetime.strptime(timestamp_str, fmt)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero

    Returns:
        float: Division result or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp value between min and max.

    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value

    Returns:
        float: Clamped value
    """
    return max(min_value, min(value, max_value))


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Dict: Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks.

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List[List]: List of chunks
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]

