# TBYN Automation Bot

This repo contains small Python automation workflows for Tiong Bahru Youth Network (TBYN). The bot is designed to stay readable for volunteer handover while leaving room for future workflows.

## Requirements

- Python 3.11 or newer
- A Telegram bot token from BotFather
- The bot added to the target Telegram group
- Bot permissions to send polls and delete its own temporary messages

## Dependency Setup

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install runtime dependencies:

```bash
python3 -m pip install -r requirements.txt
```

The Telegram poll command uses only the Python standard library. The packages in `requirements.txt` are for the Google Sheets monthly summary workflow.

## Local Setup

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env`:

```text
TELEGRAM_BOT_TOKEN=your-bot-token
VALIDATION_DELETE_AFTER_SECONDS=20
POLLING_TIMEOUT_SECONDS=30
GOOGLE_SHEET_ID=your-google-sheet-id
GOOGLE_SERVICE_ACCOUNT_FILE=google-service-account.json
GOOGLE_EVENTS_RANGE=Events!A:D
```

The app reads `.env` automatically for local development. On a cloud host, set the same values as environment variables in the host dashboard; real environment variables take precedence over `.env`.

## Telegram Setup

1. Create a bot with BotFather.
2. Add the bot to your Telegram group.
3. Make the bot an admin if you want it to reliably check admin status and delete temporary validation messages.
4. In BotFather, consider disabling privacy mode if the bot does not receive group commands.

The bot registers its Telegram command menu when it starts. To re-register the
menu manually without starting the polling loop, run:

```bash
python3 -m tbyn_bot.bot_commands
```

After startup or manual registration, typing `/` in a Telegram chat with the bot should show:

```text
/poll_event
/events_this_month
```

## Google Sheets Setup

Use a Google service account for automation:

1. Create a service account in Google Cloud.
2. Download the service account JSON file.
3. Share the Google Sheet with the service account email.
4. Set `GOOGLE_SERVICE_ACCOUNT_FILE` to the JSON file path.
5. Set `GOOGLE_SHEET_ID` from the spreadsheet URL.

## Running Locally

Run the Telegram polling bot:

```bash
python3 main.py
```

Then trigger workflows from Telegram commands in a group where the bot is installed.

## Testing

Run:

```bash
python3 -m unittest discover
```

For a fuller verification pass:

```bash
python3 -m unittest discover -v
python3 -m compileall -q tbyn_bot main.py tests
```

## Cheap Cloud Hosting

Deploy `python3 main.py` as a long-running Python worker process on a low-cost host that supports persistent background workers.

Set these environment variables on the host:

```text
TELEGRAM_BOT_TOKEN
VALIDATION_DELETE_AFTER_SECONDS
POLLING_TIMEOUT_SECONDS
GOOGLE_SHEET_ID
GOOGLE_SERVICE_ACCOUNT_FILE
GOOGLE_EVENTS_RANGE
```

## Project Structure

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

## Workflows

<details>
<summary>Event Poll Workflow</summary>

In a Telegram group, an admin sends:

```text
/poll_event Meeting on 6th June
```

The bot posts a non-anonymous, single-choice poll with the title exactly as written:

```text
Meeting on 6th June
```

The bot randomly chooses one friendly yes option and one friendly no option from predefined variation lists each time it creates a poll.

If the command is missing the title, or if a non-admin tries to use it, the bot posts a short group message and attempts to delete that message after 20 seconds.

Workflow docs: `tbyn_bot/workflows/event_poll/README.md`

</details>

<details>
<summary>Monthly Event Summary Workflow</summary>

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

In a Telegram group, an admin sends:

```text
/events_this_month
```

The bot filters events for the current month and sends a Telegram message like:

```text
Whats happening this month:
1. Fun Times! - March @ Science Centre Omni-Theatre - 14/3/2026
2. Earth & Us! - Thrift, Trade, Transform @ The Nest @ TBCC - 28/3/2026
3. Board Game Afternoon @ The Nest @ TBCC - 29/3/2026
```

Workflow docs: `tbyn_bot/workflows/monthly_summary/README.md`

</details>
