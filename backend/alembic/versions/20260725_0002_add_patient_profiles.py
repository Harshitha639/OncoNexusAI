"""Add patient_profiles table

Revision ID: 20260725_0002
Revises: 20260724_0001
Create Date: 2026-07-25 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260725_0002"
down_revision: Union[str, None] = "20260724_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

GENDER = ("male", "female", "other", "prefer_not_to_say")
BLOOD_GROUP = ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "unknown")
SMOKING_STATUS = ("never", "former", "current")
ALCOHOL_CONSUMPTION = ("never", "occasional", "regular", "frequent")


def upgrade() -> None:
    gender_enum = postgresql.ENUM(
        *GENDER,
        name="gender",
        create_type=False,
    )

    blood_group_enum = postgresql.ENUM(
        *BLOOD_GROUP,
        name="blood_group",
        create_type=False,
    )

    smoking_status_enum = postgresql.ENUM(
        *SMOKING_STATUS,
        name="smoking_status",
        create_type=False,
    )

    alcohol_consumption_enum = postgresql.ENUM(
        *ALCOHOL_CONSUMPTION,
        name="alcohol_consumption",
        create_type=False,
    )

    bind = op.get_bind()
    gender_enum.create(bind, checkfirst=True)
    blood_group_enum.create(bind, checkfirst=True)
    smoking_status_enum.create(bind, checkfirst=True)
    alcohol_consumption_enum.create(bind, checkfirst=True)

    op.create_table(
        "patient_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", gender_enum, nullable=True),
        sa.Column("phone_number", sa.String(length=32), nullable=True),
        sa.Column("blood_group", blood_group_enum, nullable=True),
        sa.Column("height_cm", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("emergency_contact_name", sa.String(length=255), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(length=32), nullable=True),
        sa.Column("emergency_contact_relationship", sa.String(length=100), nullable=True),
        sa.Column("family_history", sa.Text(), nullable=True),
        sa.Column("allergies", sa.Text(), nullable=True),
        sa.Column("current_medications", sa.Text(), nullable=True),
        sa.Column("smoking_status", smoking_status_enum, nullable=True),
        sa.Column("alcohol_consumption", alcohol_consumption_enum, nullable=True),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_patient_profiles_user_id", "patient_profiles", ["user_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_patient_profiles_user_id", table_name="patient_profiles")
    op.drop_table("patient_profiles")

    bind = op.get_bind()
    postgresql.ENUM(name="alcohol_consumption").drop(bind, checkfirst=True)
    postgresql.ENUM(name="smoking_status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="blood_group").drop(bind, checkfirst=True)
    postgresql.ENUM(name="gender").drop(bind, checkfirst=True)
