"""
Patient profile business logic.

Every field in `PROFILE_COMPLETION_FIELDS` counts toward the profile
completion percentage surfaced on the dashboard.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import ConflictException, NotFoundException
from app.models.patient_profile import PatientProfile
from app.repositories.patient_profile_repository import PatientProfileRepository
from app.schemas.patient_profile import (
    PatientProfileCreateRequest,
    PatientProfileReadSchema,
    PatientProfileUpdateRequest,
)

PROFILE_COMPLETION_FIELDS: tuple[str, ...] = (
    "date_of_birth",
    "gender",
    "phone_number",
    "blood_group",
    "height_cm",
    "weight_kg",
    "address",
    "emergency_contact_name",
    "emergency_contact_phone",
    "family_history",
    "allergies",
    "current_medications",
    "smoking_status",
    "alcohol_consumption",
)


def calculate_profile_completion_percentage(profile: PatientProfile) -> int:
    filled = sum(1 for field in PROFILE_COMPLETION_FIELDS if getattr(profile, field) not in (None, ""))
    return round((filled / len(PROFILE_COMPLETION_FIELDS)) * 100)


def _to_read_schema(profile: PatientProfile) -> PatientProfileReadSchema:
    schema = PatientProfileReadSchema.model_validate(profile)
    schema.completion_percentage = calculate_profile_completion_percentage(profile)
    return schema


class PatientProfileService:
    """Application-layer use cases for managing a patient's extended profile."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._profiles = PatientProfileRepository(db)

    async def get_my_profile(self, user_id: uuid.UUID) -> PatientProfileReadSchema:
        profile = await self._profiles.get_by_user_id(user_id)
        if profile is None:
            raise NotFoundException(message="You have not created a patient profile yet.")
        return _to_read_schema(profile)

    async def get_profile_or_none(self, user_id: uuid.UUID) -> PatientProfileReadSchema | None:
        profile = await self._profiles.get_by_user_id(user_id)
        return _to_read_schema(profile) if profile is not None else None

    async def create_profile(
        self, user_id: uuid.UUID, payload: PatientProfileCreateRequest
    ) -> PatientProfileReadSchema:
        existing = await self._profiles.get_by_user_id(user_id)
        if existing is not None:
            raise ConflictException(message="A profile already exists for this account.")

        profile = await self._profiles.create(user_id=user_id, **payload.model_dump())
        await self._db.commit()
        await self._db.refresh(profile)
        return _to_read_schema(profile)

    async def update_profile(
        self, user_id: uuid.UUID, payload: PatientProfileUpdateRequest
    ) -> PatientProfileReadSchema:
        profile = await self._profiles.get_by_user_id(user_id)
        if profile is None:
            raise NotFoundException(message="You have not created a patient profile yet.")

        updates = payload.model_dump(exclude_unset=True)
        profile = await self._profiles.update(profile, **updates)
        await self._db.commit()
        await self._db.refresh(profile)
        return _to_read_schema(profile)
