"""Pydantic schemas for the medical reports, OCR, and AI-summary features."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import AiSummaryStatus, OcrStatus, ReportFileType
from app.schemas.common import ORMBaseSchema


class MedicalReportUploadMeta(BaseModel):
    """Non-file form fields accompanying a report upload."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class MedicalReportReadSchema(ORMBaseSchema):
    id: UUID
    patient_id: UUID
    title: str
    description: str | None
    original_filename: str
    file_type: ReportFileType
    file_size_bytes: int
    ocr_status: OcrStatus
    ocr_engine: str | None
    created_at: datetime
    updated_at: datetime
    has_ai_summary: bool = False


class MedicalReportDetailSchema(MedicalReportReadSchema):
    extracted_text: str | None = None
    ocr_error: str | None = None


class ReportAnalysisReadSchema(ORMBaseSchema):
    id: UUID
    report_id: UUID
    status: AiSummaryStatus
    error_message: str | None
    patient_friendly_summary: str | None
    medical_summary: str | None
    important_findings: list[str] | None
    cancer_type: str | None
    cancer_stage: str | None
    biomarkers: list[dict] | None
    abnormal_values: list[dict] | None
    recommendations: str | None
    follow_up_suggestions: str | None
    risk_indicators: list[str] | None
    risk_score: float | None
    model_used: str | None
    created_at: datetime
    updated_at: datetime


class ReportSearchParams(BaseModel):
    query: str | None = Field(default=None, max_length=255)
    file_type: ReportFileType | None = None
    ocr_status: OcrStatus | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
