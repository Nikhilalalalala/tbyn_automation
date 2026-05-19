import unittest

from tbyn_bot.bot.dispatcher import UpdateDispatcher
from tbyn_bot.workflows.event_poll import EventPollHandler

from tests.fakes import FakeTelegramClient, group_update


class EventPollHandlerTest(unittest.TestCase):
    def test_admin_command_sends_poll_to_same_group(self):
        client = FakeTelegramClient(admin_status="creator")
        scheduled = []
        handler = EventPollHandler(client, schedule_delete=lambda *args: scheduled.append(args))

        handled = handler.handle_update(group_update("/poll_event Meeting on 6th June"))

        self.assertTrue(handled)
        self.assertEqual(len(client.sent_polls), 1)
        chat_id, poll = client.sent_polls[0]
        self.assertEqual(chat_id, -1001)
        self.assertEqual(poll["question"], "Meeting on 6th June")
        self.assertEqual(client.sent_messages, [])
        self.assertEqual(scheduled, [])

    def test_missing_title_sends_temporary_validation_message(self):
        client = FakeTelegramClient(admin_status="administrator")
        scheduled = []
        handler = EventPollHandler(
            client,
            delete_after_seconds=20,
            schedule_delete=lambda *args: scheduled.append(args),
        )

        handled = handler.handle_update(group_update("/poll_event"))

        self.assertTrue(handled)
        self.assertEqual(client.sent_polls, [])
        self.assertEqual(client.sent_messages[0][0], -1001)
        self.assertIn("@adminuser", client.sent_messages[0][1])
        self.assertIn("Please include a poll title", client.sent_messages[0][1])
        self.assertEqual(scheduled, [(client, -1001, 202, 20)])

    def test_non_admin_gets_temporary_permission_message(self):
        client = FakeTelegramClient(admin_status="member")
        scheduled = []
        handler = EventPollHandler(
            client,
            delete_after_seconds=20,
            schedule_delete=lambda *args: scheduled.append(args),
        )

        handled = handler.handle_update(group_update("/poll_event Meeting on 6th June"))

        self.assertTrue(handled)
        self.assertEqual(client.sent_polls, [])
        self.assertIn("Only group admins", client.sent_messages[0][1])
        self.assertEqual(scheduled, [(client, -1001, 202, 20)])

    def test_admin_check_failure_fails_closed_with_temporary_message(self):
        client = FakeTelegramClient(chat_member_error=RuntimeError("api failed"))
        scheduled = []
        handler = EventPollHandler(
            client,
            delete_after_seconds=20,
            schedule_delete=lambda *args: scheduled.append(args),
        )

        with self.assertLogs(level="ERROR"):
            handled = handler.handle_update(group_update("/poll_event Meeting on 6th June"))

        self.assertTrue(handled)
        self.assertEqual(client.sent_polls, [])
        self.assertIn("could not verify admin permissions", client.sent_messages[0][1])
        self.assertEqual(scheduled, [(client, -1001, 202, 20)])

    def test_ignores_unrelated_message(self):
        client = FakeTelegramClient()
        handler = EventPollHandler(client)

        handled = handler.handle_update(group_update("hello"))

        self.assertFalse(handled)
        self.assertEqual(client.chat_member_requests, [])
        self.assertEqual(client.sent_polls, [])


class UpdateDispatcherTest(unittest.TestCase):
    def test_dispatches_to_first_handler_that_consumes_update(self):
        calls = []

        class Handler:
            def __init__(self, handled):
                self.handled = handled

            def handle_update(self, update):
                calls.append(self.handled)
                return self.handled

        dispatcher = UpdateDispatcher([Handler(False), Handler(True), Handler(True)])

        self.assertTrue(dispatcher.handle_update({"update_id": 1}))
        self.assertEqual(calls, [False, True])


if __name__ == "__main__":
    unittest.main()
