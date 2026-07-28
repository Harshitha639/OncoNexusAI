"""User endpoints."""

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.common.constants import ApiTags
from app.common.responses import BaseResponse
from app.models.user import User
from app.schemas.auth import UserReadSchema

router = APIRouter(prefix="/users", tags=[ApiTags.USERS])


def _to_user_read_schema(user: User) -> UserReadSchema:
    """Convert a User ORM model into the public response schema."""

    role_names = [
        role.name.value if hasattr(role.name, "value") else str(role.name)
        for role in user.roles
    ]

    return UserReadSchema(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        roles=role_names,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get(
    "/me",
    response_model=BaseResponse[UserReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Get the authenticated user",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> BaseResponse[UserReadSchema]:
    """Return the currently authenticated user's account information."""

    return BaseResponse(
        message="User retrieved successfully.",
        data=_to_user_read_schema(current_user),
    )