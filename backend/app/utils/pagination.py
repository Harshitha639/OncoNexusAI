"""Reusable pagination helpers shared across list endpoints."""

import math

from app.common.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.common.responses import PaginationMeta


def normalize_pagination(page: int, page_size: int) -> tuple[int, int]:
    """Clamp page/page_size to sane bounds."""
    page = max(page, 1)
    page_size = min(max(page_size, 1), MAX_PAGE_SIZE) or DEFAULT_PAGE_SIZE
    return page, page_size


def build_pagination_meta(total: int, page: int, page_size: int) -> PaginationMeta:
    total_pages = math.ceil(total / page_size) if page_size else 0
    return PaginationMeta(total=total, page=page, page_size=page_size, total_pages=total_pages)
