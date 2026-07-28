"""Appointment ORM model — a patient-booked appointment.

Phase 3 keeps appointments simple: the doctor is captured as free-text
(name/department) rather than a linked `User`, since the Doctor Portal
is out of scope until Phase 4.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AppointmentStatus

if TYPE_CHECKING:
    from app.models.user import User


class Appointment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A scheduled care appointment booked by a patient."""

    __tablename__ = "appointments"

    patient_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    doctor_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    department: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[AppointmentStatus] = mapped_column(
        SAEnum(
            AppointmentStatus,
            name="appointment_status",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
            create_type=False,
        ),
        nullable=False,
        default=AppointmentStatus.SCHEDULED,
    )

    patient: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return (
            f"<Appointment id={self.id} "
            f"patient_id={self.patient_id} "
            f"status={self.status}>"
        )