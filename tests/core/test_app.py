import unittest
from unittest.mock import patch

from tbyn_bot.app import run
from tbyn_bot.bot_commands import BOT_COMMANDS
from tbyn_bot.config import Config


class FakeTelegramClient:
    last_instance = None

    def __init__(self, token):
        self.token = token
        self.commands = None
        FakeTelegramClient.last_instance = self

    def set_my_commands(self, commands):
        self.commands = commands
        return True

    def get_updates(self, offset=None, timeout=30):
        raise KeyboardInterrupt


class AppStartupTest(unittest.TestCase):
    def test_registers_bot_commands_before_polling(self):
        config = Config(telegram_bot_token="token")

        with (
            patch("tbyn_bot.app.TelegramClient", FakeTelegramClient),
            patch("tbyn_bot.app.build_update_handlers", return_value=[]),
        ):
            with self.assertRaises(KeyboardInterrupt):
                run(config)

        self.assertEqual(FakeTelegramClient.last_instance.commands, BOT_COMMANDS)


if __name__ == "__main__":
    unittest.main()
