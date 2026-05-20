from dataclasses import dataclass
from inspect import signature
import unittest

from tbyn_bot.integrations.meeting_slides import (
    _create_meeting_slides_from_template,
    build_meeting_slides_batch_update_requests,
    create_meeting_slides_from_template,
    find_required_placeholder_slide_ids,
)
from tbyn_bot.google_oauth_setup import run_oauth_installed_app_flow


def slide_with_text(object_id, text):
    return {
        "objectId": object_id,
        "pageElements": [
            {
                "shape": {
                    "text": {
                        "textElements": [
                            {"textRun": {"content": text}},
                        ]
                    }
                }
            }
        ],
    }


@dataclass
class SlidePlanItem:
    kind: str
    title: str
    body: str = ""


class GoogleSlidesTest(unittest.TestCase):
    def test_finds_required_placeholder_slide_ids(self):
        presentation = {
            "slides": [
                slide_with_text("slide_1", "{{MEETING_TITLE}}"),
                slide_with_text("slide_2", "{{AGENDA_TITLE}}"),
                slide_with_text(
                    "slide_3",
                    "{{AGENDA_ITEM_TITLE}}\n{{AGENDA_ITEM_BODY}}",
                ),
            ]
        }

        placeholders = find_required_placeholder_slide_ids(presentation)

        self.assertEqual(
            placeholders,
            {
                "meeting_title": "slide_1",
                "agenda_title": "slide_2",
                "agenda_item": "slide_3",
            },
        )

    def test_uses_agenda_item_slide_with_title_and_body_placeholders(self):
        presentation = {
            "slides": [
                slide_with_text("slide_1", "{{MEETING_TITLE}}"),
                slide_with_text("slide_2", "{{AGENDA_TITLE}}"),
                slide_with_text("incomplete_item", "{{AGENDA_ITEM_TITLE}}"),
                slide_with_text(
                    "complete_item",
                    "{{AGENDA_ITEM_TITLE}}\n{{AGENDA_ITEM_BODY}}",
                ),
            ]
        }

        placeholders = find_required_placeholder_slide_ids(presentation)

        self.assertEqual(placeholders["agenda_item"], "complete_item")

    def test_raises_when_required_placeholder_is_missing(self):
        presentation = {
            "slides": [
                slide_with_text("slide_1", "{{MEETING_TITLE}}"),
                slide_with_text("slide_2", "{{AGENDA_TITLE}}"),
            ]
        }

        with self.assertRaises(RuntimeError) as context:
            find_required_placeholder_slide_ids(presentation)

        self.assertIn("{{AGENDA_ITEM_TITLE}}", str(context.exception))

    def test_raises_when_agenda_item_body_placeholder_is_missing(self):
        presentation = {
            "slides": [
                slide_with_text("slide_1", "{{MEETING_TITLE}}"),
                slide_with_text("slide_2", "{{AGENDA_TITLE}}"),
                slide_with_text("slide_3", "{{AGENDA_ITEM_TITLE}}"),
            ]
        }

        with self.assertRaises(RuntimeError) as context:
            find_required_placeholder_slide_ids(presentation)

        self.assertIn("{{AGENDA_ITEM_BODY}}", str(context.exception))

    def test_builds_requests_to_duplicate_replace_and_delete_placeholders(self):
        placeholders = {
            "meeting_title": "meeting_placeholder",
            "agenda_title": "agenda_placeholder",
            "agenda_item": "item_placeholder",
        }
        slides = [
            SlidePlanItem("meeting_title", "TBYN Meeting May 2026"),
            SlidePlanItem("agenda_title", "Confirmation"),
            SlidePlanItem("agenda_item", "Bahru Mania!", "Date:\nTime:\nVenue:"),
        ]

        requests = build_meeting_slides_batch_update_requests(placeholders, slides)

        self.assertEqual(
            requests[0],
            {
                "duplicateObject": {
                    "objectId": "meeting_placeholder",
                    "objectIds": {"meeting_placeholder": "generated_slide_1"},
                }
            },
        )
        self.assertEqual(
            requests[1],
            {
                "replaceAllText": {
                    "containsText": {
                        "text": "{{MEETING_TITLE}}",
                        "matchCase": True,
                    },
                    "replaceText": "TBYN Meeting May 2026",
                    "pageObjectIds": ["generated_slide_1"],
                }
            },
        )
        self.assertIn(
            {
                "replaceAllText": {
                    "containsText": {
                        "text": "{{AGENDA_ITEM_BODY}}",
                        "matchCase": True,
                    },
                    "replaceText": "Date:\nTime:\nVenue:",
                    "pageObjectIds": ["generated_slide_3"],
                }
            },
            requests,
        )
        self.assertEqual(
            requests[-6:],
            [
                {
                    "updateSlidesPosition": {
                        "slideObjectIds": ["generated_slide_3"],
                        "insertionIndex": 0,
                    }
                },
                {
                    "updateSlidesPosition": {
                        "slideObjectIds": ["generated_slide_2"],
                        "insertionIndex": 0,
                    }
                },
                {
                    "updateSlidesPosition": {
                        "slideObjectIds": ["generated_slide_1"],
                        "insertionIndex": 0,
                    }
                },
                {"deleteObject": {"objectId": "meeting_placeholder"}},
                {"deleteObject": {"objectId": "agenda_placeholder"}},
                {"deleteObject": {"objectId": "item_placeholder"}},
            ],
        )

    def test_moves_generated_slides_one_at_a_time_in_reverse_agenda_order(self):
        placeholders = {
            "meeting_title": "meeting_placeholder",
            "agenda_title": "agenda_placeholder",
            "agenda_item": "item_placeholder",
        }
        slides = [
            SlidePlanItem("meeting_title", "TBYN Meeting May 2026"),
            SlidePlanItem("agenda_title", "Completed Events"),
            SlidePlanItem("agenda_item", "First Item", "Date:\nTime:\nVenue:"),
            SlidePlanItem("agenda_item", "Second Item", "Date:\nTime:\nVenue:"),
        ]

        requests = build_meeting_slides_batch_update_requests(placeholders, slides)

        position_requests = [
            request["updateSlidesPosition"]
            for request in requests
            if "updateSlidesPosition" in request
        ]
        self.assertEqual(
            position_requests,
            [
                {"slideObjectIds": ["generated_slide_4"], "insertionIndex": 0},
                {"slideObjectIds": ["generated_slide_3"], "insertionIndex": 0},
                {"slideObjectIds": ["generated_slide_2"], "insertionIndex": 0},
                {"slideObjectIds": ["generated_slide_1"], "insertionIndex": 0},
            ],
        )

    def test_copies_template_populates_deck_and_returns_url(self):
        fake_google = FakeGoogleServices()

        url = _create_meeting_slides_from_template(
            "template-id",
            "folder-id",
            "TBYN Meeting May 2026",
            [
                SlidePlanItem("meeting_title", "TBYN Meeting May 2026"),
                SlidePlanItem("agenda_title", "Confirmation"),
            ],
            oauth_token_file="google-oauth-token.json",
            oauth_credentials_factory=fake_google.oauth_credentials_factory,
            service_builder=fake_google.service_builder,
        )

        self.assertEqual(
            fake_google.scopes,
            [
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/presentations",
            ],
        )
        self.assertEqual(
            fake_google.drive.copy_call,
            {
                "fileId": "template-id",
                "body": {
                    "name": "TBYN Meeting May 2026",
                    "parents": ["folder-id"],
                },
                "fields": "id",
            },
        )
        self.assertEqual(fake_google.slides.get_presentation_id, "copied-id")
        self.assertEqual(fake_google.slides.batch_presentation_id, "copied-id")
        self.assertTrue(fake_google.slides.batch_requests)
        self.assertEqual(
            url,
            "https://docs.google.com/presentation/d/copied-id/edit",
        )

    def test_requires_oauth_token_credentials_for_template_copy(self):
        fake_google = FakeGoogleServices()

        _create_meeting_slides_from_template(
            "template-id",
            "folder-id",
            "TBYN Meeting May 2026",
            [],
            oauth_token_file="google-oauth-token.json",
            oauth_credentials_factory=fake_google.oauth_credentials_factory,
            service_builder=fake_google.service_builder,
        )

        self.assertEqual(fake_google.oauth_token_file, "google-oauth-token.json")
        self.assertEqual(fake_google.credentials, "oauth-credentials")

    def test_uses_oauth_token_credentials_for_template_copy_when_requested(self):
        fake_google = FakeGoogleServices()

        _create_meeting_slides_from_template(
            "template-id",
            "folder-id",
            "TBYN Meeting May 2026",
            [],
            auth_mode="oauth",
            oauth_token_file="google-oauth-token.json",
            oauth_credentials_factory=fake_google.oauth_credentials_factory,
            service_builder=fake_google.service_builder,
        )

        self.assertEqual(fake_google.oauth_token_file, "google-oauth-token.json")
        self.assertEqual(
            fake_google.scopes,
            [
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/presentations",
            ],
        )
        self.assertEqual(fake_google.credentials, "oauth-credentials")

    def test_public_template_copy_uses_oauth_arguments_only(self):
        parameters = signature(create_meeting_slides_from_template).parameters

        self.assertNotIn("service_account_file", parameters)
        self.assertEqual(parameters["auth_mode"].default, "oauth")

    def test_runs_oauth_installed_app_flow_and_writes_token_file(self):
        fake_flow_factory = FakeOAuthFlowFactory()
        token_writer = FakeTokenWriter()

        credentials = run_oauth_installed_app_flow(
            "google-oauth-client.json",
            "google-oauth-token.json",
            flow_factory=fake_flow_factory.from_client_secrets_file,
            token_writer=token_writer.write_text,
        )

        self.assertEqual(credentials, fake_flow_factory.flow.credentials)
        self.assertEqual(
            fake_flow_factory.call,
            {
                "client_secrets_file": "google-oauth-client.json",
                "scopes": [
                    "https://www.googleapis.com/auth/drive",
                    "https://www.googleapis.com/auth/presentations",
                    "https://www.googleapis.com/auth/spreadsheets.readonly",
                ],
            },
        )
        self.assertEqual(fake_flow_factory.flow.run_local_server_port, 0)
        self.assertEqual(
            token_writer.call,
            {
                "path": "google-oauth-token.json",
                "text": '{"refresh_token": "token"}',
                "mode": 0o600,
            },
        )


