"""Telegram command handler for creating meeting slides."""

from __future__ import annotations

from collections.abc import Callable
import logging

from tbyn_bot.bot.permissions import is_admin_status
from tbyn_bot.config import Config

from .commands import parse_create_meeting_slides_command
from .messages import (
    ADMIN_CHECK_FAILED_MESSAGE,
    CREATE_ERROR_MESSAGE,
    NON_ADMIN_MESSAGE,
    USAGE_MESSAGE,
    VALIDATION_ERROR_MESSAGE,
    mention_prefixed_message,
)
from .runner import AgendaParseError, send_meeting_slides_to_chat


GROUP_CHAT_TYPES = {"group", "supergroup"}


class CreateMeetingSlidesHandler:
    def __init__(
        self,
        client,
        config: Config,
        delete_after_seconds: int = 20,
        schedule_delete: Callable | None = None,
        send_slides: Callable | None = None,
    ) -> None:
        self.client = client
        self.config = config
        self.delete_after_seconds = delete_after_seconds
        self.schedule_delete = schedule_delete
        self.send_slides = send_slides or send_meeting_slides_to_chat

    def handle_update(self, update: dict) -> bool:
        message = update.get("message") or {}
        text = message.get("text") or ""
        parsed = parse_create_meeting_slides_command(text)
        if parsed is None:
            return False

        chat = message.get("chat") or {}
        if chat.get("type") not in GROUP_CHAT_TYPES:
            return True

        chat_id = chat["id"]
        user = message.get("from") or {}
        user_id = user.get("id")
        if user_id is None:
            logging.warning("Create meeting slides command ignored because sender user id is missing")
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

        if not parsed.has_deck_title or not parsed.has_agenda_text:
            self._send_temporary_reply(chat_id, user, USAGE_MESSAGE)
            return True

        try:
            self.send_slides(
                self.config,
                self.client,
                chat_id,
                parsed.deck_title,
                parsed.agenda_text,
            )
        except AgendaParseError:
            logging.info("Invalid meeting slides agenda", extra={"chat_id": chat_id})
            self._send_temporary_reply(chat_id, user, VALIDATION_ERROR_MESSAGE)
            return True
        except Exception:
            logging.exception("Failed to create meeting slides")
            self._send_temporary_reply(chat_id, user, CREATE_ERROR_MESSAGE)
            return True

        logging.info("Created meeting slides", extra={"chat_id": chat_id})
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
