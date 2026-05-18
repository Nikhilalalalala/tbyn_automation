# Event Poll Workflow

This workflow lets a Telegram group admin create a quick event attendance poll.

## Command

```text
/poll_event Meeting on 6th June
```

The text after `/poll_event` becomes the poll title exactly as written.

## Poll Behaviour

The bot sends a non-anonymous, single-choice Telegram poll to the same group.

Example poll title:

```text
Meeting on 6th June
```

The bot randomly picks one yes-style option and one no-style option from the variation lists in `polls.py`.

## Access Control

Only Telegram group admins can create polls. The workflow checks the sender through Telegram's chat member API and allows users with status `creator` or `administrator`.

## Validation Messages

If the command is missing a title, or a non-admin tries to use the command, the bot posts a short message in the group and schedules that message for deletion after 20 seconds.

## Main Files

- `commands.py`: parses `/poll_event`.
- `handler.py`: handles Telegram updates, admin checks, and sending polls.
- `messages.py`: user-facing validation and permission messages.
- `permissions.py`: admin status rules.
- `polls.py`: poll payload and option variations.

