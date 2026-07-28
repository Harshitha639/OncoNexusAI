"""Pydantic request/response contracts for the authentication API."""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import RoleName

_PASSWORD_MIN_LENGTH = 8


class RegisterRequest(BaseModel):
    """Payload for `POST /api/v1/auth/register`."""

    email: EmailStr
    password: str = Field(..., min_length=_PASSWORD_MIN_LENGTH, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=255)
    role: RoleName = Field(
        default=RoleName.PATIENT,
        description="Requested account role. Defaults to 'patient'.",
    )

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value: str) -> str:
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("Password must contain at least one letter and one number.")
        return value

    @field_validator("full_name")
    @classmethod
    def full_name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Full name cannot be blank.")
        return value.strip()


class LoginRequest(BaseModel):
    """Payload for `POST /api/v1/auth/login`."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    """Payload for `POST /api/v1/auth/refresh`."""

    refresh_token: str = Field(..., min_length=1)


class LogoutRequest(BaseModel):
    """Payload for `POST /api/v1/auth/logout`."""

    refresh_token: str = Field(..., min_length=1)


class TokenPairResponse(BaseModel):
    """Access + refresh token pair returned on successful login/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime


class UserReadSchema(BaseModel):
    """Public-facing representation of a `User`."""

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    roles: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("roles", mode="before")
    @classmethod
    def coerce_roles(cls, value: object) -> list[str]:
        if value and hasattr(value, "__iter__") and not isinstance(value, (str, list)):
            return [getattr(role, "name", role) for role in value]
        return value  # type: ignore[return-value]
