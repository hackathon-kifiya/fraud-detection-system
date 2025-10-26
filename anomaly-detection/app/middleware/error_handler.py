"""
Error Handler Middleware
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import logger
from app.models.schemas import ErrorResponse


def add_error_handlers(app: FastAPI):
    """Add error handlers to FastAPI app"""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.warning(
            "HTTP exception: %s - %s",
            exc.status_code,
            exc.detail,
            extra={"path": request.url.path, "method": request.method}
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=f"HTTP {exc.status_code}",
                detail=str(exc.detail)
            ).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors"""
        logger.warning(
            "Validation error: %s",
            exc.errors(),
            extra={"path": request.url.path, "method": request.method}
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error="Validation Error",
                detail=str(exc.errors())
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(
            "Unhandled exception: %s",
            str(exc),
            exc_info=True,
            extra={"path": request.url.path, "method": request.method}
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="Internal Server Error",
                detail="An unexpected error occurred. Please contact support."
            ).model_dump()
        )
