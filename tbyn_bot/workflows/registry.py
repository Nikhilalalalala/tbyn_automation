"""Workflow registration for the TBYN Telegram bot."""

from __future__ import annotations

from collections.abc import Callable

from tbyn_bot.bot.dispatcher import UpdateHandler
from tbyn_bot.config import Config
from tbyn_bot.workflows.create_meeting_slides import CreateMeetingSlidesHandler
from tbyn_bot.workflows.event_poll import EventPollHandler
from tbyn_bot.workflows.monthly_summary import MonthlySummaryHandler


def build_update_handlers(
    client,
    config: Config,
    delete_after_seconds: int,
    schedule_delete: Callable | None,
) -> list[UpdateHandler]:
    return [
        EventPollHandler(
            client=client,
            delete_after_seconds=delete_after_seconds,
            schedule_delete=schedule_delete,
        ),
        MonthlySummaryHandler(
            client=client,
            config=config,
            delete_after_seconds=delete_after_seconds,
            schedule_delete=schedule_delete,
        ),
        CreateMeetingSlidesHandler(
            client=client,
            config=config,
            delete_after_seconds=delete_after_seconds,
            schedule_delete=schedule_delete,
        ),
    ]
