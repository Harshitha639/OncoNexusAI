"""Application-specific exception hierarchy.

All custom exceptions inherit from `AppException` so the global exception
handler can catch a single base type and format a consistent response.
"""

from http import HTTPStatus


class AppException(Exception):
    """Base class for all predictable, handled application errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        code: str = "app_error",
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found.", code: str = "not_found") -> None:
        super().__init__(message=message, code=code, status_code=HTTPStatus.NOT_FOUND)


class BadRequestException(AppException):
    def __init__(self, message: str = "Invalid request.", code: str = "bad_request") -> None:
        super().__init__(message=message, code=code, status_code=HTTPStatus.BAD_REQUEST)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required.", code: str = "unauthorized") -> None:
        super().__init__(message=message, code=code, status_code=HTTPStatus.UNAUTHORIZED)


class ForbiddenException(AppException):
    def __init__(self, message: str = "You do not have access to this resource.", code: str = "forbidden") -> None:
        super().__init__(message=message, code=code, status_code=HTTPStatus.FORBIDDEN)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource conflict.", code: str = "conflict") -> None:
        super().__init__(message=message, code=code, status_code=HTTPStatus.CONFLICT)


class ServiceUnavailableException(AppException):
    def __init__(self, message: str = "Service temporarily unavailable.", code: str = "service_unavailable") -> None:
        super().__init__(message=message, code=code, status_code=HTTPStatus.SERVICE_UNAVAILABLE)
