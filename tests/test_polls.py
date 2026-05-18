import unittest

from tbyn_bot.workflows.event_poll.polls import build_event_poll


class EventPollTest(unittest.TestCase):
    def test_builds_required_poll_payload(self):
        def choose_first(options):
            return options[0]

        poll = build_event_poll("Meeting on 6th June", choose_option=choose_first)

        self.assertEqual(poll["question"], "Meeting on 6th June")
        self.assertEqual(poll["options"], ["Yes, I'll be there!", "Sorry, I'll join next time"])
        self.assertIs(poll["is_anonymous"], False)
        self.assertIs(poll["allows_multiple_answers"], False)
        self.assertEqual(poll["type"], "regular")
        self.assertNotIn("open_period", poll)
        self.assertNotIn("close_date", poll)

    def test_chooses_one_yes_and_one_no_variation(self):
        calls = []

        def choose_last(options):
            calls.append(options)
            return options[-1]

        poll = build_event_poll("Meeting on 6th June", choose_option=choose_last)

        self.assertEqual(poll["options"], ["Yes, I'll be there :)", "Sorry, have fun without me"])
        self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
