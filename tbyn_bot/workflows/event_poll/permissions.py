"""Permission helpers."""

from __future__ import annotations


ADMIN_STATUSES = {"creator", "administrator"}


def is_admin_status(status: str | None) -> bool:
    return status in ADMIN_STATUSES
