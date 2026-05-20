"""Application configuration."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    validation_delete_after_seconds: int = 20
    polling_timeout_seconds: int = 30
    google_sheet_id: str = ""
    google_service_account_file: str = ""
    google_events_range: str = "Events!A:D"
    google_auth_mode: str = "oauth"
    google_oauth_client_secrets_file: str = "google-oauth-client.json"
    google_oauth_token_file: str = "google-oauth-token.json"
    google_meeting_slides_template_id: str = ""
    google_meeting_slides_folder_id: str = ""


def load_config() -> Config:
    load_dotenv()

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    return Config(
        telegram_bot_token=token,
        validation_delete_after_seconds=_read_int(
            "VALIDATION_DELETE_AFTER_SECONDS",
            default=20,
        ),
        polling_timeout_seconds=_read_int("POLLING_TIMEOUT_SECONDS", default=30),
        google_sheet_id=os.environ.get("GOOGLE_SHEET_ID", "").strip(),
        google_service_account_file=os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip(),
        google_events_range=os.environ.get("GOOGLE_EVENTS_RANGE", "Events!A:D").strip(),
        google_auth_mode=_read_google_auth_mode(),
        google_oauth_client_secrets_file=os.environ.get(
            "GOOGLE_OAUTH_CLIENT_SECRETS_FILE",
            "google-oauth-client.json",
        ).strip(),
        google_oauth_token_file=os.environ.get(
            "GOOGLE_OAUTH_TOKEN_FILE",
            "google-oauth-token.json",
        ).strip(),
        google_meeting_slides_template_id=os.environ.get(
            "GOOGLE_MEETING_SLIDES_TEMPLATE_ID",
            "",
        ).strip(),
        google_meeting_slides_folder_id=os.environ.get(
            "GOOGLE_MEETING_SLIDES_FOLDER_ID",
            "",
        ).strip(),
    )


def load_dotenv(path: str | Path = ".env") -> None:
    """Load KEY=VALUE pairs from a .env file without overriding real env vars."""
    env_path = Path(path)
    if not env_path.exists():
        return

    for line_number, raw_line in enumerate(env_path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line.removeprefix("export ").strip()

        key, separator, value = line.partition("=")
        if not separator:
            raise RuntimeError(f"Invalid .env line {line_number}: expected KEY=VALUE")

        key = key.strip()
        if not key:
            raise RuntimeError(f"Invalid .env line {line_number}: key is empty")

        os.environ.setdefault(key, _clean_env_value(value.strip()))


def _clean_env_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _read_int(name: str, default: int) -> int:
    raw_value = os.environ.get(name, "").strip()
    if not raw_value:
        return default

    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


def _read_google_auth_mode() -> str:
    auth_mode = os.environ.get("GOOGLE_AUTH_MODE", "oauth").strip().lower()
    if auth_mode not in {"service_account", "oauth"}:
        raise RuntimeError("GOOGLE_AUTH_MODE must be service_account or oauth")
    return auth_mode
