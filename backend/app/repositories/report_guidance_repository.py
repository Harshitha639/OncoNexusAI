"""Data-access layer for `ReportGuidance` entities."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import GuidanceType
from app.models.report_guidance import ReportGuidance


class ReportGuidanceRepository:
    """Encapsulates all direct SQLAlchemy queries against `report_guidance`."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_report_and_type(
        self, report_id: uuid.UUID, guidance_type: GuidanceType
    ) -> ReportGuidance | None:
        result = await self._db.execute(
            select(ReportGuidance).where(
                ReportGuidance.report_id == report_id,
                ReportGuidance.guidance_type == guidance_type,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, **fields) -> ReportGuidance:
        guidance = ReportGuidance(**fields)
        self._db.add(guidance)
        await self._db.flush()
        return guidance

    async def update(self, guidance: ReportGuidance, **fields) -> ReportGuidance:
        for key, value in fields.items():
            setattr(guidance, key, value)
        await self._db.flush()
        return guidance
