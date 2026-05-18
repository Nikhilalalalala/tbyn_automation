"""Telegram update handlers for TBYN workflows."""

from __future__ import annotations

import logging
from typing import Callable

from .commands import parse_poll_event_command
from .messages import (
    ADMIN_CHECK_FAILED_MESSAGE,
    NON_ADMIN_MESSAGE,
    USAGE_MESSAGE,
    mention_prefixed_message,
)
from .permissions import is_admin_status
from .polls import build_event_poll


GROUP_CHAT_TYPES = {"group", "supergroup"}


class EventPollHandler:
    def __init__(
        self,
        client,
        delete_after_seconds: int = 20,
        schedule_delete: Callable | None = None,
    ) -> None:
        self.client = client
        self.delete_after_seconds = delete_after_seconds
        self.schedule_delete = schedule_delete

    def handle_update(self, update: dict) -> bool:
        message = update.get("message") or {}
        text = message.get("text") or ""
        parsed = parse_poll_event_command(text)
        if parsed is None:
            return False

        chat = message.get("chat") or {}
        if chat.get("type") not in GROUP_CHAT_TYPES:
            return True

        chat_id = chat["id"]
        user = message.get("from") or {}
        user_id = user.get("id")
        if user_id is None:
            logging.warning("Poll command ignored because sender user id is missing")
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

        if not parsed.has_argument:
            self._send_temporary_reply(chat_id, user, USAGE_MESSAGE)
            return True

        poll = build_event_poll(parsed.argument)
        self.client.send_poll(chat_id, poll)
        logging.info("Sent event poll", extra={"chat_id": chat_id, "poll_title": parsed.argument})
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
