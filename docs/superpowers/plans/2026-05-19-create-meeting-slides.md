# Create Meeting Slides Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Telegram admin command that creates a Google Slides meeting deck from a template and replies with the deck link.

**Architecture:** Keep the workflow in `tbyn_bot/workflows/create_meeting_slides/`, with pure command and agenda parsing separated from Telegram handling. Keep Google Drive/Slides API request construction in `tbyn_bot/integrations/google_slides.py`, and call it through a runner that validates config.

**Tech Stack:** Python 3.11, `unittest`, official Telegram Bot API wrapper already in repo, Google API Python client already in `requirements.txt`.

---

## File Map

- Create `tbyn_bot/workflows/create_meeting_slides/commands.py`: parse `/create_meeting_slides` into deck title and agenda body.
- Create `tbyn_bot/workflows/create_meeting_slides/agenda.py`: parse agenda lines into a slide plan.
- Create `tbyn_bot/workflows/create_meeting_slides/messages.py`: user-facing messages.
- Create `tbyn_bot/workflows/create_meeting_slides/runner.py`: validate config and call Google integration.
- Create `tbyn_bot/workflows/create_meeting_slides/handler.py`: Telegram admin command handler.
- Create `tbyn_bot/workflows/create_meeting_slides/__init__.py`: exported command and handler.
- Create `tbyn_bot/workflows/create_meeting_slides/README.md`: workflow docs.
- Create `tbyn_bot/integrations/google_slides.py`: copy template, duplicate slides, replace placeholders, delete template marker slides.
- Modify `tbyn_bot/config.py`: add meeting slides template/folder config.
- Modify `tbyn_bot/workflows/registry.py`: register new handler.
- Modify `tbyn_bot/bot_commands.py`: add command suggestion.
- Modify `.env.example` and `README.md`: document setup and command.
- Create tests:
  - `tests/test_create_meeting_slides_commands.py`
  - `tests/test_create_meeting_slides_agenda.py`
  - `tests/test_create_meeting_slides_runner.py`
  - `tests/test_create_meeting_slides_handler.py`
  - `tests/test_google_slides.py`

## Task 1: Pure Command And Agenda Parsing

**Files:**
- Create: `tbyn_bot/workflows/create_meeting_slides/commands.py`
- Create: `tbyn_bot/workflows/create_meeting_slides/agenda.py`
- Create: `tbyn_bot/workflows/create_meeting_slides/__init__.py`
- Test: `tests/test_create_meeting_slides_commands.py`
- Test: `tests/test_create_meeting_slides_agenda.py`

- [ ] **Step 1: Write failing command parser tests**

Use `unittest`. Cover:

```python
from tbyn_bot.workflows.create_meeting_slides.commands import (
    CREATE_MEETING_SLIDES_COMMAND,
    parse_create_meeting_slides_command,
)


def test_parse_command_with_title_and_agenda(self):
    parsed = parse_create_meeting_slides_command(
        "/create_meeting_slides TBYN Meeting May 2026\n1. Opening"
    )
    self.assertEqual(CREATE_MEETING_SLIDES_COMMAND, "/create_meeting_slides")
    self.assertEqual(parsed.deck_title, "TBYN Meeting May 2026")
    self.assertEqual(parsed.agenda_text, "1. Opening")
    self.assertTrue(parsed.has_deck_title)
    self.assertTrue(parsed.has_agenda_text)


def test_parse_command_without_agenda(self):
    parsed = parse_create_meeting_slides_command(
        "/create_meeting_slides TBYN Meeting May 2026"
    )
    self.assertEqual(parsed.deck_title, "TBYN Meeting May 2026")
    self.assertEqual(parsed.agenda_text, "")
    self.assertTrue(parsed.has_deck_title)
    self.assertFalse(parsed.has_agenda_text)


def test_parse_non_matching_command_returns_none(self):
    self.assertIsNone(parse_create_meeting_slides_command("/events_this_month"))
```

- [ ] **Step 2: Run command parser tests and confirm RED**

Run: `python3 -m unittest tests.test_create_meeting_slides_commands -v`

Expected: import failure for missing module or function.

