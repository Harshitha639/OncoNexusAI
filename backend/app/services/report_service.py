"""
Medical report business logic.

Orchestrates file storage, the `MedicalReport` repository, and the OCR
pipeline. AI summary generation lives in `ReportAnalysisService` since it
operates on already-uploaded, already-OCR'd reports.
"""

import uuid

from fastapi import BackgroundTasks, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.exceptions.base import NotFoundException
from app.models.enums import NotificationType, OcrStatus, ReportFileType
from app.models.medical_report import MedicalReport
from app.ocr import OcrExtractionError, extract_text
from app.repositories.report_repository import MedicalReportRepository
from app.schemas.report import (
    MedicalReportDetailSchema,
    MedicalReportReadSchema,
    MedicalReportUploadMeta,
)
from app.services.file_storage_service import FileStorageService, resolve_file_type
from app.services.notification_service import NotificationService

logger = get_logger(__name__)


def _to_read_schema(report: MedicalReport) -> MedicalReportReadSchema:
    schema = MedicalReportReadSchema.model_validate(report)
    schema.has_ai_summary = report.analysis is not None
    return schema


def _to_detail_schema(report: MedicalReport) -> MedicalReportDetailSchema:
    schema = MedicalReportDetailSchema.model_validate(report)
    schema.has_ai_summary = report.analysis is not None
    return schema


class ReportService:
    """Application-layer use cases for uploading and managing medical reports."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._reports = MedicalReportRepository(db)
        self._storage = FileStorageService()
        self._notifications = NotificationService(db)

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------
    async def upload_report(
        self,
        patient_id: uuid.UUID,
        meta: MedicalReportUploadMeta,
        file: UploadFile,
        background_tasks: BackgroundTasks,
    ) -> MedicalReportReadSchema:
        file_type: ReportFileType = resolve_file_type(file.filename or "")
        stored_filename, file_path, size_bytes = await self._storage.save(patient_id, file)

        report = await self._reports.create(
            patient_id=patient_id,
            title=meta.title,
            description=meta.description,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_type=file_type,
            file_size_bytes=size_bytes,
            ocr_status=OcrStatus.PENDING,
        )
        await self._db.commit()
        await self._db.refresh(report)

        await self._notifications.notify(
            user_id=patient_id,
            notification_type=NotificationType.REPORT_UPLOAD_SUCCESS,
            title="Report uploaded successfully",
            message=f"'{report.title}' was uploaded and is being processed.",
            related_entity_type="medical_report",
            related_entity_id=report.id,
        )
        await self._db.commit()

        # OCR runs after the response is sent so the upload feels instant.
        background_tasks.add_task(run_ocr_in_background, report.id)

        return _to_read_schema(report)

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------
    async def get_report_detail(
        self, report_id: uuid.UUID, patient_id: uuid.UUID
    ) -> MedicalReportDetailSchema:
        report = await self._reports.get_by_id_for_patient(report_id, patient_id)
        if report is None:
            raise NotFoundException(message="Report not found.")
        return _to_detail_schema(report)

    async def search_reports(
        self,
        patient_id: uuid.UUID,
        *,
        query: str | None,
        file_type: ReportFileType | None,
        ocr_status: OcrStatus | None,
        page: int,
        page_size: int,
    ) -> tuple[list[MedicalReportReadSchema], int]:
        reports, total = await self._reports.list_for_patient(
            patient_id,
            query=query,
            file_type=file_type,
            ocr_status=ocr_status,
            page=page,
            page_size=page_size,
        )
        return [_to_read_schema(r) for r in reports], total

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    async def delete_report(self, report_id: uuid.UUID, patient_id: uuid.UUID) -> None:
        report = await self._reports.get_by_id_for_patient(report_id, patient_id)
        if report is None:
            raise NotFoundException(message="Report not found.")

        file_path = report.file_path
        await self._reports.delete(report)
        await self._db.commit()
        self._storage.delete(file_path)


async def run_ocr_in_background(report_id: uuid.UUID) -> None:
    """Standalone background-task entrypoint — opens its own DB session
    since it runs after the request's session has already closed."""
    from app.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        repo = MedicalReportRepository(db)
        report = await repo.get_by_id(report_id)
        if report is None:
            logger.warning("OCR background task: report %s no longer exists.", report_id)
            return

        report.ocr_status = OcrStatus.PROCESSING
        await db.commit()

        try:
            text, engine = extract_text(report.file_path, report.file_type)
            report = await repo.get_by_id(report_id)
            report.extracted_text = text
            report.ocr_engine = engine
            report.ocr_status = OcrStatus.COMPLETED
            report.ocr_error = None
            await db.commit()
            logger.info("OCR completed for report %s using %s", report_id, engine)
        except OcrExtractionError as exc:
            report = await repo.get_by_id(report_id)
            report.ocr_status = OcrStatus.FAILED
            report.ocr_error = str(exc)
            await db.commit()
            logger.warning("OCR failed for report %s: %s", report_id, exc)
        except Exception as exc:  # noqa: BLE001
            report = await repo.get_by_id(report_id)
            report.ocr_status = OcrStatus.FAILED
            report.ocr_error = f"Unexpected OCR error: {exc}"
            await db.commit()
            logger.error("Unexpected OCR error for report %s: %s", report_id, exc)
