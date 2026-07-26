"""Data-access layer for `ReportAnalysis` entities."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import AiSummaryStatus
from app.models.medical_report import MedicalReport
from app.models.report_analysis import ReportAnalysis


class ReportAnalysisRepository:
    """Encapsulates all direct SQLAlchemy queries against `report_analyses`."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_report_id(self, report_id: uuid.UUID) -> ReportAnalysis | None:
        result = await self._db.execute(
            select(ReportAnalysis).where(ReportAnalysis.report_id == report_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_completed_for_patient(
        self, patient_id: uuid.UUID
    ) -> ReportAnalysis | None:
        result = await self._db.execute(
            select(ReportAnalysis)
            .join(MedicalReport, MedicalReport.id == ReportAnalysis.report_id)
            .where(
                MedicalReport.patient_id == patient_id,
                ReportAnalysis.status == AiSummaryStatus.COMPLETED,
            )
            .order_by(ReportAnalysis.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, *, report_id: uuid.UUID, **fields) -> ReportAnalysis:
        analysis = ReportAnalysis(report_id=report_id, **fields)
        self._db.add(analysis)
        await self._db.flush()
        return analysis

    async def update(self, analysis: ReportAnalysis, **fields) -> ReportAnalysis:
        for key, value in fields.items():
            setattr(analysis, key, value)
        await self._db.flush()
        return analysis
