import unittest

from tbyn_bot.config import Config
from tbyn_bot.workflows.event_poll import POLL_EVENT_COMMAND
from tbyn_bot.workflows.monthly_summary import MONTHLY_SUMMARY_COMMAND, MonthlySummaryHandler

from tests.fakes import FakeTelegramClient, group_update


def config():
    return Config(
        telegram_bot_token="token",
        google_sheet_id="sheet-id",
        google_auth_mode="oauth",
        google_oauth_token_file="google-oauth-token.json",
    )


class MonthlySummaryHandlerTest(unittest.TestCase):
    def test_admin_command_sends_summary_to_same_group(self):
        client = FakeTelegramClient(admin_status="creator")
        calls = []

        def send_summary(config, telegram_client, chat_id):
            calls.append((config, telegram_client, chat_id))

        handler = MonthlySummaryHandler(client, config(), send_summary=send_summary)

        handled = handler.handle_update(group_update(MONTHLY_SUMMARY_COMMAND))

        self.assertTrue(handled)
        self.assertEqual(calls, [(config(), client, -1001)])
        self.assertEqual(client.sent_messages, [])

    def test_parses_bot_username_suffix(self):
        client = FakeTelegramClient(admin_status="administrator")
        calls = []
        handler = MonthlySummaryHandler(
            client,
            config(),
            send_summary=lambda *args: calls.append(args),
        )

        handled = handler.handle_update(group_update(f"{MONTHLY_SUMMARY_COMMAND}@TBYNBot"))

        self.assertTrue(handled)
        self.assertEqual(len(calls), 1)

    def test_non_admin_gets_temporary_permission_message(self):
        client = FakeTelegramClient(admin_status="member", sent_message_id=303)
        scheduled = []
        handler = MonthlySummaryHandler(
            client,
            config(),
            delete_after_seconds=20,
            schedule_delete=lambda *args: scheduled.append(args),
        )

        handled = handler.handle_update(group_update(MONTHLY_SUMMARY_COMMAND))

        self.assertTrue(handled)
        self.assertIn("Only group admins", client.sent_messages[0][1])
        self.assertEqual(scheduled, [(client, -1001, 303, 20)])

    def test_send_failure_gets_temporary_error_message(self):
        client = FakeTelegramClient(admin_status="administrator", sent_message_id=303)
        scheduled = []

        def send_summary(*args):
            raise RuntimeError("missing config")

        handler = MonthlySummaryHandler(
            client,
            config(),
            delete_after_seconds=20,
            schedule_delete=lambda *args: scheduled.append(args),
            send_summary=send_summary,
        )

        with self.assertLogs(level="ERROR"):
            handled = handler.handle_update(group_update(MONTHLY_SUMMARY_COMMAND))

        self.assertTrue(handled)
        self.assertIn("Monthly summary is not configured", client.sent_messages[0][1])
        self.assertEqual(scheduled, [(client, -1001, 303, 20)])

    def test_ignores_unrelated_message(self):
        client = FakeTelegramClient()
        handler = MonthlySummaryHandler(client, config())

        handled = handler.handle_update(group_update(f"{POLL_EVENT_COMMAND} Test"))

        self.assertFalse(handled)
        self.assertEqual(client.chat_member_requests, [])


if __name__ == "__main__":
    unittest.main()
