"""PatientProfile ORM model — extended medical/demographic profile for a patient."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AlcoholConsumption, BloodGroup, Gender, SmokingStatus

if TYPE_CHECKING:
    from app.models.user import User


class PatientProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Extended profile information for a `patient`-role user.

    One-to-one with `User` — every patient has at most one profile.
    """

    __tablename__ = "patient_profiles"

    user_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender"), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    blood_group: Mapped[BloodGroup | None] = mapped_column(
        Enum(BloodGroup, name="blood_group"), nullable=True
    )
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    emergency_contact_relationship: Mapped[str | None] = mapped_column(String(100), nullable=True)

    family_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_medications: Mapped[str | None] = mapped_column(Text, nullable=True)

    smoking_status: Mapped[SmokingStatus | None] = mapped_column(
        Enum(SmokingStatus, name="smoking_status"), nullable=True
    )
    alcohol_consumption: Mapped[AlcoholConsumption | None] = mapped_column(
        Enum(AlcoholConsumption, name="alcohol_consumption"), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="patient_profile")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<PatientProfile id={self.id} user_id={self.user_id}>"