class FakeGoogleServices:
    def __init__(self):
        self.scopes = None
        self.oauth_token_file = None
        self.drive = FakeDriveService()
        self.slides = FakeSlidesService()

    def oauth_credentials_factory(self, oauth_token_file, scopes):
        self.oauth_token_file = oauth_token_file
        self.scopes = scopes
        return "oauth-credentials"

    def service_builder(self, service_name, version, credentials):
        self.credentials = credentials
        if (service_name, version) == ("drive", "v3"):
            return self.drive
        if (service_name, version) == ("slides", "v1"):
            return self.slides
        raise AssertionError(f"Unexpected service: {service_name} {version}")


class FakeDriveService:
    def __init__(self):
        self.copy_call = None

    def files(self):
        return self

    def copy(self, **kwargs):
        self.copy_call = kwargs
        return FakeExecute({"id": "copied-id"})


class FakeSlidesService:
    def __init__(self):
        self.get_presentation_id = None
        self.batch_presentation_id = None
        self.batch_requests = None

    def presentations(self):
        return self

    def get(self, presentationId):
        self.get_presentation_id = presentationId
        return FakeExecute(
            {
                "slides": [
                    slide_with_text("meeting_placeholder", "{{MEETING_TITLE}}"),
                    slide_with_text("agenda_placeholder", "{{AGENDA_TITLE}}"),
                    slide_with_text(
                        "item_placeholder",
                        "{{AGENDA_ITEM_TITLE}}\n{{AGENDA_ITEM_BODY}}",
                    ),
                ]
            }
        )

    def batchUpdate(self, presentationId, body):
        self.batch_presentation_id = presentationId
        self.batch_requests = body["requests"]
        return FakeExecute({})


class FakeExecute:
    def __init__(self, result):
        self.result = result

    def execute(self):
        return self.result


class FakeOAuthFlowFactory:
    def __init__(self):
        self.call = None
        self.flow = FakeOAuthFlow()

    def from_client_secrets_file(self, client_secrets_file, scopes):
        self.call = {
            "client_secrets_file": client_secrets_file,
            "scopes": scopes,
        }
        return self.flow


class FakeOAuthFlow:
    def __init__(self):
        self.credentials = FakeOAuthCredentials()
        self.run_local_server_port = None

    def run_local_server(self, port):
        self.run_local_server_port = port
        return self.credentials


class FakeOAuthCredentials:
    def to_json(self):
        return '{"refresh_token": "token"}'


class FakeTokenWriter:
    def __init__(self):
        self.call = None

    def write_text(self, path, text, mode=None):
        self.call = {
            "path": path,
            "text": text,
            "mode": mode,
        }


if __name__ == "__main__":
    unittest.main()
