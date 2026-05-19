"""Event parsing and monthly summary formatting."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import re


@dataclass(frozen=True)
class Event:
    serial_number: str
    title: str
    event_date: date
    date_text: str
    venue: str


def parse_events_sheet(rows: list[list[str]]) -> list[Event]:
    if not rows:
        return []

    header_row_index, header_indexes = _find_header_row(rows)
    events: list[Event] = []

    for row in rows[header_row_index + 1:]:
        if not any(cell.strip() for cell in row if isinstance(cell, str)):
            continue

        title = _cell(row, header_indexes["event_title"])
        date_text = _cell(row, header_indexes["event_date"])
        venue = _cell(row, header_indexes["venue"])

        if not title or not date_text:
            continue

        events.append(
            Event(
                serial_number=_cell(row, header_indexes["serial_number"]),
                title=title,
                event_date=parse_event_date(date_text),
                date_text=date_text,
                venue=venue,
            )
        )

    return events


def _find_header_row(rows: list[list[str]]) -> tuple[int, dict[str, int]]:
    for index, row in enumerate(rows):
        header_indexes = _header_indexes(row, raise_on_missing=False)
        if header_indexes is not None:
            return index, header_indexes

    raise ValueError(
        "Missing required event sheet columns: serial_number, event_title, event_date, venue"
    )


def parse_event_date(value: str) -> date:
    value = value.strip()
    for date_format in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue

    raise ValueError(f"Unsupported event date format: {value}")


def events_for_month(events: list[Event], today: date) -> list[Event]:
    return sorted(
        [
            event
            for event in events
            if event.event_date.year == today.year and event.event_date.month == today.month
        ],
        key=lambda event: event.event_date,
    )


def format_monthly_events_summary(events: list[Event]) -> str:
    if not events:
        return "Whats happening this month:\nNo events listed for this month yet."

    lines = ["Whats happening this month:"]
    for index, event in enumerate(events, start=1):
        lines.append(f"{index}. {event.title} @ {event.venue} - {event.date_text}")

    return "\n".join(lines)


def _header_indexes(header: list[str], raise_on_missing: bool = True) -> dict[str, int] | None:
    normalized = {_normalize_header(value): index for index, value in enumerate(header)}

    required = {
        "serial_number": "sn",
        "event_title": "eventtitle",
        "event_date": "eventdate",
        "venue": "venue",
    }

    missing = [label for label, key in required.items() if key not in normalized]
    if missing:
        if not raise_on_missing:
            return None
        raise ValueError(f"Missing required event sheet columns: {', '.join(missing)}")

    return {label: normalized[key] for label, key in required.items()}


def _normalize_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _cell(row: list[str], index: int) -> str:
    if index >= len(row):
        return ""
    return str(row[index]).strip()
