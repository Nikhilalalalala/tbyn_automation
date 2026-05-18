"""Command parsing for Telegram updates."""

from __future__ import annotations

from dataclasses import dataclass


POLL_EVENT_COMMAND = "/poll_event"
POLL_EVENT_COMMAND_ALIASES = (POLL_EVENT_COMMAND,)


@dataclass(frozen=True)
class ParsedCommand:
    name: str
    argument: str

    @property
    def has_argument(self) -> bool:
        return bool(self.argument)


def parse_poll_event_command(text: str) -> ParsedCommand | None:
    """Parse event poll commands, including Telegram's /cmd@BotName form."""
    return parse_command(text, POLL_EVENT_COMMAND_ALIASES)


def parse_command(text: str, command_names: tuple[str, ...]) -> ParsedCommand | None:
    """Parse a Telegram slash command and preserve the remaining text as one argument."""
    text = (text or "").strip()
    if not text:
        return None

    first_part, _, rest = text.partition(" ")
    command_name = first_part.split("@", 1)[0]
    if command_name not in command_names:
        return None

    return ParsedCommand(name=command_name, argument=rest.strip())
