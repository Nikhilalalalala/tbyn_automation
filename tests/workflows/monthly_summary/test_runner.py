import unittest

from tbyn_bot.config import Config
from tbyn_bot.workflows.monthly_summary.runner import send_monthly_summary_to_chat

from tests.fakes import FakeTelegramClient


def config(**overrides):
    values = {
        "telegram_bot_token": "token",
        "google_auth_mode": "oauth",
        "google_oauth_token_file": "google-oauth-token.json",
        "google_sheet_id": "sheet-id",
        "google_events_range": "Events!A:D",
    }
    values.update(overrides)
    return Config(**values)


class MonthlySummaryRunnerTest(unittest.TestCase):
    def test_oauth_requires_token_file(self):
        with self.assertRaisesRegex(RuntimeError, "GOOGLE_OAUTH_TOKEN_FILE"):
            send_monthly_summary_to_chat(
                config(google_oauth_token_file=""),
                FakeTelegramClient(),
                -1001,
            )

    def test_service_account_auth_mode_is_rejected_for_monthly_summary(self):
        with self.assertRaisesRegex(RuntimeError, "GOOGLE_AUTH_MODE=oauth"):
            send_monthly_summary_to_chat(
                config(google_auth_mode="service_account"),
                FakeTelegramClient(),
                -1001,
            )

    def test_success_reads_sheet_with_oauth_token_and_sends_summary(self):
        client = FakeTelegramClient()
        read_calls = []

        def read_values(**kwargs):
            read_calls.append(kwargs)
            return [
                ["S/N", "Event TItle", "Event Date", "Venue"],
                ["1", "Opening", "1/5/2026", "TBYN"],
            ]

        send_monthly_summary_to_chat(
            config(),
            client,
            -1001,
            read_values=read_values,
        )

        self.assertEqual(
            read_calls,
            [
                {
                    "spreadsheet_id": "sheet-id",
                    "cell_range": "Events!A:D",
                    "oauth_token_file": "google-oauth-token.json",
                }
            ],
        )
        self.assertEqual(
            client.sent_messages,
            [(-1001, "Whats happening this month:\n1. Opening @ TBYN - 1/5/2026")],
        )


if __name__ == "__main__":
    unittest.main()
