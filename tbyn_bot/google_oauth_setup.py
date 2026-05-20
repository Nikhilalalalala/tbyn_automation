"""Local setup helper for Google OAuth credentials."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from tbyn_bot.config import load_dotenv
from tbyn_bot.integrations.google_oauth import SCOPES


def run_oauth_installed_app_flow(
    client_secrets_file: str,
    token_file: str,
    scopes: list[str] | None = None,
    flow_factory=None,
    token_writer=None,
):
    """Run the local installed-app OAuth flow and write refresh-token credentials."""
    selected_scopes = scopes or SCOPES
    if flow_factory is None:
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError as exc:
            raise RuntimeError(
                "Google OAuth setup dependency is not installed. "
                "Run: pip install google-auth-oauthlib"
            ) from exc

        flow_factory = InstalledAppFlow.from_client_secrets_file

    flow = flow_factory(client_secrets_file, selected_scopes)
    credentials = flow.run_local_server(port=0)

    writer = token_writer or _write_token_file
    writer(token_file, credentials.to_json(), mode=0o600)
    return credentials


def _write_token_file(token_file: str, token_json: str, mode: int = 0o600) -> None:
    path = Path(token_file)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    with os.fdopen(file_descriptor, "w", encoding="utf-8") as token_handle:
        token_handle.write(token_json)


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Run Google OAuth consent and write the token JSON file.",
    )
    parser.add_argument(
        "--client-secrets-file",
        default=os.environ.get(
            "GOOGLE_OAUTH_CLIENT_SECRETS_FILE",
            "google-oauth-client.json",
        ),
    )
    parser.add_argument(
        "--token-file",
        default=os.environ.get(
            "GOOGLE_OAUTH_TOKEN_FILE",
            "google-oauth-token.json",
        ),
    )
    args = parser.parse_args()

    run_oauth_installed_app_flow(
        args.client_secrets_file,
        args.token_file,
    )


if __name__ == "__main__":
    main()
