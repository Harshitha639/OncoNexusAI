"""Pydantic schema for the patient dashboard aggregate response."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.appointment import AppointmentReadSchema
from app.schemas.report import MedicalReportReadSchema, ReportAnalysisReadSchema


class DashboardWelcomeSchema(BaseModel):
    full_name: str
    email: str
    roles: list[str]


class DashboardSummarySchema(BaseModel):
    welcome: DashboardWelcomeSchema
    profile_completion_percentage: int
    has_profile: bool
    recent_reports: list[MedicalReportReadSchema]
    latest_ai_summary: ReportAnalysisReadSchema | None
    latest_risk_score: float | None
    upcoming_appointments: list[AppointmentReadSchema]
    unread_notification_count: int
    total_reports: int
