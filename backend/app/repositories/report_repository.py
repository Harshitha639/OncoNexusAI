"""Data-access layer for `MedicalReport` entities."""

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import OcrStatus, ReportFileType
from app.models.medical_report import MedicalReport


class MedicalReportRepository:
    """Encapsulates all direct SQLAlchemy queries against `medical_reports`."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, report_id: uuid.UUID) -> MedicalReport | None:
        result = await self._db.execute(
            select(MedicalReport).where(MedicalReport.id == report_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_for_patient(
        self, report_id: uuid.UUID, patient_id: uuid.UUID
    ) -> MedicalReport | None:
        result = await self._db.execute(
            select(MedicalReport).where(
                MedicalReport.id == report_id, MedicalReport.patient_id == patient_id
            )
        )
        return result.scalar_one_or_none()

    async def list_for_patient(
        self,
        patient_id: uuid.UUID,
        *,
        query: str | None = None,
        file_type: ReportFileType | None = None,
        ocr_status: OcrStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[MedicalReport], int]:
        stmt = select(MedicalReport).where(MedicalReport.patient_id == patient_id)

        if query:
            like_pattern = f"%{query}%"
            stmt = stmt.where(
                or_(
                    MedicalReport.title.ilike(like_pattern),
                    MedicalReport.description.ilike(like_pattern),
                    MedicalReport.extracted_text.ilike(like_pattern),
                )
            )
        if file_type is not None:
            stmt = stmt.where(MedicalReport.file_type == file_type)
        if ocr_status is not None:
            stmt = stmt.where(MedicalReport.ocr_status == ocr_status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._db.execute(count_stmt)).scalar_one()

        stmt = (
            stmt.order_by(MedicalReport.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all()), total

    async def list_recent_for_patient(
        self, patient_id: uuid.UUID, limit: int = 5
    ) -> list[MedicalReport]:
        result = await self._db.execute(
            select(MedicalReport)
            .where(MedicalReport.patient_id == patient_id)
            .order_by(MedicalReport.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_for_patient(self, patient_id: uuid.UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .select_from(MedicalReport)
            .where(MedicalReport.patient_id == patient_id)
        )
        return result.scalar_one()

    async def create(self, **fields) -> MedicalReport:
        report = MedicalReport(**fields)
        self._db.add(report)
        await self._db.flush()
        return report

    async def delete(self, report: MedicalReport) -> None:
        await self._db.delete(report)
        await self._db.flush()
