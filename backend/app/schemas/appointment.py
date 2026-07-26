"""Pydantic schemas for the appointments feature."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.enums import AppointmentStatus
from app.schemas.common import ORMBaseSchema


class AppointmentCreateRequest(BaseModel):
    doctor_name: str = Field(..., min_length=1, max_length=255)
    department: str | None = Field(default=None, max_length=255)
    scheduled_at: datetime
    reason: str | None = Field(default=None, max_length=2000)

    @field_validator("scheduled_at")
    @classmethod
    def scheduled_at_must_be_future(cls, value: datetime) -> datetime:
        reference = datetime.now(value.tzinfo) if value.tzinfo else datetime.now()
        if value <= reference:
            raise ValueError("Appointment time must be in the future.")
        return value


class AppointmentReadSchema(ORMBaseSchema):
    id: UUID
    patient_id: UUID
    doctor_name: str
    department: str | None
    scheduled_at: datetime
    reason: str | None
    notes: str | None
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
