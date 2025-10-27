"""
API Dependencies
Shared dependency functions for API endpoints
"""
from fastapi import HTTPException, Request, status

from app.services.unsupervised_anomaly_detector import UnsupervisedAnomalyDetectorService
from app.services.supervised_anomaly_detector import SupervisedAnomalyDetectorService


def get_unsupervised_anomaly_detector_service(request: Request) -> UnsupervisedAnomalyDetectorService:
    """
    Dependency to get unsupervised anomaly service from app state

    Args:
        request: FastAPI request object

    Returns:
        UnsupervisedAnomalyDetectorService instance from app state
        
    Raises:
        HTTPException: If service is not initialized
    """
    service = request.app.state.unsupervised_anomaly_service
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unsupervised anomaly detection service is not available. Please ensure models are loaded."
        )
    return service


def get_supervised_anomaly_service(request: Request) -> SupervisedAnomalyDetectorService:
    """
    Dependency to get supervised anomaly service from app state

    Args:
        request: FastAPI request object

    Returns:
        SupervisedAnomalyDetectorService instance from app state
        
    Raises:
        HTTPException: If service is not initialized
    """
    service = request.app.state.supervised_anomaly_service
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supervised anomaly detection service is not available. Please ensure models are loaded."
        )
    return service


# Aliases for backward compatibility
def get_anomaly_service(request: Request) -> UnsupervisedAnomalyDetectorService:
    """Alias for get_unsupervised_anomaly_detector_service"""
    return get_unsupervised_anomaly_detector_service(request)