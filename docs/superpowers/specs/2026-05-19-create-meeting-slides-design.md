# Create Meeting Slides Workflow Design

## Goal

Add a Telegram workflow that lets a group admin paste a structured meeting agenda and receive a Google Slides deck link. The deck is generated from an existing Google Slides template so TBYN styling, layouts, logos, and page size stay controlled in Google Slides rather than in code.

## Command

The workflow command is:

```text
/create_meeting_slides TBYN Meeting May 2026
<agenda text>
```

The text after `/create_meeting_slides` on the first line is the deck title. The remaining lines are the agenda body. The bot replies in the same Telegram group with a link to the created deck.

If the deck title or agenda body is missing, the bot sends a temporary usage message.

## Access Control

The command is group-only and admin-only, matching the existing workflow behavior:

- Ignore direct messages.
- Check the sender's group role with Telegram `getChatMember`.
- Allow `creator` and `administrator`.
- Send temporary validation replies for non-admin users, permission check failures, and validation errors.
- Do not delete the user's original command message.

## Google Template Model

The workflow copies a configured template deck, then builds the final deck inside the copy.

Required configuration:

- `GOOGLE_MEETING_SLIDES_TEMPLATE_ID`: source template presentation ID.
- `GOOGLE_MEETING_SLIDES_FOLDER_ID`: target Drive folder ID.

The target Drive folder must be shared with the Google service account. The service account must have permission to copy the template and create files in the folder.

The template deck must contain exactly one slide for each of these placeholder designs:

- `{{MEETING_TITLE}}`: opening title slide design.
- `{{AGENDA_TITLE}}`: numbered section title slide design.
- `{{AGENDA_ITEM_TITLE}}`: content slide design for sub-items.

The content slide must also include `{{AGENDA_ITEM_BODY}}`. It is replaced with this fixed starter body:

```text
Date:
Time:
Venue:
```

## Agenda Parsing

Parsing is intentionally simple and line-based so volunteers can predict the result.

### Input Separation

The first line contains the command and deck title:

```text
/create_meeting_slides TBYN Meeting May 2026
```

Everything after the first newline is the agenda body. Blank lines in the agenda body are ignored.

### Numbered Section Lines

A line creates a section title slide when, after trimming leading whitespace, it matches this shape:

```text
<digits>. <title text>
```

The dot must be followed by at least one space or tab. Numbered labels are parsed before sub-item labels.

Examples:

```text
1. Confirmation of Last Meeting Minutes
2. Chairperson's Update
10. AOBs
```

The numeric label and following dot are removed from the slide title. Leading and trailing whitespace around the remaining title is trimmed.

Example:

```text
3. Completed Events
```

creates a section title slide with:

```text
Completed Events
```

### Sub-Item Lines

A line creates a content slide when, after trimming leading whitespace, it matches this shape:

```text
<sub-item label>. <title text>
```

The dot must be followed by at least one space or tab. Supported sub-item labels are:

- alphabetic labels: one letter from `a` through `z`, case-insensitive
- roman numeral labels: lowercase or uppercase roman numerals using `i`, `v`, `x`, `l`, `c`, `d`, and `m`

Examples:

```text
a. Monthly Football - Apr (11 Apr)
b. TPTB EMA + EG (25 Apr)
i. Comparative Statements
ii. Bank Signatories
```

The label and following dot are removed from the slide title. Leading and trailing whitespace around the remaining title is trimmed.

Example:

```text
   a. Bahru Mania!
```

creates a content slide with top title:

```text
Bahru Mania!
```

The body is prefilled with:

```text
Date:
Time:
Venue:
```

### Indentation

Indentation is not semantically significant. It is accepted for readability only.

These two lines produce the same slide:

```text
a. Birthdays
    a. Birthdays
```

### Label Collisions

Single-letter roman numerals such as `i.` and `v.` are also alphabetic labels. This does not matter because both alphabetic labels and roman numeral labels produce the same content slide type.

Top-level numbered labels always take precedence over sub-item labels.

Sub-item roman numerals are validated only as label-like roman numeral text, not as mathematically valid roman numbers. For example, `iiii. Topic` is accepted as a content slide because the purpose is agenda formatting, not roman numeral correctness.

### Unrecognized Lines

Any non-blank agenda line that does not match a numbered section label or a sub-item label is invalid. The bot should fail the command with a temporary validation message that points to the first invalid line.

This avoids silently dropping agenda content.

### Slide Order

Generated slides follow this order:

1. One opening title slide using the deck title and `{{MEETING_TITLE}}`.
2. One slide for each parsed agenda line, in input order.

Example input:

```text
/create_meeting_slides TBYN Meeting May 2026
1. Confirmation of Last Meeting Minutes

2. Chairperson's Update

3. Completed Events
   a. Monthly Football - Apr (11 Apr)
   b. TPTB EMA + EG (25 Apr)
```

Produces:

```text
Opening title slide: TBYN Meeting May 2026
Section title slide: Confirmation of Last Meeting Minutes
Section title slide: Chairperson's Update
Section title slide: Completed Events
Content slide: Monthly Football - Apr (11 Apr)
Content slide: TPTB EMA + EG (25 Apr)
```

## Google Slides Generation

The Google integration will:

1. Copy the configured template presentation into the configured Drive folder, using the deck title as the copied file name.
2. Inspect slides in the copied deck to find the placeholder slides.
3. Duplicate the appropriate placeholder slide for each planned output slide.
4. Replace placeholders in duplicated slides:
   - `{{MEETING_TITLE}}` with the deck title.
   - `{{AGENDA_TITLE}}` with a numbered section title.
   - `{{AGENDA_ITEM_TITLE}}` with a sub-item title.
   - `{{AGENDA_ITEM_BODY}}` with:

     ```text
     Date:
     Time:
     Venue:
     ```
5. Delete the original placeholder slides from the copied deck.
6. Return the standard Google Slides URL.

The implementation should keep Google API request construction in `tbyn_bot/integrations/`, not in the Telegram handler.

## Code Structure

Add:

```text
tbyn_bot/workflows/create_meeting_slides/
  README.md
  __init__.py
  commands.py
  agenda.py
  handler.py
  messages.py
  runner.py
```

Add Google integration code under:

```text
tbyn_bot/integrations/google_slides.py
```

Update:

- `tbyn_bot/config.py`
- `tbyn_bot/workflows/registry.py`
- `tbyn_bot/bot_commands.py`
- `.env.example`
- `README.md`
- `requirements.txt` comments if useful

## Error Handling

Expected user-facing validation errors:

- Missing deck title.
- Missing agenda body.
- Invalid agenda line.
- Missing Google configuration.
- Missing required template placeholders.
- Google API failure while copying or editing the deck.

For Google API failures, the Telegram reply should be concise and not expose tokens, file paths, or service account details.

## Testing

Use `unittest`.

Add focused tests for:

- command parsing with deck title and agenda body.
- missing deck title.
- missing agenda body.
- numbered agenda line parsing.
- alphabetic sub-item parsing.
- roman numeral sub-item parsing.
- indentation tolerance.
- invalid agenda line reporting.
- slide plan ordering, including opening title slide first.
- content slide body prefill: `Date:`, `Time:`, and `Venue:`.
- handler admin checks and temporary replies.
- runner config validation.
- runner calling Google integration with expected template ID, folder ID, deck title, and slide plan.

The normal test suite must not call real Google APIs.

## Out Of Scope

- Editing slide body content from Telegram.
- Uploading screenshots or images into generated slides.
- Scheduling slide generation.
- Sharing permissions beyond placing the file in the configured folder.
- AI summarization or rewriting of agenda text.
