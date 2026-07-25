"""Data-access layer for `Role` entities."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import RoleName
from app.models.role import Role


class RoleRepository:
    """Encapsulates all direct SQLAlchemy queries against the `roles` table."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_name(self, name: RoleName) -> Role | None:
        result = await self._db.execute(select(Role).where(Role.name == name.value))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Role]:
        result = await self._db.execute(select(Role))
        return list(result.scalars().all())
