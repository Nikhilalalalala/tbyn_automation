from datetime import date
import unittest

from tbyn_bot.workflows.monthly_summary import build_monthly_summary_message


class MonthlySummaryTest(unittest.TestCase):
    def test_builds_summary_message_for_current_month(self):
        rows = [
            ["S/N", "Event TItle", "Event Date", "Venue"],
            ["5", "Fun Times! - March", "14/3/2026", "Science Centre Omni-Theatre"],
            ["6", "Earth & Us! - Thrift, Trade, Transform", "28/3/2026", "The Nest @ TBCC"],
            ["8", "Quarterly Football - April", "11/4/2026", "The Cage Kallang"],
        ]

        message = build_monthly_summary_message(rows, today=date(2026, 3, 1))

        self.assertEqual(
            message,
            "\n".join(
                [
                    "Whats happening this month:",
                    "1. Fun Times! - March @ Science Centre Omni-Theatre - 14/3/2026",
                    "2. Earth & Us! - Thrift, Trade, Transform @ The Nest @ TBCC - 28/3/2026",
                ]
            ),
        )


if __name__ == "__main__":
    unittest.main()
