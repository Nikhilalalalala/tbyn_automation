# Monthly Summary Workflow

This workflow reads a Google Sheet of events and sends a Telegram summary of events happening in the current month.

## Sheet Structure

The Google Sheet should have these columns:

```text
S/N | Event TItle | Event Date | Venue
```

Event dates are currently parsed as `D/M/YYYY`, for example:

```text
14/3/2026
```

## Message Format

For March 2026, the message looks like:

```text
Whats happening this month:
1. Fun Times! - March @ Science Centre Omni-Theatre - 14/3/2026
2. Earth & Us! - Thrift, Trade, Transform @ The Nest @ TBCC - 28/3/2026
3. Board Game Afternoon @ The Nest @ TBCC - 29/3/2026
```

## Command

Run the Telegram bot:

```bash
python3 main.py
```

Then send this command in a Telegram group where the bot is installed:

```text
/events_this_month
```

## Required Environment Variables

```text
TELEGRAM_BOT_TOKEN
GOOGLE_SHEET_ID
GOOGLE_EVENTS_RANGE
GOOGLE_AUTH_MODE
GOOGLE_OAUTH_TOKEN_FILE
```

`GOOGLE_EVENTS_RANGE` defaults to `Events!A:D`.
Set `GOOGLE_AUTH_MODE=oauth` and share the Google Sheet with the automation Google account used to generate `GOOGLE_OAUTH_TOKEN_FILE`.
If the OAuth token was created before this workflow used OAuth, regenerate it with `python3 -m tbyn_bot.google_oauth_setup`.

## Main Files

- `events.py`: parses rows, filters current-month events, and formats the summary.
- `handler.py`: handles the `/events_this_month` Telegram command.
- `runner.py`: reads the Google Sheet and sends the Telegram message to the command's group.
