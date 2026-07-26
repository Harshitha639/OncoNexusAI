"""Notification business logic — create and query in-app notifications."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import NotFoundException
from app.models.enums import NotificationType
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationReadSchema


class NotificationService:
    """Application-layer use cases for user notifications."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._notifications = NotificationRepository(db)

    async def notify(
        self,
        *,
        user_id: uuid.UUID,
        notification_type: NotificationType,
        title: str,
        message: str,
        related_entity_type: str | None = None,
        related_entity_id: uuid.UUID | None = None,
    ) -> NotificationReadSchema:
        """Create a notification. Does NOT commit — callers typically create a
        notification as part of a larger transaction (e.g. report upload)."""
        notification = await self._notifications.create(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )
        return NotificationReadSchema.model_validate(notification)

    async def list_my_notifications(
        self, user_id: uuid.UUID, *, unread_only: bool = False
    ) -> list[NotificationReadSchema]:
        notifications = await self._notifications.list_for_user(user_id, unread_only=unread_only)
        return [NotificationReadSchema.model_validate(n) for n in notifications]

    async def count_unread(self, user_id: uuid.UUID) -> int:
        return await self._notifications.count_unread_for_user(user_id)

    async def mark_as_read(
        self, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> NotificationReadSchema:
        notification = await self._notifications.get_by_id_for_user(notification_id, user_id)
        if notification is None:
            raise NotFoundException(message="Notification not found.")
        notification = await self._notifications.mark_read(notification)
        await self._db.commit()
        return NotificationReadSchema.model_validate(notification)
