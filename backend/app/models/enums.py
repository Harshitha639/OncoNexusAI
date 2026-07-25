"""Shared enumerations used across ORM models and schemas."""

import enum


class RoleName(str, enum.Enum):
    """Fixed set of platform roles. Stored as the `roles.name` value."""

    PATIENT = "patient"
    DOCTOR = "doctor"
    CAREGIVER = "caregiver"
    ADMIN = "admin"
