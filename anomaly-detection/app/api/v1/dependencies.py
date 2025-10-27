"""
API Dependencies
Shared dependency functions for API endpoints
"""
from fastapi import Request

from app.services.unsupervised_anomaly_detector import UnsupervisedAnomalyDetectorService
from app.services.supervised_anomaly_detector import SupervisedAnomalyDetectorService


def get_unsupervised_anomaly_detector_service(request: Request) -> UnsupervisedAnomalyDetectorService:
    """
    Dependency to get unsupervised anomaly service from app state

    Args:
        request: FastAPI request object

    Returns:
        UnsupervisedAnomalyDetectorService instance from app state
    """
    return request.app.state.unsupervised_anomaly_service


def get_supervised_anomaly_service(request: Request) -> SupervisedAnomalyDetectorService:
    """
    Dependency to get supervised anomaly service from app state

    Args:
        request: FastAPI request object

    Returns:
        SupervisedAnomalyDetectorService instance from app state
    """
    return request.app.state.supervised_anomaly_service


# Aliases for backward compatibility
def get_anomaly_service(request: Request) -> UnsupervisedAnomalyDetectorService:
    """Alias for get_unsupervised_anomaly_detector_service"""
    return get_unsupervised_anomaly_detector_service(request)
