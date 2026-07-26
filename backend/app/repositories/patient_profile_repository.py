"""Data-access layer for `PatientProfile` entities."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient_profile import PatientProfile


class PatientProfileRepository:
    """Encapsulates all direct SQLAlchemy queries against `patient_profiles`."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_user_id(self, user_id: uuid.UUID) -> PatientProfile | None:
        result = await self._db.execute(
            select(PatientProfile).where(PatientProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, *, user_id: uuid.UUID, **fields) -> PatientProfile:
        profile = PatientProfile(user_id=user_id, **fields)
        self._db.add(profile)
        await self._db.flush()
        return profile

    async def update(self, profile: PatientProfile, **fields) -> PatientProfile:
        for key, value in fields.items():
            setattr(profile, key, value)
        await self._db.flush()
        return profile
