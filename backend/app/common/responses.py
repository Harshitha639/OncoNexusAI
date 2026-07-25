"""
Standardized API response envelopes.

Every endpoint should return responses shaped by these models so that
frontend clients can rely on a single, predictable contract.
"""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from app.common.constants import ResponseStatus

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Generic success envelope wrapping any payload type `T`."""

    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str = "Request completed successfully."
    data: Optional[T] = None


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(BaseResponse[T], Generic[T]):
    """Success envelope for paginated list endpoints."""

    meta: PaginationMeta


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    field: Optional[str] = Field(default=None, description="Offending field, if applicable")


class ErrorResponse(BaseModel):
    status: ResponseStatus = ResponseStatus.ERROR
    message: str
    errors: list[ErrorDetail] = Field(default_factory=list)
