# Requirements: TBYN Telegram Poll Bot v1

## Scope

Build the cheapest and easiest first version of a Telegram bot workflow for Tiong Bahru Youth Network (TBYN). 

This v1 focuses only on sending an event attendance poll from a Telegram group command. It does not include Google Sheets, Gmail, reminders, monthly summaries, schedulers, or WhatsApp.

The implementation should still be structured so future workflows can be added without rewriting the bot. Future workflows may include scheduled polls, Google Sheets-backed configuration, event summaries, reminders, attendance exports, and other TBYN volunteer operations.

## Primary Workflow

A user sends a command in a Telegram group with one required argument: the poll title.

Example:

```text
/poll_event Meeting on 6th June
```

The bot sends a poll to the same Telegram group.

Poll question:

```text
Meeting on 6th June
```

Poll options:

```text
Yes, I'll be there!
Sorry, I'll join next time
```

## Acceptance Criteria

1. The bot can be added to a Telegram group.
2. The bot listens for the `/poll_event` group command with a poll title argument.
3. The poll title argument may contain spaces, such as `Meeting on 6th June`.
4. The poll title is treated as display text for v1.
5. The bot sends the poll to the same group where the command was used.
6. The poll question is exactly the title supplied after `/poll_event`.
7. The poll has exactly two options: one randomly selected yes-style option and one randomly selected no-style option.
8. The poll is non-anonymous.
9. The poll allows only one selected option per voter.
10. The poll stays open indefinitely.
11. Only Telegram group admins can trigger the command successfully.
12. Non-admin users cannot create polls with this command.
13. The implementation does not require Google Sheets or any spreadsheet configuration.
14. The implementation favors the cheapest and easiest viable workflow.
15. The code is modular enough to add future workflows without replacing the command parser, Telegram client, configuration loading, or deployment approach.

## Recommended V1 Technical Direction

Use a small Telegram Bot API implementation hosted on a cheap cloud platform.

Reasoning:

- Cheap cloud hosting is easier to keep online than running the bot from a laptop.
- A small bot avoids Google Apps Script complexity while the current requirement is Telegram-only.
- The code can still be run locally for development before deployment.

The bot token should be read from an environment variable, not committed to the repository.

Suggested environment variable:

```text
TELEGRAM_BOT_TOKEN
```

The design should separate:

1. Command parsing.
2. Permission checks.
3. Poll message construction.
4. Telegram API calls.
5. Configuration.
6. Application startup.

This keeps the first workflow small while leaving a clean path for later TBYN workflows.

## Admin-Only Access

The bot must check whether the command sender is a Telegram group admin before creating the poll.

Implementation requirement:

1. Use Telegram's chat member/admin APIs to verify the sender.
2. Allow users whose status is `creator` or `administrator`.
3. Reject regular members.
4. Log rejected attempts without exposing unnecessary personal data.

## User-Only Error Replies

Telegram does not provide a true ephemeral, user-only reply for a normal group slash command.

For v1, use this behavior:

1. If an admin uses the command correctly, the bot posts the poll in the group.
2. If the command is invalid, the bot posts a short validation message in the group.
3. The validation message should mention the user when Telegram user data allows it.
4. The validation message should be deleted after 20 seconds if the bot has delete-message permissions.
5. If the bot cannot delete the validation message, it should leave the message in place and log the cleanup failure.

Future option:

Use inline buttons for interactions that need true user-only notifications, because Telegram callback query answers can be shown only to the user who pressed the button.

## Assumptions

1. The bot will use the official Telegram Bot API.
2. Poll results will be viewed directly in Telegram.
3. No attendance export is required in v1.
4. No validation is performed to confirm the poll title contains a real calendar date.
5. The command creates the poll immediately.
6. The bot only needs to work in Telegram groups for this slice.
7. Missing configuration and operational governance will be decided later.
8. The bot may need admin permissions in the group to verify admins reliably and clean up fallback messages.
9. The bot needs delete-message permissions if validation messages should be reliably removed after 20 seconds.

## Non-Goals

1. No Google Sheets integration.
2. No Apps Script implementation for this slice unless later requested.
3. No monthly event summary.
4. No Gmail or WhatsApp reminders.
5. No attendance export.
6. No recurring meeting automation.
7. No date parsing, timezone logic, or calendar validation.
8. No poll closing behavior.
9. No admin dashboard.
10. No user registration or identity mapping outside Telegram.

## Open Questions Before Implementation

1. Should the first implementation be Node.js or Python?
2. Which cheap cloud host should be used first?
3. Should non-admin attempts get the same temporary group message behavior as validation errors, or should they be ignored silently?
4. Should the bot delete the original invalid command message too, or only delete its own validation reply?
