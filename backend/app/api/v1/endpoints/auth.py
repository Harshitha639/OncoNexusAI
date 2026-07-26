"""Authentication endpoints — register, login, refresh, logout."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.constants import ApiTags
from app.common.responses import BaseResponse
from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
    UserReadSchema,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=[ApiTags.AUTH])


def _client_meta(request: Request) -> tuple[str | None, str | None]:
    """Extract user-agent and client IP for refresh-token audit fields."""
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    return user_agent, ip_address


@router.post(
    "/register",
    response_model=BaseResponse[UserReadSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[UserReadSchema]:
    """Create a new user account with the requested role (defaults to `patient`)."""
    service = AuthService(db)
    user = await service.register(payload)
    return BaseResponse(
        message="Account created successfully.",
        data=UserReadSchema.model_validate(user),
    )


@router.post(
    "/login",
    response_model=BaseResponse[TokenPairResponse],
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive an access/refresh token pair",
)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[TokenPairResponse]:
    """Authenticate with email + password and receive a JWT token pair."""
    service = AuthService(db)
    user_agent, ip_address = _client_meta(request)
    token_pair = await service.login(
        payload.email, payload.password, user_agent=user_agent, ip_address=ip_address
    )
    return BaseResponse(message="Login successful.", data=token_pair)


@router.post(
    "/refresh",
    response_model=BaseResponse[TokenPairResponse],
    status_code=status.HTTP_200_OK,
    summary="Exchange a valid refresh token for a new token pair",
)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[TokenPairResponse]:
    """Rotate the given refresh token for a new access/refresh token pair."""
    service = AuthService(db)
    user_agent, ip_address = _client_meta(request)
    token_pair = await service.refresh(
        payload.refresh_token, user_agent=user_agent, ip_address=ip_address
    )
    return BaseResponse(message="Token refreshed successfully.", data=token_pair)


@router.post(
    "/logout",
    response_model=BaseResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Revoke a refresh token (logout)",
)
async def logout(
    payload: LogoutRequest,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[None]:
    """Revoke the given refresh token so it can no longer be used."""
    service = AuthService(db)
    await service.logout(payload.refresh_token)
    return BaseResponse(message="Logged out successfully.", data=None)
