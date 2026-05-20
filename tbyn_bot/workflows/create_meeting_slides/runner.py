"""Create meeting slides workflow runner."""

from __future__ import annotations

import logging
from typing import Callable

from tbyn_bot.config import Config
from tbyn_bot.integrations.meeting_slides import create_meeting_slides_from_template
from tbyn_bot.integrations.telegram import TelegramClient

from .agenda import parse_agenda
from .messages import slides_created_message


CreateSlides = Callable[..., str]


class AgendaParseError(RuntimeError):
    pass


def send_meeting_slides_to_chat(
    config: Config,
    telegram_client: TelegramClient,
    chat_id: int,
    deck_title: str,
    agenda_text: str,
    create_slides: CreateSlides = create_meeting_slides_from_template,
) -> None:
    if config.google_auth_mode != "oauth":
        raise RuntimeError("GOOGLE_AUTH_MODE=oauth is required for meeting slides")
    if config.google_auth_mode == "oauth" and not config.google_oauth_token_file:
        raise RuntimeError("GOOGLE_OAUTH_TOKEN_FILE is required")
    if not config.google_meeting_slides_template_id:
        raise RuntimeError("GOOGLE_MEETING_SLIDES_TEMPLATE_ID is required")
    if not config.google_meeting_slides_folder_id:
        raise RuntimeError("GOOGLE_MEETING_SLIDES_FOLDER_ID is required")

    try:
        slides = parse_agenda(deck_title, agenda_text)
    except ValueError as exc:
        raise AgendaParseError(str(exc)) from exc

    try:
        slides_url = create_slides(
            template_presentation_id=config.google_meeting_slides_template_id,
            output_folder_id=config.google_meeting_slides_folder_id,
            deck_title=deck_title,
            slides=slides,
            auth_mode=config.google_auth_mode,
            oauth_token_file=config.google_oauth_token_file,
        )
    except Exception as exc:
        raise RuntimeError("Failed to create meeting slides") from exc

    telegram_client.send_message(chat_id, slides_created_message(slides_url))


def run_create_meeting_slides(
    config: Config,
    chat_id: int,
    deck_title: str,
    agenda_text: str,
) -> None:
    send_meeting_slides_to_chat(
        config,
        TelegramClient(config.telegram_bot_token),
        chat_id,
        deck_title,
        agenda_text,
    )
    logging.info("Created meeting slides", extra={"chat_id": chat_id})
