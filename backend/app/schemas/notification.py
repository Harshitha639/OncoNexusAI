"""Pydantic schemas for the notifications feature."""

from datetime import datetime
from uuid import UUID

from app.models.enums import NotificationType
from app.schemas.common import ORMBaseSchema


class NotificationReadSchema(ORMBaseSchema):
    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    is_read: bool
    related_entity_type: str | None
    related_entity_id: UUID | None
    created_at: datetime
