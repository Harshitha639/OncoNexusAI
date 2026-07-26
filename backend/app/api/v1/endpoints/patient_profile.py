"""Patient profile endpoints — create, view, and edit the patient's own profile."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_roles
from app.common.constants import ApiTags
from app.common.responses import BaseResponse
from app.database import get_db
from app.models.enums import RoleName
from app.models.user import User
from app.schemas.patient_profile import (
    PatientProfileCreateRequest,
    PatientProfileReadSchema,
    PatientProfileUpdateRequest,
)
from app.services.patient_profile_service import PatientProfileService

router = APIRouter(prefix="/patients/me/profile", tags=[ApiTags.PATIENTS])


@router.get(
    "",
    response_model=BaseResponse[PatientProfileReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Get the current patient's profile",
)
async def get_my_profile(
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[PatientProfileReadSchema]:
    """Return the authenticated patient's extended profile."""
    service = PatientProfileService(db)
    profile = await service.get_my_profile(current_user.id)
    return BaseResponse(message="Profile retrieved successfully.", data=profile)


@router.post(
    "",
    response_model=BaseResponse[PatientProfileReadSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Create the current patient's profile",
)
async def create_my_profile(
    payload: PatientProfileCreateRequest,
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[PatientProfileReadSchema]:
    """Create the authenticated patient's extended profile (once)."""
    service = PatientProfileService(db)
    profile = await service.create_profile(current_user.id, payload)
    return BaseResponse(message="Profile created successfully.", data=profile)


@router.put(
    "",
    response_model=BaseResponse[PatientProfileReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Update the current patient's profile",
)
async def update_my_profile(
    payload: PatientProfileUpdateRequest,
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[PatientProfileReadSchema]:
    """Partially update the authenticated patient's extended profile."""
    service = PatientProfileService(db)
    profile = await service.update_profile(current_user.id, payload)
    return BaseResponse(message="Profile updated successfully.", data=profile)
