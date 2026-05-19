"""Command parsing for the monthly summary workflow."""

from __future__ import annotations


MONTHLY_SUMMARY_COMMAND = "/monthly_summary"


def is_monthly_summary_command(text: str) -> bool:
    text = (text or "").strip()
    if not text:
        return False

    first_part = text.partition(" ")[0]
    command_name = first_part.split("@", 1)[0]
    return command_name == MONTHLY_SUMMARY_COMMAND

