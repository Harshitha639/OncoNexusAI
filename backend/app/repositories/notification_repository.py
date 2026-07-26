"""Data-access layer for `Notification` entities."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:
    """Encapsulates all direct SQLAlchemy queries against `notifications`."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id_for_user(
        self, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> Notification | None:
        result = await self._db.execute(
            select(Notification).where(
                Notification.id == notification_id, Notification.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self, user_id: uuid.UUID, *, unread_only: bool = False, limit: int = 50
    ) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        stmt = stmt.order_by(Notification.created_at.desc()).limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def count_unread_for_user(self, user_id: uuid.UUID) -> int:
        result = await self._db.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        return result.scalar_one()

    async def create(self, **fields) -> Notification:
        notification = Notification(**fields)
        self._db.add(notification)
        await self._db.flush()
        return notification

    async def mark_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        await self._db.flush()
        return notification
