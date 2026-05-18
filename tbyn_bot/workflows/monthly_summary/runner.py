"""Monthly event summary workflow."""

from __future__ import annotations

from datetime import date
import logging

from tbyn_bot.config import Config, load_config
from tbyn_bot.integrations.google_sheets import read_sheet_values
from tbyn_bot.integrations.telegram import TelegramClient

from .events import events_for_month, format_monthly_events_summary, parse_events_sheet


def build_monthly_summary_message(rows: list[list[str]], today: date | None = None) -> str:
    today = today or date.today()
    events = parse_events_sheet(rows)
    monthly_events = events_for_month(events, today)
    return format_monthly_events_summary(monthly_events)


def run_monthly_summary(config: Config, today: date | None = None) -> None:
    if not config.monthly_summary_chat_id:
        raise RuntimeError("MONTHLY_SUMMARY_CHAT_ID is required")
    if not config.google_sheet_id:
        raise RuntimeError("GOOGLE_SHEET_ID is required")
    if not config.google_service_account_file:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_FILE is required")

    rows = read_sheet_values(
        spreadsheet_id=config.google_sheet_id,
        cell_range=config.google_events_range,
        service_account_file=config.google_service_account_file,
    )
    message = build_monthly_summary_message(rows, today=today)
    TelegramClient(config.telegram_bot_token).send_message(
        int(config.monthly_summary_chat_id),
        message,
    )
    logging.info("Sent monthly event summary")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_monthly_summary(load_config())


if __name__ == "__main__":
    main()
