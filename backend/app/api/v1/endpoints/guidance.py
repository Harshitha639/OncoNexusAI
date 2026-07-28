"""Phase 4 guidance endpoints — Personalized Guidance and Caregiver Support.

Both agents operate on an already-generated `ReportAnalysis` for a report
the authenticated patient owns. Mirrors the existing
`POST/GET /reports/{report_id}/summary` pair in `endpoints/reports.py`.
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_roles
from app.common.constants import ApiTags
from app.common.responses import BaseResponse
from app.database import get_db
from app.models.enums import RoleName
from app.models.user import User
from app.schemas.guidance import CaregiverGuidanceReadSchema, PersonalizedGuidanceReadSchema
from app.services.guidance_service import GuidanceService

router = APIRouter(prefix="/reports/{report_id}/guidance", tags=[ApiTags.AGENTS])


@router.post(
    "/patient",
    response_model=BaseResponse[PersonalizedGuidanceReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Generate (or regenerate) personalized patient guidance for a report",
)
async def generate_patient_guidance(
    report_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[PersonalizedGuidanceReadSchema]:
    """Requires the report's AI summary to already be generated and completed."""
    service = GuidanceService(db)
    guidance = await service.generate_patient_guidance(report_id, current_user.id)
    return BaseResponse(message="Personalized guidance generated successfully.", data=guidance)


@router.get(
    "/patient",
    response_model=BaseResponse[PersonalizedGuidanceReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Get the previously generated personalized guidance for a report",
)
async def get_patient_guidance(
    report_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[PersonalizedGuidanceReadSchema]:
    service = GuidanceService(db)
    guidance = await service.get_patient_guidance(report_id, current_user.id)
    return BaseResponse(message="Personalized guidance retrieved successfully.", data=guidance)


@router.post(
    "/caregiver",
    response_model=BaseResponse[CaregiverGuidanceReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Generate (or regenerate) caregiver support guidance for a report",
)
async def generate_caregiver_guidance(
    report_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[CaregiverGuidanceReadSchema]:
    """Requires the report's AI summary to already be generated and completed."""
    service = GuidanceService(db)
    guidance = await service.generate_caregiver_guidance(report_id, current_user.id)
    return BaseResponse(message="Caregiver guidance generated successfully.", data=guidance)


@router.get(
    "/caregiver",
    response_model=BaseResponse[CaregiverGuidanceReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Get the previously generated caregiver guidance for a report",
)
async def get_caregiver_guidance(
    report_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[CaregiverGuidanceReadSchema]:
    service = GuidanceService(db)
    guidance = await service.get_caregiver_guidance(report_id, current_user.id)
    return BaseResponse(message="Caregiver guidance retrieved successfully.", data=guidance)
