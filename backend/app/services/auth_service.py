"""
Authentication business logic.

Orchestrates the user/role/refresh-token repositories plus the password
hashing and JWT utilities. Routers should depend on this service and never
touch repositories or models directly.
"""

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token, generate_refresh_token, hash_refresh_token
from app.auth.password import hash_password, verify_password
from app.exceptions.base import ConflictException, UnauthorizedException
from app.models.enums import RoleName
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, TokenPairResponse


class AuthService:
    """Application-layer authentication use cases."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._roles = RoleRepository(db)
        self._refresh_tokens = RefreshTokenRepository(db)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------
    async def register(self, payload: RegisterRequest) -> User:
        existing = await self._users.get_by_email(payload.email)
        if existing is not None:
            raise ConflictException(message="An account with this email already exists.")

        role = await self._roles.get_by_name(payload.role)
        if role is None:
            raise ConflictException(
                message=(
                    f"Role '{payload.role.value}' is not configured. "
                    "Ensure database roles have been seeded."
                ),
                code="role_not_configured",
            )

        user = await self._users.create(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
        )
        user.roles.append(role)
        await self._db.flush()
        await self._db.commit()
        await self._db.refresh(user)
        return user

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------
    async def authenticate(self, email: str, password: str) -> User:
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedException(message="Incorrect email or password.")
        if not user.is_active:
            raise UnauthorizedException(message="This account has been deactivated.")
        return user

    async def login(
        self, email: str, password: str, *, user_agent: str | None = None, ip_address: str | None = None
    ) -> TokenPairResponse:
        user = await self.authenticate(email, password)
        token_pair, _raw_refresh = await self._issue_token_pair(
            user, user_agent=user_agent, ip_address=ip_address
        )
        await self._db.commit()
        return token_pair

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------
    async def refresh(
        self,
        raw_refresh_token: str,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenPairResponse:
        token_hash = hash_refresh_token(raw_refresh_token)
        existing_token = await self._refresh_tokens.get_by_hash(token_hash)

        if existing_token is None or not RefreshTokenRepository.is_valid(existing_token):
            raise UnauthorizedException(message="Invalid or expired refresh token.")

        user = await self._users.get_by_id(existing_token.user_id)
        if user is None or not user.is_active:
            raise UnauthorizedException(message="Account is no longer active.")

        # Rotate: issue a new pair, then revoke the old token and link it
        # to the new one for audit/replay-detection purposes.
        new_pair, new_raw_refresh = await self._issue_token_pair(
            user, user_agent=user_agent, ip_address=ip_address
        )
        await self._refresh_tokens.revoke(
            existing_token, replaced_by_token_hash=hash_refresh_token(new_raw_refresh)
        )
        await self._db.commit()
        return new_pair

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------
    async def logout(self, raw_refresh_token: str) -> None:
        token_hash = hash_refresh_token(raw_refresh_token)
        existing_token = await self._refresh_tokens.get_by_hash(token_hash)
        if existing_token is not None and not existing_token.revoked:
            await self._refresh_tokens.revoke(existing_token)
        await self._db.commit()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    async def _issue_token_pair(
        self,
        user: User,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[TokenPairResponse, str]:
        """Issue a new access+refresh token pair. Returns (pair, raw_refresh_token)."""
        role_names = [role.name for role in user.roles]
        access_token, _access_expiry = create_access_token(subject=user.id, roles=role_names)

        raw_refresh, refresh_hash, refresh_expires_at = generate_refresh_token()
        await self._create_refresh_token_record(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=refresh_expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        pair = TokenPairResponse(
            access_token=access_token,
            refresh_token=raw_refresh,
            token_type="bearer",
            expires_at=refresh_expires_at,
        )
        return pair, raw_refresh

    async def _create_refresh_token_record(
        self,
        *,
        user_id: "uuid.UUID",
        token_hash: str,
        expires_at: "datetime",
        user_agent: str | None,
        ip_address: str | None,
    ) -> RefreshToken:
        return await self._refresh_tokens.create(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
