"""User-facing messages for the monthly summary workflow."""

from __future__ import annotations


NON_ADMIN_MESSAGE = "Only group admins can send the monthly event summary."
ADMIN_CHECK_FAILED_MESSAGE = "I could not verify admin permissions. Please try again later."
CONFIG_ERROR_MESSAGE = "Monthly summary is not configured yet. Please check the Google Sheet settings."
SEND_ERROR_MESSAGE = "I could not send the monthly summary. Please try again later."


def user_label(user: dict | None) -> str:
    if not user:
        return ""

    username = user.get("username")
    if username:
        return f"@{username}"

    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")
    return " ".join(part for part in [first_name, last_name] if part).strip()


def mention_prefixed_message(user: dict | None, message: str) -> str:
    label = user_label(user)
    if not label:
        return message
    return f"{label} {message}"

