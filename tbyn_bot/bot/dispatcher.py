"""Update dispatching for Telegram workflows."""

from __future__ import annotations

from typing import Protocol


class UpdateHandler(Protocol):
    def handle_update(self, update: dict) -> bool:
        """Handle an update and return whether this handler consumed it."""


class UpdateDispatcher:
    def __init__(self, handlers: list[UpdateHandler]) -> None:
        self.handlers = handlers

    def handle_update(self, update: dict) -> bool:
        for handler in self.handlers:
            if handler.handle_update(update):
                return True
        return False

