"""Agenda parsing for the create meeting slides workflow."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


CONTENT_BODY_PREFILL = "Date:\nTime:\nVenue:"


class SlideKind(Enum):
    MEETING_TITLE = "meeting_title"
    AGENDA_TITLE = "agenda_title"
    AGENDA_ITEM = "agenda_item"


@dataclass(frozen=True)
class SlidePlan:
    kind: SlideKind
    title: str
    body: str = ""


NUMBERED_LINE_RE = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")
SUB_ITEM_LINE_RE = re.compile(r"^\s*([A-Za-z]|[ivxlcdmIVXLCDM]+)\.\s+(.+?)\s*$")


def parse_agenda(deck_title: str, agenda_text: str) -> list[SlidePlan]:
    """Build slide plans from a deck title and agenda text."""
    slides = [SlidePlan(kind=SlideKind.MEETING_TITLE, title=deck_title)]

    for line_number, line in enumerate((agenda_text or "").splitlines(), start=1):
        if not line.strip():
            continue

        numbered_match = NUMBERED_LINE_RE.match(line)
        if numbered_match:
            slides.append(
                SlidePlan(
                    kind=SlideKind.AGENDA_TITLE,
                    title=numbered_match.group(2),
                )
            )
            continue

        sub_item_match = SUB_ITEM_LINE_RE.match(line)
        if sub_item_match:
            slides.append(
                SlidePlan(
                    kind=SlideKind.AGENDA_ITEM,
                    title=sub_item_match.group(2),
                    body=CONTENT_BODY_PREFILL,
                )
            )
            continue

        raise ValueError(f"Invalid agenda line {line_number}: {line}")

    return slides
