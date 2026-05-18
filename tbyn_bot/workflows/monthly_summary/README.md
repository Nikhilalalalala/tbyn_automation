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

## Running Manually

```bash
python3 -m tbyn_bot.workflows.monthly_summary
```

## Required Environment Variables

```text
TELEGRAM_BOT_TOKEN
MONTHLY_SUMMARY_CHAT_ID
GOOGLE_SHEET_ID
GOOGLE_SERVICE_ACCOUNT_FILE
GOOGLE_EVENTS_RANGE
```

`GOOGLE_EVENTS_RANGE` defaults to `Events!A:D`.

## Main Files

- `events.py`: parses rows, filters current-month events, and formats the summary.
- `runner.py`: reads the Google Sheet and sends the Telegram message.
- `__main__.py`: entry point for `python3 -m tbyn_bot.workflows.monthly_summary`.

