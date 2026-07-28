"""ReportAnalysis ORM model — Gemini-generated structured summary of a report."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AiSummaryStatus

if TYPE_CHECKING:
    from app.models.medical_report import MedicalReport


class ReportAnalysis(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """AI-generated structured analysis of a single medical report."""

    __tablename__ = "report_analyses"

    report_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("medical_reports.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    status: Mapped[AiSummaryStatus] = mapped_column(
        SAEnum(
            AiSummaryStatus,
            name="ai_summary_status",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
            create_type=False,
        ),
        nullable=False,
        default=AiSummaryStatus.PENDING,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    patient_friendly_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    medical_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    important_findings: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    cancer_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    cancer_stage: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    biomarkers: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    abnormal_values: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    recommendations: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    follow_up_suggestions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    risk_indicators: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    risk_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    model_used: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    report: Mapped["MedicalReport"] = relationship(
        back_populates="analysis",
    )

    def __repr__(self) -> str:
        return (
            f"<ReportAnalysis id={self.id} "
            f"report_id={self.report_id} "
            f"status={self.status}>"
        )