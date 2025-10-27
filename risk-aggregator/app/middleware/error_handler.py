"""
Error handling middleware.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import setup_logging

logger = setup_logging()


def add_exception_handlers(app: FastAPI):
    """
    Add exception handlers to FastAPI application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        logger.warning(
            f"HTTP error: {exc.status_code} - {exc.detail} - "
            f"Path: {request.url.path}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "status_code": exc.status_code,
                    "message": exc.detail,
                    "path": str(request.url.path),
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle request validation errors."""
        logger.warning(
            f"Validation error: {exc.errors()} - Path: {request.url.path}"
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "status_code": 422,
                    "message": "Validation error",
                    "details": exc.errors(),
                    "path": str(request.url.path),
                }
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(
            f"Unhandled exception: {str(exc)} - Path: {request.url.path}",
            exc_info=True,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "status_code": 500,
                    "message": "Internal server error",
                    "detail": str(exc) if logger.level <= 10 else "An error occurred",
                    "path": str(request.url.path),
                }
            },
        )

