"""Notification endpoints — list and mark-as-read for the current user."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.common.constants import ApiTags
from app.common.responses import BaseResponse
from app.database import get_db
from app.schemas.notification import NotificationReadSchema
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=[ApiTags.NOTIFICATIONS])


@router.get(
    "",
    response_model=BaseResponse[list[NotificationReadSchema]],
    status_code=status.HTTP_200_OK,
    summary="List the current user's notifications",
)
async def list_notifications(
    current_user: CurrentUser,
    unread_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[list[NotificationReadSchema]]:
    service = NotificationService(db)
    notifications = await service.list_my_notifications(current_user.id, unread_only=unread_only)
    return BaseResponse(message="Notifications retrieved successfully.", data=notifications)


@router.get(
    "/unread-count",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get the current user's unread notification count",
)
async def unread_count(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[dict]:
    service = NotificationService(db)
    count = await service.count_unread(current_user.id)
    return BaseResponse(message="Unread count retrieved successfully.", data={"unread_count": count})


@router.post(
    "/{notification_id}/read",
    response_model=BaseResponse[NotificationReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Mark a notification as read",
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[NotificationReadSchema]:
    service = NotificationService(db)
    notification = await service.mark_as_read(notification_id, current_user.id)
    return BaseResponse(message="Notification marked as read.", data=notification)
