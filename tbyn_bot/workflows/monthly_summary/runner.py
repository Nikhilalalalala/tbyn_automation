"""Monthly event summary workflow."""

from __future__ import annotations

from datetime import date
import logging
from typing import Callable

from tbyn_bot.config import Config, load_config
from tbyn_bot.integrations.google_sheets import read_sheet_values
from tbyn_bot.integrations.telegram import TelegramClient

from .events import events_for_month, format_monthly_events_summary, parse_events_sheet


def build_monthly_summary_message(rows: list[list[str]], today: date | None = None) -> str:
    today = today or date.today()
    events = parse_events_sheet(rows)
    monthly_events = events_for_month(events, today)
    return format_monthly_events_summary(monthly_events)


def send_monthly_summary_to_chat(
    config: Config,
    telegram_client: TelegramClient,
    chat_id: int,
    today: date | None = None,
    read_values: Callable[[str, str, str], list[list[str]]] = read_sheet_values,
) -> None:
    if not config.google_sheet_id:
        raise RuntimeError("GOOGLE_SHEET_ID is required")
    if not config.google_service_account_file:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_FILE is required")

    rows = read_values(
        spreadsheet_id=config.google_sheet_id,
        cell_range=config.google_events_range,
        service_account_file=config.google_service_account_file,
    )
    message = build_monthly_summary_message(rows, today=today)
    telegram_client.send_message(chat_id, message)


def run_monthly_summary(config: Config, chat_id: int, today: date | None = None) -> None:
    send_monthly_summary_to_chat(
        config,
        TelegramClient(config.telegram_bot_token),
        chat_id,
        today=today,
    )
    logging.info("Sent monthly event summary", extra={"chat_id": chat_id})


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    raise RuntimeError("Monthly summary now runs from Telegram with /monthly_summary")


if __name__ == "__main__":
    main()