- [ ] **Step 3: Implement command parser**

Implement a dataclass `ParsedCreateMeetingSlidesCommand` with `deck_title`, `agenda_text`, `has_deck_title`, `has_agenda_text`. Match only `/create_meeting_slides` with optional bot mention suffix support matching existing command style if present elsewhere.

- [ ] **Step 4: Run command parser tests and confirm GREEN**

Run: `python3 -m unittest tests.test_create_meeting_slides_commands -v`

Expected: all tests pass.

- [ ] **Step 5: Write failing agenda parser tests**

Cover:

```python
from tbyn_bot.workflows.create_meeting_slides.agenda import (
    CONTENT_BODY_PREFILL,
    SlideKind,
    parse_agenda,
)


def test_parse_agenda_builds_opening_and_items(self):
    slides = parse_agenda(
        "TBYN Meeting May 2026",
        "1. Confirmation\n\n2. Updates\n   a. Bahru Mania!\n   ii. Bank Signatories",
    )
    self.assertEqual([slide.kind for slide in slides], [
        SlideKind.MEETING_TITLE,
        SlideKind.AGENDA_TITLE,
        SlideKind.AGENDA_TITLE,
        SlideKind.AGENDA_ITEM,
        SlideKind.AGENDA_ITEM,
    ])
    self.assertEqual(slides[0].title, "TBYN Meeting May 2026")
    self.assertEqual(slides[1].title, "Confirmation")
    self.assertEqual(slides[3].title, "Bahru Mania!")
    self.assertEqual(slides[3].body, CONTENT_BODY_PREFILL)


def test_invalid_line_reports_line_number_and_text(self):
    with self.assertRaises(ValueError) as context:
        parse_agenda("Deck", "1. Good\nThis is invalid")
    self.assertIn("line 2", str(context.exception))
    self.assertIn("This is invalid", str(context.exception))
```

- [ ] **Step 6: Run agenda tests and confirm RED**

Run: `python3 -m unittest tests.test_create_meeting_slides_agenda -v`

Expected: missing module/function failures.

- [ ] **Step 7: Implement agenda parser**

Use regexes:

- numbered: `^\s*(\d+)\.\s+(.+?)\s*$`
- sub-item: `^\s*([A-Za-z]|[ivxlcdmIVXLCDM]+)\.\s+(.+?)\s*$`

Define:

```python
CONTENT_BODY_PREFILL = "Date:\nTime:\nVenue:"
```

Return opening title slide first, then one slide per non-blank agenda line. Raise `ValueError` for the first invalid non-blank line.

- [ ] **Step 8: Run agenda tests and confirm GREEN**

Run: `python3 -m unittest tests.test_create_meeting_slides_agenda -v`

Expected: all tests pass.

## Task 2: Google Slides Integration

**Files:**
- Create: `tbyn_bot/integrations/google_slides.py`
- Test: `tests/test_google_slides.py`

- [ ] **Step 1: Write failing unit tests for request planning helpers**

Avoid real Google API calls. Test pure helper behavior for placeholder detection and request creation. Cover:

- finds slide object IDs containing `{{MEETING_TITLE}}`, `{{AGENDA_TITLE}}`, `{{AGENDA_ITEM_TITLE}}`
- raises `RuntimeError` when a required placeholder is missing
- builds duplicate, replaceAllText, and deleteObject requests for a small slide plan

- [ ] **Step 2: Run tests and confirm RED**

Run: `python3 -m unittest tests.test_google_slides -v`

Expected: missing module/function failures.

- [ ] **Step 3: Implement Google integration**

Expose:

```python
def create_meeting_slides_from_template(
    template_presentation_id: str,
    output_folder_id: str,
    deck_title: str,
    slides: list,
    service_account_file: str,
) -> str:
    ...
```

Use scopes:

```python
[
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/presentations",
]
```

Use Drive API to copy the template into the folder. Use Slides API to get the copied deck, find placeholder slides, batchUpdate duplicate/replace/delete requests, and return:

```python
f"https://docs.google.com/presentation/d/{presentation_id}/edit"
```

- [ ] **Step 4: Run tests and confirm GREEN**

