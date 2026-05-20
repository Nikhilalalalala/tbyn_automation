"""Google Sheets reader for event workflows."""

from __future__ import annotations

from typing import Any

from tbyn_bot.integrations.google_oauth import SPREADSHEETS_READONLY_SCOPE


def read_sheet_values(
    spreadsheet_id: str,
    cell_range: str,
    oauth_token_file: str,
    credentials_factory: Any | None = None,
    service_builder: Any | None = None,
) -> list[list[str]]:
    """Read values from Google Sheets using OAuth user credentials."""
    if credentials_factory is None or service_builder is None:
        try:
            from google.oauth2.credentials import Credentials as OAuthCredentials
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError(
                "Google Sheets dependencies are not installed. "
                "Run: pip install google-api-python-client google-auth"
            ) from exc

        credentials_factory = credentials_factory or OAuthCredentials.from_authorized_user_file
        service_builder = service_builder or build

    credentials = credentials_factory(
        oauth_token_file,
        scopes=[SPREADSHEETS_READONLY_SCOPE],
    )
    service = service_builder("sheets", "v4", credentials=credentials)
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=cell_range)
        .execute()
    )
    return result.get("values", [])
