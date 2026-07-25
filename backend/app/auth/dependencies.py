"""
FastAPI dependencies for authentication and role-based authorization.

Usage:
    @router.get("/me")
    async def me(current_user: User = Depends(get_current_user)): ...

    @router.get("/admin-only")
    async def admin_only(_: User = Depends(require_roles(RoleName.ADMIN))): ...
"""

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_access_token
from app.database import get_db
from app.exceptions.base import ForbiddenException, UnauthorizedException
from app.models.enums import RoleName
from app.models.user import User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False, description="JWT access token")


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Resolve the authenticated `User` from the `Authorization: Bearer <token>` header."""
    if credentials is None or not credentials.credentials:
        raise UnauthorizedException(message="Not authenticated.")

    payload = decode_access_token(credentials.credentials)
    user_id_raw = payload.get("sub")
    if not user_id_raw:
        raise UnauthorizedException(message="Invalid access token payload.")

    try:
        user_id = uuid.UUID(user_id_raw)
    except (ValueError, TypeError) as exc:
        raise UnauthorizedException(message="Invalid access token subject.") from exc

    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise UnauthorizedException(message="User no longer exists.")
    if not user.is_active:
        raise ForbiddenException(message="This account has been deactivated.")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*allowed_roles: RoleName):
    """Dependency factory restricting access to users holding one of `allowed_roles`."""

    async def _check_roles(current_user: CurrentUser) -> User:
        user_role_names = {role.name for role in current_user.roles}
        allowed_names = {role.value for role in allowed_roles}
        if not user_role_names.intersection(allowed_names):
            raise ForbiddenException(
                message="You do not have permission to perform this action."
            )
        return current_user

    return _check_roles
