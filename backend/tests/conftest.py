"""
Shared pytest fixtures for the backend test suite.

Integration tests run against a real PostgreSQL database (see
`docker-compose.yml` / `POSTGRES_*` settings). Each test runs inside a
transaction that is rolled back afterwards, so tests never leak state
into one another and never require manual cleanup.
"""

import asyncio
import sys
import uuid

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models import (  # noqa: F401
    Appointment,
    MedicalReport,
    Notification,
    PatientProfile,
    RefreshToken,
    ReportAnalysis,
    ReportGuidance,
    Role,
    User,
    UserRole,
)
from app.models.enums import RoleName

_test_engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
_TestSessionLocal = async_sessionmaker(bind=_test_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def _prepare_database():
    """Create all tables and seed fixed roles once for the test session."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with _TestSessionLocal() as session:
        result = await session.execute(select(Role))
        existing_names = {r.name for r in result.scalars().all()}
        for role_name in RoleName:
            if role_name.value not in existing_names:
                session.add(
                    Role(id=uuid.uuid4(), name=role_name.value, description=role_name.value)
                )
        await session.commit()

    yield

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _test_engine.dispose()


@pytest.fixture
async def db_session() -> AsyncSession:
    """A DB session bound to a transaction that is rolled back after each test."""
    async with _test_engine.connect() as connection:
        transaction = await connection.begin()
        # `create_savepoint` lets the service layer call session.commit()
        # normally (it operates on a SAVEPOINT) while the outer transaction
        # stays open, so the whole test can always be rolled back at the end.
        session = AsyncSession(
            bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """Async HTTP client wired directly to the FastAPI app, using the
    transactional `db_session` fixture for full test isolation."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None)
