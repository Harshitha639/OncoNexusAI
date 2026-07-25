"""
Global exception handlers, registered once on the FastAPI app instance.

Guarantees every error response — expected or not — follows the
`ErrorResponse` contract defined in `app.common.responses`.
"""

from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.responses import ErrorDetail, ErrorResponse
from app.core.logging import get_logger
from app.exceptions.base import AppException

logger = get_logger(__name__)


def _json_error(status_code: int, message: str, errors: list[ErrorDetail] | None = None) -> JSONResponse:
    body = ErrorResponse(message=message, errors=errors or [])
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning("Handled AppException: %s (%s)", exc.message, exc.code)
        return _json_error(
            status_code=exc.status_code,
            message=exc.message,
            errors=[ErrorDetail(code=exc.code, message=exc.message)],
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            ErrorDetail(
                code="validation_error",
                message=err.get("msg", "Invalid value."),
                field=".".join(str(loc) for loc in err.get("loc", [])),
            )
            for err in exc.errors()
        ]
        return _json_error(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Request validation failed.",
            errors=errors,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _json_error(status_code=exc.status_code, message=str(exc.detail))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return _json_error(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred. Please try again later.",
        )
