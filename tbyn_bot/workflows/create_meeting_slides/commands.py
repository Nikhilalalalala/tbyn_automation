"""Command parsing for the create meeting slides workflow."""

from __future__ import annotations

from dataclasses import dataclass
import re


CREATE_MEETING_SLIDES_COMMAND = "/create_meeting_slides"


@dataclass(frozen=True)
class ParsedCreateMeetingSlidesCommand:
    deck_title: str
    agenda_text: str

    @property
    def has_deck_title(self) -> bool:
        return bool(self.deck_title)

    @property
    def has_agenda_text(self) -> bool:
        return bool(self.agenda_text)


def parse_create_meeting_slides_command(
    text: str,
) -> ParsedCreateMeetingSlidesCommand | None:
    """Parse /create_meeting_slides into a deck title and agenda text."""
    text = (text or "").lstrip()
    if not text.strip():
        return None

    first_part, separator_match, rest = _partition_first_whitespace(text)
    command_name = first_part.split("@", 1)[0]
    if command_name != CREATE_MEETING_SLIDES_COMMAND:
        return None

    if separator_match == "\n":
        deck_title = ""
        agenda_text = rest
    else:
        deck_title, has_agenda_separator, agenda_text = rest.partition("\n")
        if not has_agenda_separator:
            agenda_text = ""

    return ParsedCreateMeetingSlidesCommand(
        deck_title=deck_title.strip(),
        agenda_text=agenda_text,
    )


def _partition_first_whitespace(text: str) -> tuple[str, str, str]:
    match = re.search(r"\s", text)
    if match is None:
        return text, "", ""

    first_part = text[: match.start()]
    separator = text[match.start()]
    rest = text[match.end() :]
    if separator != "\n":
        rest = rest.lstrip(" \t")
    return first_part, separator, rest
