import unittest

from tbyn_bot.config import Config
from tbyn_bot.workflows.create_meeting_slides import CREATE_MEETING_SLIDES_COMMAND
from tbyn_bot.workflows.create_meeting_slides.handler import CreateMeetingSlidesHandler
from tbyn_bot.workflows.create_meeting_slides.runner import AgendaParseError

from tests.fakes import FakeTelegramClient, group_update


def config():
    return Config(
        telegram_bot_token="token",
        google_auth_mode="oauth",
        google_oauth_token_file="token.json",
        google_meeting_slides_template_id="template-id",
        google_meeting_slides_folder_id="folder-id",
    )


def direct_update(text):
    return {
        "update_id": 2,
        "message": {
            "message_id": 12,
            "text": text,
            "chat": {"id": 55, "type": "private"},
            "from": {"id": 55, "username": "adminuser", "first_name": "Admin"},
        },
    }


class CreateMeetingSlidesHandlerTest(unittest.TestCase):
    def test_ignores_unrelated_message(self):
        client = FakeTelegramClient()
        handler = CreateMeetingSlidesHandler(client, config())

        handled = handler.handle_update(group_update("/events_this_month"))

        self.assertFalse(handled)
        self.assertEqual(client.chat_member_requests, [])
        self.assertEqual(client.sent_messages, [])

    def test_direct_chat_command_is_consumed_without_sending(self):
        client = FakeTelegramClient()
        handler = CreateMeetingSlidesHandler(client, config())

        handled = handler.handle_update(
            direct_update(f"{CREATE_MEETING_SLIDES_COMMAND} Deck\n1. Opening")
        )

        self.assertTrue(handled)
        self.assertEqual(client.chat_member_requests, [])
        self.assertEqual(client.sent_messages, [])

    def test_non_admin_gets_temporary_permission_message(self):
        client = FakeTelegramClient(admin_status="member", sent_message_id=303)
        scheduled = []
        handler = CreateMeetingSlidesHandler(
            client,
            config(),
            delete_after_seconds=20,
            schedule_delete=lambda *args: scheduled.append(args),
        )

        handled = handler.handle_update(
            group_update(f"{CREATE_MEETING_SLIDES_COMMAND} Deck\n1. Opening")
        )

        self.assertTrue(handled)
        self.assertIn("Only group admins", client.sent_messages[0][1])
        self.assertEqual(scheduled, [(client, -1001, 303, 20)])

    def test_missing_title_or_agenda_gets_usage_message(self):
        client = FakeTelegramClient(sent_message_id=303)
        scheduled = []
        handler = CreateMeetingSlidesHandler(
            client,
            config(),
            delete_after_seconds=20,
            schedule_delete=lambda *args: scheduled.append(args),
        )

        handled = handler.handle_update(group_update(f"{CREATE_MEETING_SLIDES_COMMAND} Deck"))

        self.assertTrue(handled)
        self.assertIn("Please include a deck title and agenda", client.sent_messages[0][1])
        self.assertEqual(scheduled, [(client, -1001, 303, 20)])

    def test_invalid_agenda_gets_temporary_validation_message(self):
        client = FakeTelegramClient(sent_message_id=303)
        scheduled = []
        handler = CreateMeetingSlidesHandler(
            client,
            config(),
            delete_after_seconds=20,
            schedule_delete=lambda *args: scheduled.append(args),
        )

        handled = handler.handle_update(
            group_update(f"{CREATE_MEETING_SLIDES_COMMAND} Deck\ninvalid agenda")
        )

        self.assertTrue(handled)
        self.assertIn("I could not read that agenda", client.sent_messages[0][1])
        self.assertEqual(scheduled, [(client, -1001, 303, 20)])

    def test_runtime_error_gets_temporary_failure_message(self):
        client = FakeTelegramClient(sent_message_id=303)
        scheduled = []

        def send_slides(*args):
            raise RuntimeError("missing config")

        handler = CreateMeetingSlidesHandler(
            client,
            config(),
            delete_after_seconds=20,
            schedule_delete=lambda *args: scheduled.append(args),
            send_slides=send_slides,
        )

        with self.assertLogs(level="ERROR"):
            handled = handler.handle_update(
                group_update(f"{CREATE_MEETING_SLIDES_COMMAND} Deck\n1. Opening")
            )

        self.assertTrue(handled)
        self.assertIn("I could not create the slides", client.sent_messages[0][1])
        self.assertEqual(scheduled, [(client, -1001, 303, 20)])

    def test_unexpected_send_error_gets_temporary_failure_message(self):
        client = FakeTelegramClient(sent_message_id=303)
        scheduled = []

        def send_slides(*args):
            raise Exception("google api failed")

        handler = CreateMeetingSlidesHandler(
            client,
            config(),
            delete_after_seconds=20,
            schedule_delete=lambda *args: scheduled.append(args),
            send_slides=send_slides,
        )

        with self.assertLogs(level="ERROR"):
            handled = handler.handle_update(
                group_update(f"{CREATE_MEETING_SLIDES_COMMAND} Deck\n1. Opening")
            )

        self.assertTrue(handled)
        self.assertIn("I could not create the slides", client.sent_messages[0][1])
        self.assertEqual(scheduled, [(client, -1001, 303, 20)])

    def test_agenda_parse_error_gets_temporary_validation_message(self):
        client = FakeTelegramClient(sent_message_id=303)
        scheduled = []

        def send_slides(*args):
            raise AgendaParseError("Invalid agenda line 1")

        handler = CreateMeetingSlidesHandler(
            client,
            config(),
            delete_after_seconds=20,
            schedule_delete=lambda *args: scheduled.append(args),
            send_slides=send_slides,
        )

        handled = handler.handle_update(
            group_update(f"{CREATE_MEETING_SLIDES_COMMAND} Deck\n1. Opening")
        )

        self.assertTrue(handled)
        self.assertIn("I could not read that agenda", client.sent_messages[0][1])
        self.assertEqual(scheduled, [(client, -1001, 303, 20)])

    def test_valid_admin_command_sends_slides_to_same_group(self):
        client = FakeTelegramClient(admin_status="creator")
        calls = []

        def send_slides(config, telegram_client, chat_id, deck_title, agenda_text):
            calls.append((config, telegram_client, chat_id, deck_title, agenda_text))

        handler = CreateMeetingSlidesHandler(client, config(), send_slides=send_slides)

        handled = handler.handle_update(
            group_update(f"{CREATE_MEETING_SLIDES_COMMAND} Deck\n1. Opening")
        )

        self.assertTrue(handled)
        self.assertEqual(calls, [(config(), client, -1001, "Deck", "1. Opening")])
        self.assertEqual(client.sent_messages, [])


if __name__ == "__main__":
    unittest.main()
