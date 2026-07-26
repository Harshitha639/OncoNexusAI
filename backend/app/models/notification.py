"""Notification ORM model — in-app notifications for a user."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import NotificationType

if TYPE_CHECKING:
    from app.models.user import User


def enum_values(enum_class: type) -> list[str]:
    """Return enum values instead of enum member names for PostgreSQL."""
    return [member.value for member in enum_class]


class Notification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single in-app notification delivered to a user."""

    __tablename__ = "notifications"

    user_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type: Mapped[NotificationType] = mapped_column(
        Enum(
            NotificationType,
            name="notification_type",
            values_callable=enum_values,
        ),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    related_entity_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    related_entity_id: Mapped[PG_UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return (
            f"<Notification id={self.id} "
            f"user_id={self.user_id} "
            f"type={self.type}>"
        )