"""User profile endpoints."""

from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser
from app.common.constants import ApiTags
from app.common.responses import BaseResponse
from app.schemas.auth import UserReadSchema

router = APIRouter(prefix="/users", tags=[ApiTags.USERS])


@router.get(
    "/me",
    response_model=BaseResponse[UserReadSchema],
    status_code=status.HTTP_200_OK,
    summary="Get the currently authenticated user's profile",
)
async def get_me(current_user: CurrentUser) -> BaseResponse[UserReadSchema]:
    """Return the profile of the authenticated user (resolved from the JWT)."""
    return BaseResponse(
        message="Current user retrieved successfully.",
        data=UserReadSchema.model_validate(current_user),
    )
