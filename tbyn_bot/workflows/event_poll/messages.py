"""Small user-facing message helpers."""

from __future__ import annotations


USAGE_MESSAGE = "Please include a poll title, e.g. /poll_event Meeting on 6th June"
NON_ADMIN_MESSAGE = "Only group admins can create TBYN event polls."
ADMIN_CHECK_FAILED_MESSAGE = "I could not verify admin permissions. Please try again later."


def user_label(user: dict | None) -> str:
    if not user:
        return ""

    username = user.get("username")
    if username:
        return f"@{username}"

    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")
    full_name = " ".join(part for part in [first_name, last_name] if part).strip()
    return full_name


def mention_prefixed_message(user: dict | None, message: str) -> str:
    label = user_label(user)
    if not label:
        return message
    return f"{label} {message}"
