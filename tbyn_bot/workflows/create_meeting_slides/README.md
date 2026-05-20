# Create Meeting Slides Workflow

This workflow creates a Google Slides meeting deck from a Telegram agenda message.

In a Telegram group, an admin sends:

```text
/create_meeting_slides TBYN Meeting May 2026
1. Confirmation of Last Meeting Minutes

2. Chairperson's Update

3. Completed Events
   a. Monthly Football - Apr (11 Apr)
   b. TPTB EMA + EG (25 Apr)
```

The bot copies the configured Google Slides template into the configured Drive folder, fills slides from the agenda, and replies with the new deck link.

## Template Placeholders

The template deck must contain one slide for each design:

```text
{{MEETING_TITLE}}
{{AGENDA_TITLE}}
{{AGENDA_ITEM_TITLE}}
{{AGENDA_ITEM_BODY}}
```

`{{MEETING_TITLE}}` is used for the first slide. `{{AGENDA_TITLE}}` is used for numbered agenda section slides. `{{AGENDA_ITEM_TITLE}}` and `{{AGENDA_ITEM_BODY}}` are used for item slides.

Item slides get this fixed starter body:

```text
Date:
Time:
Venue:
```

## Agenda Parsing

Blank lines are ignored.

Numbered lines create section title slides:

```text
1. Confirmation of Last Meeting Minutes
```

Alphabetic and roman-numeral lines create item slides:

```text
a. Bahru Mania!
ii. Bank Signatories
```

Any other non-blank line is rejected so agenda content is not silently dropped.

## Configuration

Meeting slides use Google Drive and Google Slides. OAuth user auth is recommended so decks are created by a dedicated Google automation account.

Set:

```text
GOOGLE_AUTH_MODE=oauth
GOOGLE_OAUTH_CLIENT_SECRETS_FILE=google-oauth-client.json
GOOGLE_OAUTH_TOKEN_FILE=google-oauth-token.json
GOOGLE_MEETING_SLIDES_TEMPLATE_ID=your-template-presentation-id
GOOGLE_MEETING_SLIDES_FOLDER_ID=your-output-folder-id
```

Setup:

1. Create or choose a dedicated Google account for TBYN automation.
2. Enable the Google Drive API and Google Slides API in Google Cloud Console.
3. Create an OAuth client ID with application type `Desktop app`.
4. Download the OAuth client secrets JSON as `google-oauth-client.json`.
5. Sign in as the automation account and run:

   ```bash
   python3 -m tbyn_bot.google_oauth_setup
   ```

6. Keep `google-oauth-client.json` and `google-oauth-token.json` private.
7. Keep `GOOGLE_MEETING_SLIDES_TEMPLATE_ID` and `GOOGLE_MEETING_SLIDES_FOLDER_ID` pointed at the approved template deck and output folder.

Do not commit real Google OAuth credential JSON files, OAuth tokens, spreadsheet IDs, or Drive IDs.
