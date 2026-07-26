"""Patient dashboard endpoint — a single aggregate summary payload."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_roles
from app.common.constants import ApiTags
from app.common.responses import BaseResponse
from app.database import get_db
from app.models.enums import RoleName
from app.models.user import User
from app.schemas.dashboard import DashboardSummarySchema
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=[ApiTags.DASHBOARD])


@router.get(
    "",
    response_model=BaseResponse[DashboardSummarySchema],
    status_code=status.HTTP_200_OK,
    summary="Get the current patient's dashboard summary",
)
async def get_dashboard(
    current_user: User = Depends(require_roles(RoleName.PATIENT)),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[DashboardSummarySchema]:
    """Welcome info, profile completion, recent reports, latest AI summary,
    latest risk score, upcoming appointments, and unread notification count."""
    service = DashboardService(db)
    summary = await service.get_summary(current_user)
    return BaseResponse(message="Dashboard summary retrieved successfully.", data=summary)
