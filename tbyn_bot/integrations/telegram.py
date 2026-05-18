"""Minimal Telegram Bot API client using only the Python standard library."""

from __future__ import annotations

import json
from typing import Any
from urllib import request, error


class TelegramApiError(RuntimeError):
    pass


class TelegramClient:
    def __init__(self, token: str) -> None:
        self.base_url = f"https://api.telegram.org/bot{token}"

    def get_updates(self, offset: int | None = None, timeout: int = 30) -> list[dict]:
        payload: dict[str, Any] = {"timeout": timeout}
        if offset is not None:
            payload["offset"] = offset
        return self._call("getUpdates", payload)

    def get_chat_member(self, chat_id: int, user_id: int) -> dict:
        return self._call("getChatMember", {"chat_id": chat_id, "user_id": user_id})

    def send_poll(self, chat_id: int, poll: dict) -> dict:
        payload = {"chat_id": chat_id, **poll}
        return self._call("sendPoll", payload)

    def send_message(self, chat_id: int, text: str) -> dict:
        return self._call("sendMessage", {"chat_id": chat_id, "text": text})

    def delete_message(self, chat_id: int, message_id: int) -> dict:
        return self._call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    def _call(self, method: str, payload: dict) -> Any:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/{method}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise TelegramApiError(f"Telegram API HTTP error for {method}: {details}") from exc
        except error.URLError as exc:
            raise TelegramApiError(f"Telegram API network error for {method}: {exc.reason}") from exc

        if not data.get("ok"):
            description = data.get("description", "Unknown Telegram API error")
            raise TelegramApiError(f"Telegram API error for {method}: {description}")

        return data.get("result")
