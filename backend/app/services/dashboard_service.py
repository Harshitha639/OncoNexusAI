"""Patient dashboard aggregation logic."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.patient_profile_repository import PatientProfileRepository
from app.repositories.report_analysis_repository import ReportAnalysisRepository
from app.repositories.report_repository import MedicalReportRepository
from app.schemas.appointment import AppointmentReadSchema
from app.schemas.dashboard import DashboardSummarySchema, DashboardWelcomeSchema
from app.schemas.report import MedicalReportReadSchema, ReportAnalysisReadSchema
from app.services.patient_profile_service import calculate_profile_completion_percentage


class DashboardService:
    """Aggregates data from every Phase 3 feature into a single dashboard payload."""

    def __init__(self, db: AsyncSession) -> None:
        self._profiles = PatientProfileRepository(db)
        self._reports = MedicalReportRepository(db)
        self._analyses = ReportAnalysisRepository(db)
        self._appointments = AppointmentRepository(db)
        self._notifications = NotificationRepository(db)

    async def get_summary(self, user: User) -> DashboardSummarySchema:
        profile = await self._profiles.get_by_user_id(user.id)
        completion = calculate_profile_completion_percentage(profile) if profile is not None else 0

        recent_reports = await self._reports.list_recent_for_patient(user.id, limit=5)
        total_reports = await self._reports.count_for_patient(user.id)

        latest_analysis = await self._analyses.get_latest_completed_for_patient(user.id)

        upcoming_appointments = await self._appointments.list_upcoming_for_patient(
            user.id, limit=5
        )
        unread_count = await self._notifications.count_unread_for_user(user.id)

        recent_report_schemas = []
        for report in recent_reports:
            schema = MedicalReportReadSchema.model_validate(report)
            schema.has_ai_summary = report.analysis is not None
            recent_report_schemas.append(schema)

        return DashboardSummarySchema(
            welcome=DashboardWelcomeSchema(
                full_name=user.full_name,
                email=user.email,
                roles=[role.name for role in user.roles],
            ),
            profile_completion_percentage=completion,
            has_profile=profile is not None,
            recent_reports=recent_report_schemas,
            latest_ai_summary=(
                ReportAnalysisReadSchema.model_validate(latest_analysis)
                if latest_analysis is not None
                else None
            ),
            latest_risk_score=(
                latest_analysis.risk_score if latest_analysis is not None else None
            ),
            upcoming_appointments=[
                AppointmentReadSchema.model_validate(a) for a in upcoming_appointments
            ],
            unread_notification_count=unread_count,
            total_reports=total_reports,
        )
