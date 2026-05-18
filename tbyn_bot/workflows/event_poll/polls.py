"""Poll construction for TBYN workflows."""

from __future__ import annotations

from collections.abc import Callable
import random


YES_OPTION_VARIATIONS = [
    "Yes, I'll be there!",
    "Yes, count me in!",
    "Yes, see you there!",
    "Yes, I'm coming!",
    "Yes, I'll join!",
    "Yes, sounds good!",
    "Yes, I'll make it!",
    "Yes, I'm in!",
    "Yes, happy to join!",
    "Yes, I'll be there :)",
]

NO_OPTION_VARIATIONS = [
    "Sorry, I'll join next time",
    "Sorry, can't make it this time",
    "Sorry, next time for me",
    "Sorry, I'll have to pass",
    "Sorry, I can't join this one",
    "Sorry, maybe the next one",
    "Sorry, not this time",
    "Sorry, I won't be able to make it",
    "Sorry, I'll catch the next one",
    "Sorry, have fun without me",
]


def build_event_poll(
    title: str,
    choose_option: Callable[[list[str]], str] = random.choice,
) -> dict:
    title = title.strip()
    return {
        "question": title,
        "options": [
            choose_option(YES_OPTION_VARIATIONS),
            choose_option(NO_OPTION_VARIATIONS),
        ],
        "is_anonymous": False,
        "allows_multiple_answers": False,
        "type": "regular",
    }
