"""Telegram command handler for monthly event summaries."""

from __future__ import annotations

from collections.abc import Callable
import logging

from tbyn_bot.bot.permissions import is_admin_status
from tbyn_bot.config import Config

from .commands import is_monthly_summary_command
from .messages import (
    ADMIN_CHECK_FAILED_MESSAGE,
    CONFIG_ERROR_MESSAGE,
    NON_ADMIN_MESSAGE,
    SEND_ERROR_MESSAGE,
    mention_prefixed_message,
)
from .runner import send_monthly_summary_to_chat


GROUP_CHAT_TYPES = {"group", "supergroup"}


class MonthlySummaryHandler:
    def __init__(
        self,
        client,
        config: Config,
        delete_after_seconds: int = 20,
        schedule_delete: Callable | None = None,
        send_summary: Callable | None = None,
    ) -> None:
        self.client = client
        self.config = config
        self.delete_after_seconds = delete_after_seconds
        self.schedule_delete = schedule_delete
        self.send_summary = send_summary or send_monthly_summary_to_chat

    def handle_update(self, update: dict) -> bool:
        message = update.get("message") or {}
        text = message.get("text") or ""
        if not is_monthly_summary_command(text):
            return False

        chat = message.get("chat") or {}
        if chat.get("type") not in GROUP_CHAT_TYPES:
            return True

        chat_id = chat["id"]
        user = message.get("from") or {}
        user_id = user.get("id")
        if user_id is None:
            logging.warning("Monthly summary command ignored because sender user id is missing")
            return True

        try:
            is_group_admin = self._is_group_admin(chat_id, user_id)
        except Exception:
            logging.exception("Failed to verify Telegram admin status")
            self._send_temporary_reply(chat_id, user, ADMIN_CHECK_FAILED_MESSAGE)
            return True

        if not is_group_admin:
            self._send_temporary_reply(chat_id, user, NON_ADMIN_MESSAGE)
            return True

        try:
            self.send_summary(self.config, self.client, chat_id)
        except RuntimeError:
            logging.exception("Monthly summary configuration error")
            self._send_temporary_reply(chat_id, user, CONFIG_ERROR_MESSAGE)
            return True
        except Exception:
            logging.exception("Failed to send monthly summary")
            self._send_temporary_reply(chat_id, user, SEND_ERROR_MESSAGE)
            return True

        logging.info("Sent monthly event summary", extra={"chat_id": chat_id})
        return True

    def _is_group_admin(self, chat_id: int, user_id: int) -> bool:
        member = self.client.get_chat_member(chat_id, user_id)
        return is_admin_status(member.get("status"))

    def _send_temporary_reply(self, chat_id: int, user: dict, message: str) -> None:
        sent_message = self.client.send_message(chat_id, mention_prefixed_message(user, message))
        message_id = sent_message.get("message_id")
        if message_id is None or self.schedule_delete is None:
            return

        self.schedule_delete(
            self.client,
            chat_id,
            message_id,
            self.delete_after_seconds,
        )
