"""Lunch guard behavior across calendar runs and manual deletions."""

import tempfile
import unittest
from datetime import date, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from cal import lunch


class TestLunchGuardDeletion(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        state = Path(self.directory.name) / "lunch-guard" / "state.json"
        self.addCleanup(patch.stopall)
        patch.object(lunch, "STATE_FILE", state).start()
        patch.object(lunch, "local_tz", return_value=timezone.utc).start()
        patch.object(lunch, "config_data", return_value={
            "calendars": {"work": {"name": "Work", "lunch_guard": True}}
        }).start()
        patch.object(lunch, "log").start()
        patch.object(lunch, "ical", side_effect=self.calendar_command).start()
        self.events = {}
        self.day = next(date.today() + timedelta(days=i) for i in range(1, 7)
                        if (date.today() + timedelta(days=i)).weekday() < 5)
        self.other_day = next(self.day + timedelta(days=i) for i in range(1, 7)
                              if (self.day + timedelta(days=i)).weekday() < 5)

    def calendar_command(self, *args):
        command = args[0]
        if command == "list":
            return list(self.events.get((args[args.index("-c") + 1], args[args.index("--from") + 1]), []))
        if command == "add":
            cal = args[args.index("-c") + 1]
            day = args[args.index("-s") + 1][:10]
            self.events.setdefault((cal, day), []).append({
                "id": f"guard:{cal}:{day}", "title": "Lunch", "notes": lunch.TAG,
            })
            return []
        if command == "delete":
            for events in self.events.values():
                events[:] = [event for event in events if event.get("id") != args[1]]
            return []
        raise AssertionError(f"Unexpected ical command: {command}")

    def busy(self, day):
        return {
            "title": "Meeting", "notes": "", "availability": "busy",
            "start_date": f"{day}T11:00:00Z", "end_date": f"{day}T12:00:00Z",
        }

    def guards(self, day, cal="Work"):
        return [e for e in self.events[(cal, str(day))] if e.get("notes") == lunch.TAG]

    def test_deleted_guard_stays_deleted_while_new_day_is_protected(self):
        self.events[("Work", str(self.day))] = [self.busy(self.day)]
        lunch.main()
        self.assertEqual(len(self.guards(self.day)), 1)

        self.events[("Work", str(self.day))][:] = [self.busy(self.day)]  # user deletes the guard
        self.events[("Work", str(self.other_day))] = [self.busy(self.other_day)]
        lunch.main()
        self.assertEqual(self.guards(self.day), [])
        self.assertEqual(len(self.guards(self.other_day)), 1)
        lunch.main()
        self.assertEqual(self.guards(self.day), [])

    def test_existing_guard_is_remembered_before_manual_deletion(self):
        self.events[("Work", str(self.day))] = [self.busy(self.day), {
            "id": "old-guard", "title": "Lunch", "notes": lunch.TAG,
        }]
        lunch.main()
        self.events[("Work", str(self.day))][:] = [self.busy(self.day)]
        lunch.main()
        self.assertEqual(self.guards(self.day), [])

    def test_automatic_removal_can_be_followed_by_new_guard(self):
        self.events[("Work", str(self.day))] = [self.busy(self.day)]
        lunch.main()
        self.assertEqual(len(self.guards(self.day)), 1)
        self.events[("Work", str(self.day))][:] = []  # risk passes; job removes the guard
        self.events[("Work", str(self.day))].append({
            "id": "old-guard", "title": "Lunch", "notes": lunch.TAG,
        })
        lunch.main()
        self.assertEqual(self.guards(self.day), [])
        self.events[("Work", str(self.day))] = [self.busy(self.day)]
        lunch.main()
        self.assertEqual(len(self.guards(self.day)), 1)

    def test_failed_creation_does_not_suppress_later_attempt(self):
        self.events[("Work", str(self.day))] = [self.busy(self.day)]
        with patch.object(self, "calendar_command", wraps=self.calendar_command) as cli:
            # The add command fails without creating an event.
            with patch.object(lunch, "ical", side_effect=lambda *args: [] if args[0] == "add" else cli(*args)):
                lunch.main()
        self.assertEqual(self.guards(self.day), [])
        lunch.main()
        self.assertEqual(len(self.guards(self.day)), 1)


if __name__ == "__main__":
    unittest.main()
