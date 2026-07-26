"""Pydantic schemas for the patient profile feature."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.enums import AlcoholConsumption, BloodGroup, Gender, SmokingStatus
from app.schemas.common import ORMBaseSchema


class PatientProfileBase(BaseModel):
    date_of_birth: date | None = None
    gender: Gender | None = None
    phone_number: str | None = Field(default=None, max_length=32)
    blood_group: BloodGroup | None = None
    height_cm: float | None = Field(default=None, gt=0, le=300)
    weight_kg: float | None = Field(default=None, gt=0, le=500)
    address: str | None = Field(default=None, max_length=2000)
    emergency_contact_name: str | None = Field(default=None, max_length=255)
    emergency_contact_phone: str | None = Field(default=None, max_length=32)
    emergency_contact_relationship: str | None = Field(default=None, max_length=100)
    family_history: str | None = Field(default=None, max_length=4000)
    allergies: str | None = Field(default=None, max_length=2000)
    current_medications: str | None = Field(default=None, max_length=2000)
    smoking_status: SmokingStatus | None = None
    alcohol_consumption: AlcoholConsumption | None = None

    @field_validator("date_of_birth")
    @classmethod
    def date_of_birth_not_in_future(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return value


class PatientProfileCreateRequest(PatientProfileBase):
    """Payload for creating a patient profile. All fields are optional except
    none are strictly required — patients can fill their profile incrementally."""

    pass


class PatientProfileUpdateRequest(PatientProfileBase):
    """Payload for partially updating a patient profile (all fields optional)."""

    pass


class PatientProfileReadSchema(PatientProfileBase, ORMBaseSchema):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    completion_percentage: int = Field(
        default=0, description="Percentage (0-100) of profile fields that are filled in."
    )
