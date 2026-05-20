"""User-facing messages for the create meeting slides workflow."""

from __future__ import annotations


USAGE_MESSAGE = (
    "Please include a deck title and agenda, e.g. "
    "/create_meeting_slides TBYN Meeting\n1. Opening"
)
NON_ADMIN_MESSAGE = "Only group admins can create meeting slides."
ADMIN_CHECK_FAILED_MESSAGE = "I could not verify admin permissions. Please try again later."
VALIDATION_ERROR_MESSAGE = "I could not read that agenda. Please check the numbering."
CREATE_ERROR_MESSAGE = "I could not create the slides. Please check the Google setup."


def slides_created_message(slides_url: str) -> str:
    return f"Meeting slides created: {slides_url}"


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
