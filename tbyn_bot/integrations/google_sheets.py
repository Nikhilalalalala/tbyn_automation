"""Google Sheets reader for event workflows."""

from __future__ import annotations


def read_sheet_values(spreadsheet_id: str, cell_range: str, service_account_file: str) -> list[list[str]]:
    """Read values from Google Sheets using service account credentials.

    Install dependencies before using this integration:
    pip install google-api-python-client google-auth
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Google Sheets dependencies are not installed. "
            "Run: pip install google-api-python-client google-auth"
        ) from exc

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    service = build("sheets", "v4", credentials=credentials)
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=cell_range)
        .execute()
    )
    return result.get("values", [])
