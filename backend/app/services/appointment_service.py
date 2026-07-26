"""Appointment business logic — book, view, and cancel appointments."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import BadRequestException, NotFoundException
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus, NotificationType
from app.repositories.appointment_repository import AppointmentRepository
from app.schemas.appointment import AppointmentCreateRequest, AppointmentReadSchema
from app.services.notification_service import NotificationService


def _to_read_schema(appointment: Appointment) -> AppointmentReadSchema:
    return AppointmentReadSchema.model_validate(appointment)


class AppointmentService:
    """Application-layer use cases for patient appointments."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._appointments = AppointmentRepository(db)
        self._notifications = NotificationService(db)

    async def book_appointment(
        self, patient_id: uuid.UUID, payload: AppointmentCreateRequest
    ) -> AppointmentReadSchema:
        appointment = await self._appointments.create(
            patient_id=patient_id,
            doctor_name=payload.doctor_name,
            department=payload.department,
            scheduled_at=payload.scheduled_at,
            reason=payload.reason,
            status=AppointmentStatus.SCHEDULED,
        )
        await self._notifications.notify(
            user_id=patient_id,
            notification_type=NotificationType.APPOINTMENT_REMINDER,
            title="Appointment booked",
            message=(
                f"Your appointment with {payload.doctor_name} is scheduled for "
                f"{payload.scheduled_at.strftime('%B %d, %Y at %I:%M %p')}."
            ),
            related_entity_type="appointment",
            related_entity_id=appointment.id,
        )
        await self._db.commit()
        await self._db.refresh(appointment)
        return _to_read_schema(appointment)

    async def list_my_appointments(self, patient_id: uuid.UUID) -> list[AppointmentReadSchema]:
        appointments = await self._appointments.list_for_patient(patient_id)
        return [_to_read_schema(a) for a in appointments]

    async def cancel_appointment(
        self, appointment_id: uuid.UUID, patient_id: uuid.UUID
    ) -> AppointmentReadSchema:
        appointment = await self._appointments.get_by_id_for_patient(appointment_id, patient_id)
        if appointment is None:
            raise NotFoundException(message="Appointment not found.")
        if appointment.status != AppointmentStatus.SCHEDULED:
            raise BadRequestException(message="Only scheduled appointments can be cancelled.")

        appointment = await self._appointments.update(
            appointment, status=AppointmentStatus.CANCELLED
        )
        await self._db.commit()
        await self._db.refresh(appointment)
        return _to_read_schema(appointment)
