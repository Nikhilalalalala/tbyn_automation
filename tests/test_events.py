from datetime import date
import unittest

from tbyn_bot.workflows.monthly_summary.events import (
    events_for_month,
    format_monthly_events_summary,
    parse_events_sheet,
)


SAMPLE_ROWS = [
    ["S/N", "Event TItle", "Event Date", "Venue"],
    ["1", "Youth Hangout! - Timeless Tiong Bahru!", "10/1/2026", "The Nest @ TBCC"],
    ["2", "Quarterly Football - January", "10/1/2026", "The Cage Kallang"],
    ["3", "TBYN Retreat 2026", "24/1/2026", "TBC"],
    ["4", "The Perch! - Meet, Mingle, Match", "28/2/2026", "The Nest @ TBCC"],
    ["5", "Fun Times! - March", "14/3/2026", "Science Centre Omni-Theatre"],
    ["6", "Earth & Us! - Thrift, Trade, Transform", "28/3/2026", "The Nest @ TBCC"],
    ["7", "Board Game Afternoon", "29/3/2026", "The Nest @ TBCC"],
    ["8", "Quarterly Football - April", "11/4/2026", "The Cage Kallang"],
    ["9", "Story Alive! 2026 - Prelims", "18/4/2026", "Tiong Bahru CC"],
]


class EventsTest(unittest.TestCase):
    def test_parses_sheet_rows(self):
        events = parse_events_sheet(SAMPLE_ROWS)

        self.assertEqual(len(events), 9)
        self.assertEqual(events[4].title, "Fun Times! - March")
        self.assertEqual(events[4].event_date, date(2026, 3, 14))
        self.assertEqual(events[4].venue, "Science Centre Omni-Theatre")

    def test_filters_events_for_current_month(self):
        events = parse_events_sheet(SAMPLE_ROWS)

        march_events = events_for_month(events, today=date(2026, 3, 1))

        self.assertEqual([event.title for event in march_events], [
            "Fun Times! - March",
            "Earth & Us! - Thrift, Trade, Transform",
            "Board Game Afternoon",
        ])

    def test_formats_monthly_summary(self):
        events = parse_events_sheet(SAMPLE_ROWS)
        march_events = events_for_month(events, today=date(2026, 3, 1))

        message = format_monthly_events_summary(march_events)

        self.assertEqual(
            message,
            "\n".join(
                [
                    "Whats happening this month:",
                    "1. Fun Times! - March @ Science Centre Omni-Theatre - 14/3/2026",
                    "2. Earth & Us! - Thrift, Trade, Transform @ The Nest @ TBCC - 28/3/2026",
                    "3. Board Game Afternoon @ The Nest @ TBCC - 29/3/2026",
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
