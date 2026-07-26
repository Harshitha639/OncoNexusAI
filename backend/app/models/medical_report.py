"""MedicalReport ORM model — an uploaded patient medical report file."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import OcrStatus, ReportFileType

if TYPE_CHECKING:
    from app.models.report_analysis import ReportAnalysis
    from app.models.user import User


class MedicalReport(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A medical report file uploaded by a patient."""

    __tablename__ = "medical_reports"

    patient_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_type: Mapped[ReportFileType] = mapped_column(
        Enum(ReportFileType, name="report_file_type"), nullable=False
    )
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)

    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_status: Mapped[OcrStatus] = mapped_column(
        Enum(OcrStatus, name="ocr_status"), nullable=False, default=OcrStatus.PENDING
    )
    ocr_engine: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ocr_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    patient: Mapped["User"] = relationship()
    analysis: Mapped["ReportAnalysis | None"] = relationship(
        back_populates="report",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MedicalReport id={self.id} patient_id={self.patient_id} title={self.title!r}>"
