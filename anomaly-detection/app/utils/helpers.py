"""
Helper Utilities
General utility functions for data generation and other helpers
"""
import numpy as np

from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_synthetic_kyc_data(n_samples: int) -> np.ndarray:
    """
    Generate synthetic KYC data for training

    Args:
        n_samples: Number of samples to generate

    Returns:
        numpy array of synthetic KYC data
    """
    data = np.random.randn(n_samples, 7)

    # Transform to realistic ranges
    data[:, 0] = data[:, 0] * 15 + 45  # age: ~45 ± 15
    data[:, 1] = np.abs(data[:, 1]) * 30000 + 50000  # income: 50k-110k
    data[:, 2] = data[:, 2] * 100 + 650  # credit score: ~650 ± 100
    data[:, 3] = np.abs(data[:, 3] * 2 + 2)  # num_accounts: ~2-4
    data[:, 4] = np.abs(data[:, 4] * 500 + 1000)  # account_age_days: ~1000-2000
    data[:, 5] = np.abs(data[:, 5] * 10 + 20)  # transactions: ~20 ± 10
    data[:, 6] = np.abs(data[:, 6] * 100 + 150)  # avg_amount: ~150 ± 100

    return data


def generate_synthetic_transaction_data(n_samples: int) -> np.ndarray:
    """
    Generate synthetic transaction data for training

    Args:
        n_samples: Number of samples to generate

    Returns:
        numpy array of synthetic transaction data
    """
    data = np.random.randn(n_samples, 8)

    # Transform to realistic ranges
    data[:, 0] = np.abs(data[:, 0]) * 200 + 100  # amount: 100-500
    data[:, 1] = np.random.randint(0, 4, n_samples)  # transaction_type: 0-3
    data[:, 2] = np.random.randint(0, 24, n_samples)  # hour: 0-23
    data[:, 3] = np.random.randint(0, 7, n_samples)  # day: 0-6
    data[:, 4] = np.abs(data[:, 4] * 5 + 10)  # distance: ~10 ± 5 km
    data[:, 5] = np.random.randint(0, 2, n_samples)  # is_online: 0-1
    data[:, 6] = np.abs(data[:, 6] * 2 + 3)  # transactions_24h: ~3 ± 2
    data[:, 7] = np.abs(data[:, 7] * 100 + 150)  # avg_amount: ~150 ± 100

    return data
