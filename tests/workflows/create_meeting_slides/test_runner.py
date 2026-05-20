import unittest

from tbyn_bot.config import Config
from tbyn_bot.workflows.create_meeting_slides.agenda import SlideKind
from tbyn_bot.workflows.create_meeting_slides.runner import (
    AgendaParseError,
    send_meeting_slides_to_chat,
)

from tests.fakes import FakeTelegramClient


def config(**overrides):
    values = {
        "telegram_bot_token": "token",
        "google_auth_mode": "oauth",
        "google_oauth_token_file": "token.json",
        "google_meeting_slides_template_id": "template-id",
        "google_meeting_slides_folder_id": "folder-id",
    }
    values.update(overrides)
    return Config(**values)


class CreateMeetingSlidesRunnerTest(unittest.TestCase):
    def test_service_account_auth_mode_is_rejected_for_meeting_slides(self):
        with self.assertRaisesRegex(RuntimeError, "GOOGLE_AUTH_MODE=oauth"):
            send_meeting_slides_to_chat(
                config(
                    google_auth_mode="service_account",
                    google_service_account_file="service-account.json",
                ),
                FakeTelegramClient(),
                -1001,
                "Deck",
                "1. Opening",
            )

    def test_oauth_requires_token_file(self):
        with self.assertRaisesRegex(RuntimeError, "GOOGLE_OAUTH_TOKEN_FILE"):
            send_meeting_slides_to_chat(
                config(
                    google_auth_mode="oauth",
                    google_oauth_client_secrets_file="client.json",
                    google_oauth_token_file="",
                ),
                FakeTelegramClient(),
                -1001,
                "Deck",
                "1. Opening",
            )

    def test_missing_template_id_raises(self):
        with self.assertRaisesRegex(RuntimeError, "GOOGLE_MEETING_SLIDES_TEMPLATE_ID"):
            send_meeting_slides_to_chat(
                config(google_meeting_slides_template_id=""),
                FakeTelegramClient(),
                -1001,
                "Deck",
                "1. Opening",
            )

    def test_missing_folder_id_raises(self):
        with self.assertRaisesRegex(RuntimeError, "GOOGLE_MEETING_SLIDES_FOLDER_ID"):
            send_meeting_slides_to_chat(
                config(google_meeting_slides_folder_id=""),
                FakeTelegramClient(),
                -1001,
                "Deck",
                "1. Opening",
            )

    def test_success_creates_deck_and_sends_url_to_chat(self):
        client = FakeTelegramClient()
        creator_calls = []

        def creator(**kwargs):
            creator_calls.append(kwargs)
            return "https://docs.google.com/presentation/d/new-deck/edit"

        send_meeting_slides_to_chat(
            config(),
            client,
            -1001,
            "TBYN Meeting May 2026",
            "1. Opening\n   a. Updates",
            create_slides=creator,
        )

        self.assertEqual(len(creator_calls), 1)
        self.assertEqual(creator_calls[0]["template_presentation_id"], "template-id")
        self.assertEqual(creator_calls[0]["output_folder_id"], "folder-id")
        self.assertEqual(creator_calls[0]["deck_title"], "TBYN Meeting May 2026")
        self.assertEqual(
            [slide.kind for slide in creator_calls[0]["slides"]],
            [SlideKind.MEETING_TITLE, SlideKind.AGENDA_TITLE, SlideKind.AGENDA_ITEM],
        )
        self.assertNotIn("service_account_file", creator_calls[0])
        self.assertEqual(creator_calls[0]["auth_mode"], "oauth")
        self.assertEqual(creator_calls[0]["oauth_token_file"], "token.json")
        self.assertEqual(
            client.sent_messages,
            [(-1001, "Meeting slides created: https://docs.google.com/presentation/d/new-deck/edit")],
        )

    def test_oauth_creates_deck_with_oauth_credentials(self):
        client = FakeTelegramClient()
        creator_calls = []

        def creator(**kwargs):
            creator_calls.append(kwargs)
            return "https://docs.google.com/presentation/d/oauth-deck/edit"

        send_meeting_slides_to_chat(
                config(
                    google_auth_mode="oauth",
                    google_oauth_client_secrets_file="client.json",
                    google_oauth_token_file="token.json",
            ),
            client,
            -1001,
            "TBYN Meeting May 2026",
            "1. Opening",
            create_slides=creator,
        )

        self.assertEqual(len(creator_calls), 1)
        self.assertEqual(creator_calls[0]["auth_mode"], "oauth")
        self.assertEqual(creator_calls[0]["oauth_token_file"], "token.json")
        self.assertEqual(
            client.sent_messages,
            [(-1001, "Meeting slides created: https://docs.google.com/presentation/d/oauth-deck/edit")],
        )

    def test_invalid_agenda_raises_agenda_parse_error(self):
        with self.assertRaises(AgendaParseError):
            send_meeting_slides_to_chat(
                config(),
                FakeTelegramClient(),
                -1001,
                "Deck",
                "invalid agenda",
            )

    def test_creator_value_error_becomes_runtime_error(self):
        def creator(**kwargs):
            raise ValueError("bad credentials")

        with self.assertRaisesRegex(RuntimeError, "Failed to create meeting slides"):
            send_meeting_slides_to_chat(
                config(),
                FakeTelegramClient(),
                -1001,
                "Deck",
                "1. Opening",
                create_slides=creator,
            )


if __name__ == "__main__":
    unittest.main()
