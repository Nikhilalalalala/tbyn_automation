"""Delayed cleanup helpers."""

from __future__ import annotations

import logging
from threading import Timer


def schedule_delete_message(client, chat_id: int, message_id: int, delay_seconds: int) -> None:
    def delete_later() -> None:
        try:
            client.delete_message(chat_id, message_id)
        except Exception:
            logging.exception("Failed to delete temporary bot message")

    timer = Timer(delay_seconds, delete_later)
    timer.daemon = True
    timer.start()
