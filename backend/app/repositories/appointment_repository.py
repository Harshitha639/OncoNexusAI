"""Data-access layer for `Appointment` entities."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus


class AppointmentRepository:
    """Encapsulates all direct SQLAlchemy queries against `appointments`."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id_for_patient(
        self, appointment_id: uuid.UUID, patient_id: uuid.UUID
    ) -> Appointment | None:
        result = await self._db.execute(
            select(Appointment).where(
                Appointment.id == appointment_id, Appointment.patient_id == patient_id
            )
        )
        return result.scalar_one_or_none()

    async def list_for_patient(self, patient_id: uuid.UUID) -> list[Appointment]:
        result = await self._db.execute(
            select(Appointment)
            .where(Appointment.patient_id == patient_id)
            .order_by(Appointment.scheduled_at.asc())
        )
        return list(result.scalars().all())

    async def list_upcoming_for_patient(
        self, patient_id: uuid.UUID, limit: int = 5
    ) -> list[Appointment]:
        result = await self._db.execute(
            select(Appointment)
            .where(
                Appointment.patient_id == patient_id,
                Appointment.status == AppointmentStatus.SCHEDULED,
                Appointment.scheduled_at >= datetime.now(),
            )
            .order_by(Appointment.scheduled_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, **fields) -> Appointment:
        appointment = Appointment(**fields)
        self._db.add(appointment)
        await self._db.flush()
        return appointment

    async def update(self, appointment: Appointment, **fields) -> Appointment:
        for key, value in fields.items():
            setattr(appointment, key, value)
        await self._db.flush()
        return appointment
