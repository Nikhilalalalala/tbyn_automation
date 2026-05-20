# TBYN Automation Bot

This repo contains small Python automation workflows for Tiong Bahru Youth Network (TBYN). The bot is designed to stay readable for volunteer handover while leaving room for future workflows.

## Requirements

- Python 3.11 or newer
- A Telegram bot token from BotFather
- The bot added to the target Telegram group
- Bot permissions to send polls and delete its own temporary messages
- Google Sheets API, Google Drive API, and Google Slides API enabled in Google Cloud Console for Google workflows

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

The Telegram poll command uses only the Python standard library. The packages in `requirements.txt` are for the Google Sheets monthly summary and Google Slides workflows.

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
GOOGLE_AUTH_MODE=oauth
GOOGLE_OAUTH_CLIENT_SECRETS_FILE=google-oauth-client.json
GOOGLE_OAUTH_TOKEN_FILE=google-oauth-token.json
GOOGLE_MEETING_SLIDES_TEMPLATE_ID=your-template-presentation-id
GOOGLE_MEETING_SLIDES_FOLDER_ID=your-output-folder-id
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
/create_meeting_slides
```

## Google Sheets Setup

Use a Google service account for the monthly event summary:

1. Enable the Google Sheets API in Google Cloud Console.
2. Create a service account in Google Cloud.
3. Download the service account JSON file.
4. Share the Google Sheet with the service account email.
5. Set `GOOGLE_SERVICE_ACCOUNT_FILE` to the JSON file path.
6. Set `GOOGLE_SHEET_ID` from the spreadsheet URL.

## Google Slides Setup

Use OAuth user auth for meeting slide generation. A dedicated Google automation account is recommended so generated decks are owned by that account instead of a volunteer's personal account.

1. Enable the Google Drive API and Google Slides API in Google Cloud Console.
2. Create an OAuth client ID with application type `Desktop app`.
3. Download the OAuth client secrets JSON as `google-oauth-client.json`.
4. Sign in as the dedicated automation Google account and run:

   ```bash
   python3 -m tbyn_bot.google_oauth_setup
   ```

5. Keep the generated `google-oauth-token.json` private.
6. Set `GOOGLE_AUTH_MODE=oauth`.
7. Set `GOOGLE_OAUTH_CLIENT_SECRETS_FILE` and `GOOGLE_OAUTH_TOKEN_FILE` to those local JSON paths.
8. Set `GOOGLE_MEETING_SLIDES_TEMPLATE_ID` from the template deck URL.
9. Set `GOOGLE_MEETING_SLIDES_FOLDER_ID` from the Drive folder URL.

The template deck must contain three slide designs with these placeholders:

```text
{{MEETING_TITLE}}
{{AGENDA_TITLE}}
{{AGENDA_ITEM_TITLE}}
{{AGENDA_ITEM_BODY}}
```

The item body placeholder is replaced with:

```text
Date:
Time:
Venue:
```

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
GOOGLE_AUTH_MODE
GOOGLE_OAUTH_CLIENT_SECRETS_FILE
GOOGLE_OAUTH_TOKEN_FILE
GOOGLE_MEETING_SLIDES_TEMPLATE_ID
GOOGLE_MEETING_SLIDES_FOLDER_ID
```

For deployment, store OAuth client secrets and the generated OAuth token as private files or deployment secrets. Do not commit real Google JSON credentials, OAuth tokens, spreadsheet IDs, or Drive IDs.

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
    meeting_slides.py
  utils/
    cleanup.py
  workflows/
    registry.py
    event_poll/
    monthly_summary/
    create_meeting_slides/
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
<summary>Create Meeting Slides Workflow</summary>

In a Telegram group, an admin sends:

```text
/create_meeting_slides TBYN Meeting May 2026
1. Confirmation of Last Meeting Minutes

2. Chairperson's Update

3. Completed Events
   a. Monthly Football - Apr (11 Apr)
   b. TPTB EMA + EG (25 Apr)
```

The bot copies the configured template deck into the configured Drive folder, creates slides from the agenda, and replies with the new Google Slides link.

Numbered lines such as `1.` and `2.` become section title slides. Alphabetic or roman-numeral lines such as `a.`, `b.`, `i.`, and `ii.` become title-and-body slides. Each body starts with:

```text
Date:
Time:
Venue:
```

Workflow docs: `tbyn_bot/workflows/create_meeting_slides/README.md`

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
