"""Register Telegram command suggestions for the bot."""

from __future__ import annotations

import logging

from tbyn_bot.config import load_config
from tbyn_bot.integrations.telegram import TelegramClient
from tbyn_bot.workflows.event_poll import POLL_EVENT_COMMAND
from tbyn_bot.workflows.monthly_summary import MONTHLY_SUMMARY_COMMAND


BOT_COMMANDS = [
    {
        "command": POLL_EVENT_COMMAND.removeprefix("/"),
        "description": "Create an event attendance poll",
    },
    {
        "command": MONTHLY_SUMMARY_COMMAND.removeprefix("/"),
        "description": "Send this month's event summary",
    },
]


def register_bot_commands(client: TelegramClient) -> bool:
    return client.set_my_commands(BOT_COMMANDS)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = load_config()
    register_bot_commands(TelegramClient(config.telegram_bot_token))
    logging.info("Registered Telegram bot commands")


if __name__ == "__main__":
    main()
