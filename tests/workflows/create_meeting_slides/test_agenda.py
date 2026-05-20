import unittest

from tbyn_bot.workflows.create_meeting_slides.agenda import (
    CONTENT_BODY_PREFILL,
    SlideKind,
    parse_agenda,
)


class CreateMeetingSlidesAgendaTest(unittest.TestCase):
    def test_parse_agenda_builds_opening_and_items(self):
        slides = parse_agenda(
            "TBYN Meeting May 2026",
            "1. Confirmation\n\n2. Updates\n   a. Bahru Mania!\n   ii. Bank Signatories",
        )

        self.assertEqual(
            [slide.kind for slide in slides],
            [
                SlideKind.MEETING_TITLE,
                SlideKind.AGENDA_TITLE,
                SlideKind.AGENDA_TITLE,
                SlideKind.AGENDA_ITEM,
                SlideKind.AGENDA_ITEM,
            ],
        )
        self.assertEqual(slides[0].title, "TBYN Meeting May 2026")
        self.assertEqual(slides[1].title, "Confirmation")
        self.assertEqual(slides[3].title, "Bahru Mania!")
        self.assertEqual(slides[3].body, CONTENT_BODY_PREFILL)

    def test_invalid_line_reports_line_number_and_text(self):
        with self.assertRaises(ValueError) as context:
            parse_agenda("Deck", "1. Good\nThis is invalid")

        self.assertIn("line 2", str(context.exception))
        self.assertIn("This is invalid", str(context.exception))


if __name__ == "__main__":
    unittest.main()
