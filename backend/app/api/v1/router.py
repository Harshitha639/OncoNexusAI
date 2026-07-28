"""
Aggregates all v1 endpoint routers into a single APIRouter.

New feature routers (auth, patients, reports, agents, ...) should be
imported and included here as they are implemented — this file is the
single place that assembles the v1 API surface.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    appointments,
    auth,
    dashboard,
    guidance,
    health,
    notifications,
    patient_profile,
    reports,
    users,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(patient_profile.router)
api_router.include_router(reports.router)
api_router.include_router(guidance.router)
api_router.include_router(appointments.router)
api_router.include_router(notifications.router)
api_router.include_router(dashboard.router)

# Future routers will be registered here (Phase 4+): doctor portal, caregiver
# portal, chatbot, nutrition, rehabilitation, analytics.
