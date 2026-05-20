import unittest

from tbyn_bot.bot_commands import BOT_COMMANDS, register_bot_commands
from tbyn_bot.workflows.create_meeting_slides import CREATE_MEETING_SLIDES_COMMAND
from tbyn_bot.workflows.event_poll import POLL_EVENT_COMMAND
from tbyn_bot.workflows.monthly_summary import MONTHLY_SUMMARY_COMMAND


class FakeTelegramClient:
    def __init__(self):
        self.commands = None

    def set_my_commands(self, commands):
        self.commands = commands
        return True


class BotCommandsTest(unittest.TestCase):
    def test_commands_are_telegram_menu_compatible(self):
        self.assertEqual(
            BOT_COMMANDS,
            [
                {
                    "command": POLL_EVENT_COMMAND.removeprefix("/"),
                    "description": "Create an event attendance poll",
                },
                {
                    "command": MONTHLY_SUMMARY_COMMAND.removeprefix("/"),
                    "description": "Send this month's event summary",
                },
                {
                    "command": CREATE_MEETING_SLIDES_COMMAND.removeprefix("/"),
                    "description": "Create meeting slides from an agenda",
                },
            ],
        )

        for command in BOT_COMMANDS:
            self.assertNotIn("/", command["command"])
            self.assertLessEqual(len(command["command"]), 32)

    def test_registers_commands_with_client(self):
        client = FakeTelegramClient()

        self.assertTrue(register_bot_commands(client))
        self.assertEqual(client.commands, BOT_COMMANDS)


if __name__ == "__main__":
    unittest.main()
