"""Medical report endpoints — upload, history, search, detail, delete, AI summary."""

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_roles
from app.common.constants import ApiTags
from app.common.responses import BaseResponse, PaginatedResponse
from app.database import get_db
from app.models.enums import OcrStatus, ReportFileType, RoleName
from app.models.user import User
from app.schemas.report import (
    MedicalReportDetailSchema,
    MedicalReportReadSchema,
    MedicalReportUploadMeta,
    ReportAnalysisReadSchema,
)
from app.services.report_analysis_service import ReportAnalysisService
from app.services.report_service import ReportService
from app.utils.pagination import build_pagination_meta, normalize_pagination

router = APIRouter(prefix="/reports", tags=[ApiTags.REPORTS])


@router.post(
    "",
    response_model=BaseResponse[MedicalReportReadSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Upload a medical report (PDF, JPG, JPEG, or PNG)",
)
async def upload_report(
    background_tasks: BackgroundTasks,
    title: str = Form(..., min_length=1, max_length=255),
    description: str | None = Form(default=None, max_length=2000),
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[MedicalReportReadSchema]:
    """Upload a report file. Max size 20 MB. Text extraction (OCR) runs in
    the background — poll `GET /reports/{id}` to see when it completes."""
    service = ReportService(db)
    meta = MedicalReportUploadMeta(title=title, description=description)
    report = await service.upload_report(current_user.id, meta, file, background_tasks)
    return BaseResponse(message="Report uploaded successfully. Processing in background.", data=report)


@router.get(
    "",
    response_model=PaginatedResponse[list[MedicalReportReadSchema]],
    status_code=status.HTTP_200_OK,
    summary="List / search the current patient's reports (report history)",
)
async def list_reports(
    query: str | None = Query(default=None, max_length=255, description="Free-text search"),
    file_type: ReportFileType | None = Query(default=None),
    ocr_status: OcrStatus | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[list[MedicalReportReadSchema]]:
    """Report history with optional free-text search and filters."""
    page, page_size = normalize_pagination(page, page_size)
    service = ReportService(db)
    reports, total = await service.search_reports(
        current_user.id,
        query=query,
        file_type=file_type,
        ocr_status=ocr_status,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        message="Reports retrieved successfully.",
        data=reports,
        meta=build_pagination_meta(total, page, page_size),
    )


@router.get(
    "/{report_id}",
    response_model=BaseResponse[MedicalReportDetailSchema],
    status_code=status.HTTP_200_OK,
    summary="View a single report (including extracted text once OCR completes)",
)
async def get_report(
    report_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[MedicalReportDetailSchema]:
    service = ReportService(db)
    report = await service.get_report_detail(report_id, current_user.id)
    return BaseResponse(message="Report retrieved successfully.", data=report)


@router.delete(
    "/{report_id}",
    response_model=BaseResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete a report and its stored file",
)
async def delete_report(
    report_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[None]:
    service = ReportService(db)
    await service.delete_report(report_id, current_user.id)
    return BaseResponse(message="Report deleted successfully.", data=None)


@router.post(
    "/{report_id}/summary",
    response_model=BaseResponse[ReportAnalysisReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Generate (or regenerate) the AI summary for a report via Gemini",
)
async def generate_report_summary(
    report_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ReportAnalysisReadSchema]:
    """Requires OCR to have completed first (see `GET /reports/{id}`)."""
    service = ReportAnalysisService(db)
    analysis = await service.generate_analysis(report_id, current_user.id)
    return BaseResponse(message="AI summary generated successfully.", data=analysis)


@router.get(
    "/{report_id}/summary",
    response_model=BaseResponse[ReportAnalysisReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Get the previously generated AI summary for a report",
)
async def get_report_summary(
    report_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[ReportAnalysisReadSchema]:
    service = ReportAnalysisService(db)
    analysis = await service.get_analysis(report_id, current_user.id)
    return BaseResponse(message="AI summary retrieved successfully.", data=analysis)
