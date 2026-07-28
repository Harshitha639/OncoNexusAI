"""Add report_guidance table (Phase 4 — Personalized Guidance & Caregiver Support)

Revision ID: 20260726_0004
Revises: 20260725_0003
Create Date: 2026-07-26 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "20260726_0004"
down_revision: Union[str, None] = "20260725_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Existing enum created by migration 20260725_0003.
AI_SUMMARY_STATUS = (
    "pending",
    "processing",
    "completed",
    "failed",
)

# New enum used by the report_guidance table.
GUIDANCE_TYPE = (
    "patient_guidance",
    "caregiver_guidance",
)


def upgrade() -> None:
    bind = op.get_bind()

    # Reuse the existing ai_summary_status enum.
    ai_summary_status_enum = postgresql.ENUM(
        *AI_SUMMARY_STATUS,
        name="ai_summary_status",
        create_type=False,
    )

    # Create guidance_type only when it does not already exist.
    guidance_type_creator = postgresql.ENUM(
        *GUIDANCE_TYPE,
        name="guidance_type",
    )
    guidance_type_creator.create(
        bind,
        checkfirst=True,
    )

    # Reuse the existing guidance_type enum during table creation.
    # create_type=False prevents SQLAlchemy from trying to create it again.
    guidance_type_enum = postgresql.ENUM(
        *GUIDANCE_TYPE,
        name="guidance_type",
        create_type=False,
    )

    op.create_table(
        "report_guidance",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "report_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "analysis_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "guidance_type",
            guidance_type_enum,
            nullable=False,
        ),
        sa.Column(
            "status",
            ai_summary_status_enum,
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column(
            "content",
            postgresql.JSONB(),
            nullable=True,
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "model_name",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["medical_reports.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["analysis_id"],
            ["report_analyses.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "report_id",
            "guidance_type",
            name="uq_report_guidance_report_type",
        ),
    )

    op.create_index(
        "ix_report_guidance_report_id",
        "report_guidance",
        ["report_id"],
    )

    op.create_index(
        "ix_report_guidance_patient_id",
        "report_guidance",
        ["patient_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_report_guidance_patient_id",
        table_name="report_guidance",
    )

    op.drop_index(
        "ix_report_guidance_report_id",
        table_name="report_guidance",
    )

    op.drop_table("report_guidance")

    bind = op.get_bind()

    # Do not drop ai_summary_status because it belongs to an earlier migration.
    postgresql.ENUM(
        *GUIDANCE_TYPE,
        name="guidance_type",
    ).drop(
        bind,
        checkfirst=True,
    )