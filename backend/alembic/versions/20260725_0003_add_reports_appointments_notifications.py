"""Add medical_reports, report_analyses, appointments, notifications

Revision ID: 20260725_0003
Revises: 20260725_0002
Create Date: 2026-07-25 01:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260725_0003"
down_revision: Union[str, None] = "20260725_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

REPORT_FILE_TYPE = ("pdf", "jpg", "jpeg", "png")
OCR_STATUS = ("pending", "processing", "completed", "failed")
AI_SUMMARY_STATUS = ("pending", "processing", "completed", "failed")
APPOINTMENT_STATUS = ("scheduled", "cancelled", "completed")
NOTIFICATION_TYPE = (
    "appointment_reminder",
    "medication_reminder",
    "report_upload_success",
    "general",
)


def upgrade() -> None:
    bind = op.get_bind()

    report_file_type_enum = postgresql.ENUM(*REPORT_FILE_TYPE, name="report_file_type")
    ocr_status_enum = postgresql.ENUM(*OCR_STATUS, name="ocr_status")
    ai_summary_status_enum = postgresql.ENUM(*AI_SUMMARY_STATUS, name="ai_summary_status")
    appointment_status_enum = postgresql.ENUM(*APPOINTMENT_STATUS, name="appointment_status")
    notification_type_enum = postgresql.ENUM(*NOTIFICATION_TYPE, name="notification_type")

    report_file_type_enum.create(bind, checkfirst=True)
    ocr_status_enum.create(bind, checkfirst=True)
    ai_summary_status_enum.create(bind, checkfirst=True)
    appointment_status_enum.create(bind, checkfirst=True)
    notification_type_enum.create(bind, checkfirst=True)

    # ------------------------------------------------------------------
    # medical_reports
    # ------------------------------------------------------------------
    op.create_table(
        "medical_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.String(length=500), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=1000), nullable=False),
        sa.Column("file_type", report_file_type_enum, nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("ocr_status", ocr_status_enum, nullable=False, server_default="pending"),
        sa.Column("ocr_engine", sa.String(length=50), nullable=True),
        sa.Column("ocr_error", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["patient_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_medical_reports_patient_id", "medical_reports", ["patient_id"])
    op.create_index(
        "ix_medical_reports_stored_filename", "medical_reports", ["stored_filename"], unique=True
    )

    # ------------------------------------------------------------------
    # report_analyses
    # ------------------------------------------------------------------
    op.create_table(
        "report_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status", ai_summary_status_enum, nullable=False, server_default="pending"
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("patient_friendly_summary", sa.Text(), nullable=True),
        sa.Column("medical_summary", sa.Text(), nullable=True),
        sa.Column("important_findings", postgresql.JSONB(), nullable=True),
        sa.Column("cancer_type", sa.String(length=255), nullable=True),
        sa.Column("cancer_stage", sa.String(length=100), nullable=True),
        sa.Column("biomarkers", postgresql.JSONB(), nullable=True),
        sa.Column("abnormal_values", postgresql.JSONB(), nullable=True),
        sa.Column("recommendations", sa.Text(), nullable=True),
        sa.Column("follow_up_suggestions", sa.Text(), nullable=True),
        sa.Column("risk_indicators", postgresql.JSONB(), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("model_used", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["report_id"], ["medical_reports.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_report_analyses_report_id", "report_analyses", ["report_id"], unique=True
    )

    # ------------------------------------------------------------------
    # appointments
    # ------------------------------------------------------------------
    op.create_table(
        "appointments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("doctor_name", sa.String(length=255), nullable=False),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "status", appointment_status_enum, nullable=False, server_default="scheduled"
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["patient_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"])

    # ------------------------------------------------------------------
    # notifications
    # ------------------------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", notification_type_enum, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("related_entity_type", sa.String(length=50), nullable=True),
        sa.Column("related_entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("ix_appointments_patient_id", table_name="appointments")
    op.drop_table("appointments")

    op.drop_index("ix_report_analyses_report_id", table_name="report_analyses")
    op.drop_table("report_analyses")

    op.drop_index("ix_medical_reports_stored_filename", table_name="medical_reports")
    op.drop_index("ix_medical_reports_patient_id", table_name="medical_reports")
    op.drop_table("medical_reports")

    bind = op.get_bind()
    postgresql.ENUM(name="notification_type").drop(bind, checkfirst=True)
    postgresql.ENUM(name="appointment_status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="ai_summary_status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="ocr_status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="report_file_type").drop(bind, checkfirst=True)
