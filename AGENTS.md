# AGENTS.md

Guidance for coding agents working on this repository.

## Project Purpose

This repo contains a small Python automation bot for Tiong Bahru Youth Network (TBYN).

Current workflows:

1. `event_poll`: Telegram admins can create event attendance polls with `/poll_event`.
2. `monthly_summary`: reads a Google Sheet and sends a Telegram summary of events happening in the current month.

Keep the code easy for future volunteers to understand and hand over.

## Architecture

Prefer this package structure:

```text
tbyn_bot/
  app.py
  config.py
  bot/
  integrations/
  utils/
  workflows/
    registry.py
    event_poll/
    monthly_summary/
```

Rules:

- Put each workflow in its own folder under `tbyn_bot/workflows/`.
- Give each workflow a local `README.md`.
- Register Telegram update handlers in `tbyn_bot/workflows/registry.py`.
- Keep external APIs in `tbyn_bot/integrations/`.
- Keep shared helpers in `tbyn_bot/utils/`.
- Keep command parsing, business logic, and integration calls separate.

## Python Standards

- Use Python 3.11+.
- Prefer the Python standard library unless a dependency clearly helps.
- Manage runtime dependencies in `requirements.txt`.
- Keep functions small and named for the workflow language.
- Use type hints where they improve readability.
- Avoid clever abstractions; this repo should feel readable to volunteers.

## Testing

Use `unittest`.

Add or update tests whenever behavior changes, especially for:

- command parsing
- permission checks
- poll payloads
- event row parsing
- monthly filtering
- message formatting
- config loading

Run before finishing:

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -v
python3 -m compileall -q tbyn_bot main.py tests
```

## Configuration And Secrets

- Read local settings from `.env`.
- Do not commit real tokens, chat IDs, service account JSON, or private spreadsheet IDs.
- Keep `.env.example` updated when adding config.
- Real environment variables should take precedence over `.env`.

## Telegram Bot Standards

- Use the official Telegram Bot API through `tbyn_bot/integrations/telegram.py`.
- Keep Telegram API payload construction out of handlers where possible.
- Admin-only commands must verify `creator` or `administrator` status.
- Temporary validation or permission replies should be deleted after the configured delay when possible.
- Do not delete a user's original command message unless explicitly requested.

## Google Sheets Standards

- Use service account auth for automation.
- Keep Google Sheets code in `tbyn_bot/integrations/google_sheets.py`.
- Keep parsing and formatting pure and testable in workflow modules.
- Do not require Google client libraries for the normal unit test suite.

## Documentation

Update the root `README.md` when setup, commands, env vars, or workflow entry points change.

Update the relevant workflow `README.md` when workflow behavior changes.

## Current Commands

Run the Telegram polling bot:

```bash
python3 main.py
```

Trigger an event poll from Telegram:

```text
/poll_event Meeting on 6th June
```

Trigger the monthly summary from Telegram:

```text
/events_this_month
```

The bot registers Telegram command suggestions on startup. To re-register them
manually without starting the polling loop:

```bash
python3 -m tbyn_bot.bot_commands
```
