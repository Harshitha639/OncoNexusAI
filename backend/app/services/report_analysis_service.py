"""
AI report analysis business logic.

Bridges `MedicalReport` (must already have OCR'd `extracted_text`), the
`AiSummaryService` (Gemini call), and the `ReportAnalysis` repository.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import BadRequestException, NotFoundException
from app.models.enums import AiSummaryStatus, OcrStatus
from app.repositories.report_analysis_repository import ReportAnalysisRepository
from app.repositories.report_repository import MedicalReportRepository
from app.schemas.report import ReportAnalysisReadSchema
from app.services.ai_summary_service import AiSummaryService


class ReportAnalysisService:
    """Application-layer use cases for generating and retrieving AI summaries."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._reports = MedicalReportRepository(db)
        self._analyses = ReportAnalysisRepository(db)
        self._ai = AiSummaryService()

    async def get_analysis(
        self, report_id: uuid.UUID, patient_id: uuid.UUID
    ) -> ReportAnalysisReadSchema:
        report = await self._reports.get_by_id_for_patient(report_id, patient_id)
        if report is None:
            raise NotFoundException(message="Report not found.")

        analysis = await self._analyses.get_by_report_id(report_id)
        if analysis is None:
            raise NotFoundException(message="No AI summary has been generated for this report yet.")
        return ReportAnalysisReadSchema.model_validate(analysis)

    async def generate_analysis(
        self, report_id: uuid.UUID, patient_id: uuid.UUID
    ) -> ReportAnalysisReadSchema:
        report = await self._reports.get_by_id_for_patient(report_id, patient_id)
        if report is None:
            raise NotFoundException(message="Report not found.")

        if report.ocr_status != OcrStatus.COMPLETED or not report.extracted_text:
            raise BadRequestException(
                message=(
                    "This report's text has not been extracted yet. "
                    "Please wait for OCR processing to complete before generating a summary."
                )
            )

        existing = await self._analyses.get_by_report_id(report_id)

        if existing is not None:
            analysis = await self._analyses.update(existing, status=AiSummaryStatus.PROCESSING)
        else:
            analysis = await self._analyses.create(
                report_id=report_id, status=AiSummaryStatus.PROCESSING
            )
        await self._db.commit()

        try:
            result = await self._ai.generate_summary(report.extracted_text)
        except Exception as exc:
            analysis = await self._analyses.update(
                analysis, status=AiSummaryStatus.FAILED, error_message=str(exc)
            )
            await self._db.commit()
            raise

        analysis = await self._analyses.update(
            analysis,
            status=AiSummaryStatus.COMPLETED,
            error_message=None,
            model_used="gemini",
            **result,
        )
        await self._db.commit()
        await self._db.refresh(analysis)
        return ReportAnalysisReadSchema.model_validate(analysis)
