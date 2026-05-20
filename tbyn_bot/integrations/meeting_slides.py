"""Google Slides deck creation for meeting workflows."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from tbyn_bot.integrations.google_oauth import DRIVE_SCOPE, PRESENTATIONS_SCOPE

SCOPES = [DRIVE_SCOPE, PRESENTATIONS_SCOPE]

MEETING_TITLE_PLACEHOLDER = "{{MEETING_TITLE}}"
AGENDA_TITLE_PLACEHOLDER = "{{AGENDA_TITLE}}"
AGENDA_ITEM_TITLE_PLACEHOLDER = "{{AGENDA_ITEM_TITLE}}"
AGENDA_ITEM_BODY_PLACEHOLDER = "{{AGENDA_ITEM_BODY}}"

PLACEHOLDER_BY_KIND = {
    "meeting_title": MEETING_TITLE_PLACEHOLDER,
    "agenda_title": AGENDA_TITLE_PLACEHOLDER,
    "agenda_item": AGENDA_ITEM_TITLE_PLACEHOLDER,
}


def create_meeting_slides_from_template(
    template_presentation_id: str,
    output_folder_id: str,
    deck_title: str,
    slides: list,
    auth_mode: str = "oauth",
    oauth_token_file: str = "",
) -> str:
    """Copy a template deck, populate meeting slides, and return the edit URL."""
    try:
        from google.oauth2.credentials import Credentials as OAuthCredentials
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Google Slides dependencies are not installed. "
            "Run: pip install google-api-python-client google-auth"
        ) from exc

    return _create_meeting_slides_from_template(
        template_presentation_id,
        output_folder_id,
        deck_title,
        slides,
        auth_mode=auth_mode,
        oauth_token_file=oauth_token_file,
        oauth_credentials_factory=OAuthCredentials.from_authorized_user_file,
        service_builder=build,
    )


def _create_meeting_slides_from_template(
    template_presentation_id: str,
    output_folder_id: str,
    deck_title: str,
    slides: list,
    service_builder: Any,
    auth_mode: str = "oauth",
    oauth_token_file: str = "",
    oauth_credentials_factory: Any | None = None,
) -> str:
    credentials = _build_credentials(
        auth_mode=auth_mode,
        oauth_token_file=oauth_token_file,
        oauth_credentials_factory=oauth_credentials_factory,
    )
    drive_service = service_builder("drive", "v3", credentials=credentials)
    slides_service = service_builder("slides", "v1", credentials=credentials)

    copied_file = (
        drive_service.files()
        .copy(
            fileId=template_presentation_id,
            body={"name": deck_title, "parents": [output_folder_id]},
            fields="id",
        )
        .execute()
    )
    presentation_id = copied_file["id"]

    presentation = (
        slides_service.presentations()
        .get(presentationId=presentation_id)
        .execute()
    )
    placeholders = find_required_placeholder_slide_ids(presentation)
    requests = build_meeting_slides_batch_update_requests(placeholders, slides)

    if requests:
        (
            slides_service.presentations()
            .batchUpdate(
                presentationId=presentation_id,
                body={"requests": requests},
            )
            .execute()
        )

    return f"https://docs.google.com/presentation/d/{presentation_id}/edit"


def _build_credentials(
    auth_mode: str,
    oauth_token_file: str,
    oauth_credentials_factory: Any | None,
) -> Any:
    normalized_auth_mode = auth_mode.strip().lower()

    if normalized_auth_mode == "oauth":
        if not oauth_token_file:
            raise RuntimeError("GOOGLE_OAUTH_TOKEN_FILE is required for OAuth auth")
        if oauth_credentials_factory is None:
            raise RuntimeError("OAuth credentials factory is required for OAuth auth")
        return oauth_credentials_factory(
            oauth_token_file,
            scopes=SCOPES,
        )

    raise RuntimeError(
        "GOOGLE_AUTH_MODE=oauth is required"
    )


def find_required_placeholder_slide_ids(presentation: dict[str, Any]) -> dict[str, str]:
    """Return the template slide object IDs for all required placeholders."""
    found: dict[str, str] = {}
    incomplete_agenda_item_found = False

    for slide in presentation.get("slides", []):
        slide_text = "\n".join(_iter_strings(slide))
        if (
            AGENDA_ITEM_TITLE_PLACEHOLDER in slide_text
            and AGENDA_ITEM_BODY_PLACEHOLDER in slide_text
            and "agenda_item" not in found
        ):
            found["agenda_item"] = slide["objectId"]
            continue
        if AGENDA_ITEM_TITLE_PLACEHOLDER in slide_text:
            incomplete_agenda_item_found = True

        for kind, placeholder in PLACEHOLDER_BY_KIND.items():
            if kind == "agenda_item":
                continue
            if placeholder in slide_text and kind not in found:
                found[kind] = slide["objectId"]

    missing = [
        placeholder
        for kind, placeholder in PLACEHOLDER_BY_KIND.items()
        if kind not in found
    ]
    if incomplete_agenda_item_found and "agenda_item" not in found:
        missing.append(AGENDA_ITEM_BODY_PLACEHOLDER)

    if missing:
        raise RuntimeError(
            "Template presentation is missing required placeholder slides: "
            + ", ".join(missing)
        )

    return found


def build_meeting_slides_batch_update_requests(
    placeholder_slide_ids: dict[str, str],
    slides: Iterable[Any],
) -> list[dict[str, Any]]:
    """Build Slides API requests for duplicating and populating planned slides."""
    requests: list[dict[str, Any]] = []
    generated_slide_ids: list[str] = []

    for index, slide in enumerate(slides, start=1):
        kind = _slide_kind_key(slide)
        placeholder_slide_id = placeholder_slide_ids[kind]
        generated_slide_id = f"generated_slide_{index}"
        generated_slide_ids.append(generated_slide_id)

        requests.append(
            {
                "duplicateObject": {
                    "objectId": placeholder_slide_id,
                    "objectIds": {placeholder_slide_id: generated_slide_id},
                }
            }
        )
        requests.extend(_replacement_requests(kind, slide, generated_slide_id))

    for generated_slide_id in reversed(generated_slide_ids):
        requests.append(
            {
                "updateSlidesPosition": {
                    "slideObjectIds": [generated_slide_id],
                    "insertionIndex": 0,
                }
            }
        )

    for placeholder_slide_id in placeholder_slide_ids.values():
        requests.append({"deleteObject": {"objectId": placeholder_slide_id}})

    return requests


def _replacement_requests(
    kind: str,
    slide: Any,
    page_object_id: str,
) -> list[dict[str, Any]]:
    if kind == "meeting_title":
        return [
            _replace_text_request(
                MEETING_TITLE_PLACEHOLDER,
                slide.title,
                page_object_id,
            )
        ]
    if kind == "agenda_title":
        return [
            _replace_text_request(
                AGENDA_TITLE_PLACEHOLDER,
                slide.title,
                page_object_id,
            )
        ]
    if kind == "agenda_item":
        return [
            _replace_text_request(
                AGENDA_ITEM_TITLE_PLACEHOLDER,
                slide.title,
                page_object_id,
            ),
            _replace_text_request(
                AGENDA_ITEM_BODY_PLACEHOLDER,
                getattr(slide, "body", ""),
                page_object_id,
            ),
        ]

    raise RuntimeError(f"Unsupported slide kind: {kind}")


def _replace_text_request(
    placeholder: str,
    replacement: str,
    page_object_id: str,
) -> dict[str, Any]:
    return {
        "replaceAllText": {
            "containsText": {
                "text": placeholder,
                "matchCase": True,
            },
            "replaceText": replacement,
            "pageObjectIds": [page_object_id],
        }
    }


def _slide_kind_key(slide: Any) -> str:
    kind = slide.kind
    value = getattr(kind, "value", kind)
    if not isinstance(value, str):
        value = getattr(kind, "name", str(kind))
    return value.lower()


def _iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _iter_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_strings(child)
