# TBYN Telegram Poll Bot

This is the first small automation workflow for Tiong Bahru Youth Network (TBYN). It runs a Telegram bot command that lets a group admin create an event attendance poll.

## What It Does

In a Telegram group, an admin sends:

```text
/poll_event Meeting on 6th June
```

The bot posts a non-anonymous, single-choice poll:

```text
Meeting on 6th June
```

Options:

```text
Yes, I'll be there!
Sorry, I'll join next time
```

The bot randomly chooses one friendly yes option and one friendly no option from predefined variation lists each time it creates a poll.

If the command is missing the date, or if a non-admin tries to use it, the bot posts a short group message and attempts to delete that message after 20 seconds.

## Requirements

- Python 3.11 or newer
- A Telegram bot token from BotFather
- The bot added to the target Telegram group
- Bot permissions to send polls and delete its own messages

No Python package installation is needed for the Telegram poll command.

The Google Sheets monthly summary workflow needs these extra packages:

```bash
pip install google-api-python-client google-auth
```

## Local Setup

Copy the example environment file and set your token:

```bash
cp .env.example .env
```

Edit `.env`:

```text
TELEGRAM_BOT_TOKEN=your-bot-token
VALIDATION_DELETE_AFTER_SECONDS=20
POLLING_TIMEOUT_SECONDS=30
MONTHLY_SUMMARY_CHAT_ID=your-telegram-chat-id
GOOGLE_SHEET_ID=your-google-sheet-id
GOOGLE_SERVICE_ACCOUNT_FILE=google-service-account.json
GOOGLE_EVENTS_RANGE=Events!A:D
```

Run the bot:

```bash
python3 main.py
```

The app reads `.env` automatically for local development. On a cloud host, set the same values as environment variables in the host dashboard; those real environment variables take precedence over `.env`.

## Telegram Setup

1. Create a bot with BotFather.
2. Add the bot to your Telegram group.
3. Make the bot an admin if you want it to reliably check admin status and delete temporary validation messages.
4. In BotFather, consider disabling privacy mode if the bot does not receive group commands.

## Testing

Run:

```bash
python3 -m unittest discover
```

## Monthly Event Summary Workflow

The monthly summary workflow reads a Google Sheet with this structure:

```text
S/N | Event TItle | Event Date | Venue
```

Example rows:

```text
5 | Fun Times! - March | 14/3/2026 | Science Centre Omni-Theatre
6 | Earth & Us! - Thrift, Trade, Transform | 28/3/2026 | The Nest @ TBCC
7 | Board Game Afternoon | 29/3/2026 | The Nest @ TBCC
```

On the 1st day of the month, it filters events for that month and sends a Telegram message like:

```text
Whats happening this month:
1. Fun Times! - March @ Science Centre Omni-Theatre - 14/3/2026
2. Earth & Us! - Thrift, Trade, Transform @ The Nest @ TBCC - 28/3/2026
3. Board Game Afternoon @ The Nest @ TBCC - 29/3/2026
```

Set these environment variables before enabling the workflow:

```text
MONTHLY_SUMMARY_CHAT_ID
GOOGLE_SHEET_ID
GOOGLE_SERVICE_ACCOUNT_FILE
GOOGLE_EVENTS_RANGE
```

Use a Google service account for automation:

1. Create a service account in Google Cloud.
2. Download the service account JSON file.
3. Share the Google Sheet with the service account email.
4. Set `GOOGLE_SERVICE_ACCOUNT_FILE` to the JSON file path.
5. Set `GOOGLE_SHEET_ID` from the spreadsheet URL.

Run the workflow manually:

```bash
python3 -m tbyn_bot.workflows.monthly_summary
```

Later, schedule that command on your cloud host for the 1st day of every month.

## Cheap Cloud Hosting

Deploy this as a long-running Python worker process on a low-cost host that supports persistent background workers. Set the same environment variables on the host:

```text
TELEGRAM_BOT_TOKEN
VALIDATION_DELETE_AFTER_SECONDS
POLLING_TIMEOUT_SECONDS
MONTHLY_SUMMARY_CHAT_ID
GOOGLE_SHEET_ID
GOOGLE_SERVICE_ACCOUNT_FILE
GOOGLE_EVENTS_RANGE
```

Use `python3 main.py` as the worker start command.

## Future Workflow Shape

The bot is intentionally split into command parsing, permission checks, poll construction, Telegram API calls, cleanup, configuration, workflow registration, and app startup.

The main package layout is:

```text
tbyn_bot/
  app.py
  config.py
  bot/
    dispatcher.py
  integrations/
    telegram.py
    google_sheets.py
  utils/
    cleanup.py
  workflows/
    registry.py
    event_poll/
    monthly_summary/
```

Future TBYN workflows should get their own folder under `tbyn_bot/workflows/` and be registered in `tbyn_bot/workflows/registry.py` instead of rewriting the polling loop.
