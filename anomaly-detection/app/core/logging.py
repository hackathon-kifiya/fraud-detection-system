"""
Logging Configuration
"""
import logging
import sys

from pythonjsonlogger import jsonlogger

from app.core.config import settings


def setup_logging():
    """Setup application logging"""

    # Create logger
    logger = logging.getLogger("anomaly_detection")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))

    # JSON formatter for structured logging
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    # Add handler
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str):
    """Get a logger instance"""
    return logging.getLogger(f"anomaly_detection.{name}")


setup_logging()
logger = logging.getLogger("anomaly_detection")
