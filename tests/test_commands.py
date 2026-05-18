import unittest

from tbyn_bot.workflows.event_poll.commands import POLL_EVENT_COMMAND, parse_poll_event_command


class ParsePollEventCommandTest(unittest.TestCase):
    def test_parses_event_title_with_spaces(self):
        parsed = parse_poll_event_command("/poll_event Meeting on 6th June")

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.name, POLL_EVENT_COMMAND)
        self.assertEqual(parsed.argument, "Meeting on 6th June")

    def test_parses_telegram_bot_command_suffix(self):
        parsed = parse_poll_event_command("/poll_event@TBYNBot Meeting on 6th June")

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.argument, "Meeting on 6th June")

    def test_returns_command_with_empty_argument(self):
        parsed = parse_poll_event_command("/poll_event")

        self.assertIsNotNone(parsed)
        self.assertFalse(parsed.has_argument)

    def test_rejects_partial_command_name(self):
        self.assertIsNone(parse_poll_event_command("/poll_event_extra Meeting on 6th June"))

    def test_ignores_other_commands(self):
        self.assertIsNone(parse_poll_event_command("/start"))


if __name__ == "__main__":
    unittest.main()
