"""
Pydantic schemas for Phase 4 personalized patient guidance
and caregiver support guidance.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AiSummaryStatus, GuidanceType
from app.schemas.common import ORMBaseSchema


class PersonalizedGuidanceContent(BaseModel):
    """Strict shape for personalized patient guidance."""

    model_config = ConfigDict(extra="forbid")

    overview: str | None = None

    immediate_actions: list[str] = Field(default_factory=list)
    questions_for_doctor: list[str] = Field(default_factory=list)
    medication_guidance: list[str] = Field(default_factory=list)
    nutrition_guidance: list[str] = Field(default_factory=list)
    activity_guidance: list[str] = Field(default_factory=list)
    warning_signs: list[str] = Field(default_factory=list)
    follow_up_plan: list[str] = Field(default_factory=list)
    emotional_support: list[str] = Field(default_factory=list)

    disclaimer: str


class CaregiverGuidanceContent(BaseModel):
    """Strict shape for caregiver support guidance."""

    model_config = ConfigDict(extra="forbid")

    overview: str | None = None

    daily_support: list[str] = Field(default_factory=list)
    medication_support: list[str] = Field(default_factory=list)
    appointment_support: list[str] = Field(default_factory=list)
    nutrition_support: list[str] = Field(default_factory=list)
    mobility_support: list[str] = Field(default_factory=list)
    emotional_support: list[str] = Field(default_factory=list)
    warning_signs: list[str] = Field(default_factory=list)
    caregiver_wellbeing: list[str] = Field(default_factory=list)

    disclaimer: str


class GuidanceBaseReadSchema(ORMBaseSchema):
    """Common database fields returned for both guidance types."""

    id: UUID
    report_id: UUID
    patient_id: UUID
    analysis_id: UUID
    guidance_type: GuidanceType
    status: AiSummaryStatus
    error_message: str | None
    model_name: str | None
    created_at: datetime
    updated_at: datetime


class PersonalizedGuidanceReadSchema(GuidanceBaseReadSchema):
    """Response schema for personalized patient guidance."""

    content: PersonalizedGuidanceContent | None = None


class CaregiverGuidanceReadSchema(GuidanceBaseReadSchema):
    """Response schema for caregiver guidance."""

    content: CaregiverGuidanceContent | None = None