"""
Aggregates all v1 endpoint routers into a single APIRouter.

New feature routers (auth, patients, reports, agents, ...) should be
imported and included here as they are implemented — this file is the
single place that assembles the v1 API surface.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, users

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)

# Future routers will be registered here, e.g.:
# api_router.include_router(patients.router)
# api_router.include_router(reports.router)
