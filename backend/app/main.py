"""
Application entrypoint and FastAPI app factory.

Run locally with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.exceptions.handlers import register_exception_handlers
from app.middleware import RequestLoggingMiddleware

configure_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Application factory — builds and configures the FastAPI instance."""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ------------------------------------------------------------------
    # Middleware (order matters: outermost registered last is run first)
    # ------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    # ------------------------------------------------------------------
    # Exception handling
    # ------------------------------------------------------------------
    register_exception_handlers(app)

    # ------------------------------------------------------------------
    # Routing (versioned)
    # ------------------------------------------------------------------
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # ------------------------------------------------------------------
    # Swagger / OpenAPI customization
    # ------------------------------------------------------------------
    def custom_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=settings.PROJECT_NAME,
            version=settings.PROJECT_VERSION,
            description=settings.PROJECT_DESCRIPTION,
            routes=app.routes,
        )
        schema["info"]["x-logo"] = {"url": "https://placehold.co/200x60?text=OncoNexus+AI"}
        schema["components"]["securitySchemes"] = {
            "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        }
        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info(
            "%s v%s starting up in '%s' mode",
            settings.PROJECT_NAME,
            settings.PROJECT_VERSION,
            settings.ENVIRONMENT,
        )

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("%s shutting down.", settings.PROJECT_NAME)

    return app


app = create_app()
