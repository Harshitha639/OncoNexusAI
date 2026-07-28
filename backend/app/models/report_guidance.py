"""ReportGuidance ORM model — Phase 4 AI-generated supportive guidance.

Stores the output of the two Phase 4 agents (Personalized Guidance and
Caregiver Support), keyed by `(report_id, guidance_type)`. Both agents
consume the already-generated `ReportAnalysis` rather than re-reading the
raw report text.

NOTE on enum storage: unlike some pre-existing enum columns in this
project, `guidance_type` explicitly passes `values_callable` so SQLAlchemy
persists the enum's *value* (e.g. "patient_guidance") rather than its
member *name* (e.g. "PATIENT_GUIDANCE"). This matches the lowercase labels
defined in the Postgres enum type created by the migration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AiSummaryStatus, GuidanceType

if TYPE_CHECKING:
    from app.models.medical_report import MedicalReport
    from app.models.report_analysis import ReportAnalysis
    from app.models.user import User


class ReportGuidance(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """AI-generated (Gemini) supportive guidance for a single `MedicalReport`,
    either for the patient or for a caregiver, derived from its `ReportAnalysis`."""

    __tablename__ = "report_guidance"
    __table_args__ = (
        UniqueConstraint("report_id", "guidance_type", name="uq_report_guidance_report_type"),
    )

    report_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("medical_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    analysis_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("report_analyses.id", ondelete="CASCADE"),
        nullable=False,
    )

    guidance_type: Mapped[GuidanceType] = mapped_column(
        Enum(
            GuidanceType,
            name="guidance_type",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    status: Mapped[AiSummaryStatus] = mapped_column(
        Enum(
            AiSummaryStatus,
            name="ai_summary_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=AiSummaryStatus.PENDING,
    )
    content: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    report: Mapped["MedicalReport"] = relationship()
    patient: Mapped["User"] = relationship()
    analysis: Mapped["ReportAnalysis"] = relationship()

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ReportGuidance id={self.id} report_id={self.report_id} "
            f"type={self.guidance_type} status={self.status}>"
        )
