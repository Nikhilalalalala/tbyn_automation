import unittest

from tbyn_bot.workflows.create_meeting_slides.commands import (
    CREATE_MEETING_SLIDES_COMMAND,
    parse_create_meeting_slides_command,
)


class CreateMeetingSlidesCommandTest(unittest.TestCase):
    def test_parse_command_with_title_and_agenda(self):
        parsed = parse_create_meeting_slides_command(
            "/create_meeting_slides TBYN Meeting May 2026\n1. Opening"
        )

        self.assertEqual(CREATE_MEETING_SLIDES_COMMAND, "/create_meeting_slides")
        self.assertEqual(parsed.deck_title, "TBYN Meeting May 2026")
        self.assertEqual(parsed.agenda_text, "1. Opening")
        self.assertTrue(parsed.has_deck_title)
        self.assertTrue(parsed.has_agenda_text)

    def test_parse_command_without_agenda(self):
        parsed = parse_create_meeting_slides_command(
            "/create_meeting_slides TBYN Meeting May 2026"
        )

        self.assertEqual(parsed.deck_title, "TBYN Meeting May 2026")
        self.assertEqual(parsed.agenda_text, "")
        self.assertTrue(parsed.has_deck_title)
        self.assertFalse(parsed.has_agenda_text)

    def test_parse_command_without_title_but_with_agenda(self):
        parsed = parse_create_meeting_slides_command("/create_meeting_slides\n1. Opening")

        self.assertEqual(parsed.deck_title, "")
        self.assertEqual(parsed.agenda_text, "1. Opening")
        self.assertFalse(parsed.has_deck_title)
        self.assertTrue(parsed.has_agenda_text)

    def test_parse_command_preserves_agenda_text_after_first_newline(self):
        parsed = parse_create_meeting_slides_command(
            "/create_meeting_slides TBYN Meeting May 2026\n   a. Opening\n"
        )

        self.assertEqual(parsed.agenda_text, "   a. Opening\n")

    def test_parse_non_matching_command_returns_none(self):
        self.assertIsNone(parse_create_meeting_slides_command("/events_this_month"))


if __name__ == "__main__":
    unittest.main()
