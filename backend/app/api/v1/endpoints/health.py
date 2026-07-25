"""Health check endpoint — used by Docker, load balancers, and CI/CD probes."""

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.common.constants import ApiTags
from app.common.responses import BaseResponse
from app.core.config import settings
from app.database import get_db

router = APIRouter(prefix="/health", tags=[ApiTags.HEALTH])


@router.get("", response_model=BaseResponse[dict], summary="Liveness check")
async def health_check() -> BaseResponse[dict]:
    """Basic liveness probe — confirms the API process is up."""
    return BaseResponse(
        message="OncoNexus AI backend is running.",
        data={
            "service": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "environment": settings.ENVIRONMENT,
        },
    )


@router.get("/readiness", response_model=BaseResponse[dict], summary="Readiness check")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> BaseResponse[dict]:
    """Readiness probe — confirms the API can reach its database."""
    await db.execute(text("SELECT 1"))
    return BaseResponse(
        message="OncoNexus AI backend is ready.",
        data={"database": "connected"},
    )
