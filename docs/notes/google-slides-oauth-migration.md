# Google Slides OAuth Migration Note

## Issue Faced

The `/create_meeting_slides` workflow currently uses the Google service account from `GOOGLE_SERVICE_ACCOUNT_FILE` to copy a template Google Slides deck into a Drive folder.

When testing against a folder from a personal Gmail Drive setup, Google returned:

```text
HttpError 403
The user's Drive storage quota has been exceeded.
reason: storageQuotaExceeded
```

The folder had been shared with the service account, but folder access did not solve the problem. During `drive.files.copy`, Google treats the authenticated identity as the file creator/owner. In this workflow, that identity is the service account, so the copy operation can hit service-account Drive ownership/quota limitations.

Shared Drives would avoid this by making generated files owned by the Shared Drive, but Shared Drives are only available in Google Workspace. The current setup uses a personal Gmail account, so Shared Drives are not available.

## Decision

Move the Google Slides/Drive write path from service account auth to OAuth user auth.

The safest practical setup is:

1. Create a dedicated Google account for the bot, for example `tbyn.automation@gmail.com`.
2. Keep only TBYN automation files in that account.
3. Authorize the bot once with OAuth using that dedicated account.
4. Store the OAuth refresh token locally or in deployment secrets.
5. Use that OAuth identity to copy the template deck and create generated decks.

This limits blast radius at the account boundary. Google OAuth scopes cannot be restricted to a single Drive folder, so a dedicated bot account is the main practical permission boundary.

## Implementation Plan

Add OAuth support for Google Slides/Drive while keeping the current service-account Sheets workflow unchanged unless we explicitly decide to migrate Sheets too.

Suggested config:

```text
GOOGLE_AUTH_MODE=service_account|oauth
GOOGLE_OAUTH_CLIENT_SECRETS_FILE=google-oauth-client.json
GOOGLE_OAUTH_TOKEN_FILE=google-oauth-token.json
```

Recommended behavior:

- `monthly_summary` can continue using service account auth for Google Sheets.
- `create_meeting_slides` should use OAuth when `GOOGLE_AUTH_MODE=oauth`.
- Keep `GOOGLE_MEETING_SLIDES_TEMPLATE_ID` and `GOOGLE_MEETING_SLIDES_FOLDER_ID`.
- Keep an app-level allowlist: the bot should only copy from the configured template ID and only write into the configured folder ID.
- Do not commit OAuth client secrets, refresh tokens, service account JSON, or real Drive IDs.

Possible OAuth scopes:

```text
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/presentations
```

`drive.file` is narrower, but may not reliably support copying an existing template into a configured folder unless the app created or was explicitly granted the relevant files through the OAuth app flow. For reliability, use the broader Drive scope only with the dedicated bot Google account.

## Setup Steps For Next Session

1. In Google Cloud Console, enable:
   - Google Drive API
   - Google Slides API
   - Google Sheets API, if continuing monthly summary in the same project
2. Create an OAuth client ID:
   - Application type: Desktop app
   - Download the client secrets JSON
3. Add a local setup command/script to run the OAuth consent flow and write `GOOGLE_OAUTH_TOKEN_FILE`.
4. Update `tbyn_bot/integrations/meeting_slides.py` to build Drive/Slides clients from OAuth credentials when configured.
5. Add tests using fake credential/client builders. The normal unit suite must not call real Google APIs.
6. Update `.env.example`, root `README.md`, and workflow README with OAuth setup.
