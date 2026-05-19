"""Application startup and polling loop."""

from __future__ import annotations

import logging
import time

from .config import Config
from .bot.dispatcher import UpdateDispatcher
from .integrations.telegram import TelegramClient
from .utils.cleanup import schedule_delete_message
from .workflows import build_update_handlers


def run(config: Config) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    client = TelegramClient(config.telegram_bot_token)
    dispatcher = UpdateDispatcher(
        build_update_handlers(
            client=client,
            config=config,
            delete_after_seconds=config.validation_delete_after_seconds,
            schedule_delete=schedule_delete_message,
        )
    )

    offset: int | None = None
    logging.info("TBYN Telegram poll bot started")

    while True:
        try:
            updates = client.get_updates(offset=offset, timeout=config.polling_timeout_seconds)
        except Exception:
            logging.exception("Failed to fetch Telegram updates")
            time.sleep(5)
            continue

        for update in updates:
            offset = update["update_id"] + 1
            try:
                dispatcher.handle_update(update)
            except Exception:
                logging.exception("Failed to handle Telegram update")
