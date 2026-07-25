"""UserRole — many-to-many association between `users` and `roles`."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Join table linking a `User` to a `Role`.

    Modeled as an explicit entity (rather than a bare `Table`) so it gets
    its own primary key and audit timestamps, and can be extended later
    (e.g. `granted_by`, `expires_at`) without a migration rewrite.
    """

    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"
