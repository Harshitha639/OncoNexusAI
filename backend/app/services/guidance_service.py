"""
Phase 4 guidance business logic.

Bridges `MedicalReport` (must have OCR completed), `ReportAnalysis` (must
exist and be completed), the `GuidanceAiService` (Gemini calls), and the
`ReportGuidance` repository. Both agents reuse the same generate/get flow,
parameterized by `GuidanceType`.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from app.models.enums import AiSummaryStatus, GuidanceType, OcrStatus
from app.repositories.report_analysis_repository import ReportAnalysisRepository
from app.repositories.report_guidance_repository import ReportGuidanceRepository
from app.repositories.report_repository import MedicalReportRepository
from app.schemas.guidance import (
    CaregiverGuidanceReadSchema,
    PersonalizedGuidanceReadSchema,
)
from app.services.guidance_ai_service import GuidanceAiService

_MODEL_NAME = "gemini"


class GuidanceService:
    """Application-layer use cases for generating and retrieving Phase 4 guidance."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._reports = MedicalReportRepository(db)
        self._analyses = ReportAnalysisRepository(db)
        self._guidance = ReportGuidanceRepository(db)
        self._ai = GuidanceAiService()

    async def _get_ready_analysis(self, report_id: uuid.UUID, patient_id: uuid.UUID):
        """Shared precondition checks for both agents.

        Verifies: report exists and belongs to the caller, OCR has
        completed, and a *completed* `ReportAnalysis` exists. Returns the
        `ReportAnalysis` row on success.
        """
        report = await self._reports.get_by_id_for_patient(report_id, patient_id)
        if report is None:
            raise NotFoundException(message="Report not found.")

        if report.ocr_status != OcrStatus.COMPLETED or not report.extracted_text:
            raise BadRequestException(
                message=(
                    "This report's text has not been extracted yet. "
                    "Please wait for OCR processing to complete before generating guidance."
                )
            )

        analysis = await self._analyses.get_by_report_id(report_id)
        if analysis is None or analysis.status != AiSummaryStatus.COMPLETED:
            raise ConflictException(
                message=(
                    "An AI report summary must be generated for this report before "
                    "guidance can be created. Please generate the AI summary first."
                )
            )

        return analysis

    async def _get_saved_guidance(
        self, report_id: uuid.UUID, patient_id: uuid.UUID, guidance_type: GuidanceType
    ):
        report = await self._reports.get_by_id_for_patient(report_id, patient_id)
        if report is None:
            raise NotFoundException(message="Report not found.")

        guidance = await self._guidance.get_by_report_and_type(report_id, guidance_type)
        if guidance is None:
            raise NotFoundException(
                message="No guidance has been generated for this report yet."
            )
        return guidance

    async def _generate(
        self, report_id: uuid.UUID, patient_id: uuid.UUID, guidance_type: GuidanceType
    ):
        analysis = await self._get_ready_analysis(report_id, patient_id)

        analysis_fields = {
            "cancer_type": analysis.cancer_type,
            "cancer_stage": analysis.cancer_stage,
            "patient_friendly_summary": analysis.patient_friendly_summary,
            "important_findings": analysis.important_findings,
            "abnormal_values": analysis.abnormal_values,
            "risk_indicators": analysis.risk_indicators,
            "recommendations": analysis.recommendations,
            "follow_up_suggestions": analysis.follow_up_suggestions,
        }

        existing = await self._guidance.get_by_report_and_type(report_id, guidance_type)
        if existing is not None:
            guidance = await self._guidance.update(existing, status=AiSummaryStatus.PROCESSING)
        else:
            guidance = await self._guidance.create(
                report_id=report_id,
                patient_id=patient_id,
                analysis_id=analysis.id,
                guidance_type=guidance_type,
                status=AiSummaryStatus.PROCESSING,
            )
        await self._db.commit()

        try:
            if guidance_type == GuidanceType.PATIENT_GUIDANCE:
                content = await self._ai.generate_personalized_guidance(analysis_fields)
            else:
                content = await self._ai.generate_caregiver_guidance(analysis_fields)
        except Exception as exc:
            guidance = await self._guidance.update(
                guidance, status=AiSummaryStatus.FAILED, error_message=str(exc)
            )
            await self._db.commit()
            raise

        guidance = await self._guidance.update(
            guidance,
            status=AiSummaryStatus.COMPLETED,
            error_message=None,
            model_name=_MODEL_NAME,
            content=content,
        )
        await self._db.commit()
        await self._db.refresh(guidance)
        return guidance

    # ------------------------------------------------------------------
    # Personalized guidance (Agent 1)
    # ------------------------------------------------------------------
    async def generate_patient_guidance(
        self, report_id: uuid.UUID, patient_id: uuid.UUID
    ) -> PersonalizedGuidanceReadSchema:
        guidance = await self._generate(report_id, patient_id, GuidanceType.PATIENT_GUIDANCE)
        return PersonalizedGuidanceReadSchema.model_validate(guidance)

    async def get_patient_guidance(
        self, report_id: uuid.UUID, patient_id: uuid.UUID
    ) -> PersonalizedGuidanceReadSchema:
        guidance = await self._get_saved_guidance(
            report_id, patient_id, GuidanceType.PATIENT_GUIDANCE
        )
        return PersonalizedGuidanceReadSchema.model_validate(guidance)

    # ------------------------------------------------------------------
    # Caregiver guidance (Agent 2)
    # ------------------------------------------------------------------
    async def generate_caregiver_guidance(
        self, report_id: uuid.UUID, patient_id: uuid.UUID
    ) -> CaregiverGuidanceReadSchema:
        guidance = await self._generate(report_id, patient_id, GuidanceType.CAREGIVER_GUIDANCE)
        return CaregiverGuidanceReadSchema.model_validate(guidance)

    async def get_caregiver_guidance(
        self, report_id: uuid.UUID, patient_id: uuid.UUID
    ) -> CaregiverGuidanceReadSchema:
        guidance = await self._get_saved_guidance(
            report_id, patient_id, GuidanceType.CAREGIVER_GUIDANCE
        )
        return CaregiverGuidanceReadSchema.model_validate(guidance)
