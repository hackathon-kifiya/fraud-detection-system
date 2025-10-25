"""
Error Handler Middleware
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.models.schemas import ErrorResponse

logger = get_logger(__name__)


def add_error_handlers(app: FastAPI):
    """Add error handlers to FastAPI app"""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.warning(
            f"HTTP exception: {exc.status_code} - {exc.detail}",
            extra={"path": request.url.path, "method": request.method},
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=f"HTTP {exc.status_code}", detail=str(exc.detail)
            ).model_dump(mode="json"),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle validation errors"""
        logger.warning(
            f"Validation error: {exc.errors()}",
            extra={"path": request.url.path, "method": request.method},
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error="Validation Error", detail=str(exc.errors())
            ).model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(
            f"Unhandled exception: {str(exc)}",
            exc_info=True,
            extra={"path": request.url.path, "method": request.method},
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal Server Error",
                detail="An unexpected error occurred. Please contact support.",
            ).model_dump(mode="json"),
        )
