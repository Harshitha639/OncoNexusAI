"""Appointment endpoints — book, view, and cancel appointments."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_roles
from app.common.constants import ApiTags
from app.common.responses import BaseResponse
from app.database import get_db
from app.models.enums import RoleName
from app.models.user import User
from app.schemas.appointment import AppointmentCreateRequest, AppointmentReadSchema
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=[ApiTags.APPOINTMENTS])


@router.post(
    "",
    response_model=BaseResponse[AppointmentReadSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Book a new appointment",
)
async def book_appointment(
    payload: AppointmentCreateRequest,
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[AppointmentReadSchema]:
    service = AppointmentService(db)
    appointment = await service.book_appointment(current_user.id, payload)
    return BaseResponse(message="Appointment booked successfully.", data=appointment)


@router.get(
    "",
    response_model=BaseResponse[list[AppointmentReadSchema]],
    status_code=status.HTTP_200_OK,
    summary="List the current patient's appointments",
)
async def list_appointments(
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[list[AppointmentReadSchema]]:
    service = AppointmentService(db)
    appointments = await service.list_my_appointments(current_user.id)
    return BaseResponse(message="Appointments retrieved successfully.", data=appointments)


@router.post(
    "/{appointment_id}/cancel",
    response_model=BaseResponse[AppointmentReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Cancel a scheduled appointment",
)
async def cancel_appointment(
    appointment_id: uuid.UUID,
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[AppointmentReadSchema]:
    service = AppointmentService(db)
    appointment = await service.cancel_appointment(appointment_id, current_user.id)
    return BaseResponse(message="Appointment cancelled successfully.", data=appointment)
