"""Shared/base Pydantic schemas reused across feature schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMBaseSchema(BaseModel):
    """Base schema for read models mapped from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class TimestampedSchema(ORMBaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
