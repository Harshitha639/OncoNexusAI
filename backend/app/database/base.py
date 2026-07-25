"""
Declarative base class shared by all ORM models.

Alembic's `env.py` imports `Base.metadata` from here, and every model
in `app.models` must inherit from `Base` so migrations can detect it.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy ORM models."""

    pass