Run: `python3 -m unittest tests.test_google_slides -v`

Expected: all tests pass.

## Task 3: Runner, Config, And Telegram Handler

**Files:**
- Modify: `tbyn_bot/config.py`
- Create: `tbyn_bot/workflows/create_meeting_slides/messages.py`
- Create: `tbyn_bot/workflows/create_meeting_slides/runner.py`
- Create: `tbyn_bot/workflows/create_meeting_slides/handler.py`
- Modify: `tbyn_bot/workflows/create_meeting_slides/__init__.py`
- Modify: `tests/fakes.py` if needed
- Test: `tests/test_create_meeting_slides_runner.py`
- Test: `tests/test_create_meeting_slides_handler.py`

- [ ] **Step 1: Write failing runner tests**

Cover missing `GOOGLE_SERVICE_ACCOUNT_FILE`, missing template ID, missing folder ID, successful call into injected creator with expected deck title and parsed slides.

- [ ] **Step 2: Run runner tests and confirm RED**

Run: `python3 -m unittest tests.test_create_meeting_slides_runner -v`

Expected: missing module/config field failures.

- [ ] **Step 3: Implement config and runner**

Add config fields:

```python
google_meeting_slides_template_id: str = ""
google_meeting_slides_folder_id: str = ""
```

Read environment variables:

```python
GOOGLE_MEETING_SLIDES_TEMPLATE_ID
GOOGLE_MEETING_SLIDES_FOLDER_ID
```

Runner validates config, parses agenda, calls injected creator or `create_meeting_slides_from_template`, then sends Telegram message with the URL.

- [ ] **Step 4: Run runner tests and confirm GREEN**

Run: `python3 -m unittest tests.test_create_meeting_slides_runner -v`

Expected: all tests pass.

- [ ] **Step 5: Write failing handler tests**

Cover:

- non-command returns `False`
- direct chat command is consumed without sending
- non-admin receives temporary message
- missing title or agenda receives usage message
- valid admin command calls injected sender and sends the resulting URL/reply through runner path

- [ ] **Step 6: Run handler tests and confirm RED**

Run: `python3 -m unittest tests.test_create_meeting_slides_handler -v`

Expected: missing handler failures.

- [ ] **Step 7: Implement handler**

Follow existing `MonthlySummaryHandler` structure. Catch `ValueError` for invalid agenda and `RuntimeError` for configuration/template errors. Use temporary replies for validation and errors.

- [ ] **Step 8: Run handler tests and confirm GREEN**

Run: `python3 -m unittest tests.test_create_meeting_slides_handler -v`

Expected: all tests pass.

## Task 4: Registration And Documentation

**Files:**
- Modify: `tbyn_bot/workflows/registry.py`
- Modify: `tbyn_bot/bot_commands.py`
- Modify: `.env.example`
- Modify: `README.md`
- Create: `tbyn_bot/workflows/create_meeting_slides/README.md`
- Test: `tests/test_bot_commands.py`
- Test: existing registry/handler tests as needed

- [ ] **Step 1: Write/update failing registration docs tests**

Update bot command tests to expect `/create_meeting_slides` with a concise description.

- [ ] **Step 2: Run relevant tests and confirm RED**

Run: `python3 -m unittest tests.test_bot_commands -v`

Expected: command list assertion fails until command is registered.

- [ ] **Step 3: Register workflow and command**

Import and instantiate `CreateMeetingSlidesHandler` in registry. Add command to `BOT_COMMANDS`.

- [ ] **Step 4: Update docs**

Document command, required template placeholders, env vars, and Google API setup in root README and workflow README. Add env vars to `.env.example`.

- [ ] **Step 5: Run relevant tests and confirm GREEN**

Run:

```bash
python3 -m unittest tests.test_bot_commands -v
python3 -m unittest discover -v
python3 -m compileall -q tbyn_bot main.py tests
```

Expected: all pass.

## Final Verification

Run:

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -v
python3 -m compileall -q tbyn_bot main.py tests
```

Expected: all commands pass. If dependency install fails due network restrictions, report that and still run the local test/compile commands.
