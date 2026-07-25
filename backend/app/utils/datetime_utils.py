"""Reusable date/time helpers."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)
