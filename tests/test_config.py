"""XDG configuration loading behavior."""

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from cal.family import occupied_slots
from cal.util import config_data


class TestConfigData(unittest.TestCase):
    def test_uses_xdg_config_home_over_home(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            custom = root / "custom" / "cal"
            custom.mkdir(parents=True)
            (custom / "config.json").write_text(json.dumps({"calendars": {"work": {"name": "Work"}}}))
            fallback = root / ".config" / "cal"
            fallback.mkdir(parents=True)
            (fallback / "config.json").write_text(json.dumps({"calendars": {}}))
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(custom.parent)}), patch("pathlib.Path.home", return_value=root):
                self.assertEqual(config_data()["calendars"]["work"]["name"], "Work")

    def test_relative_xdg_path_uses_home_default(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / ".config" / "cal"
            config.mkdir(parents=True)
            (config / "config.json").write_text('{"feeds": {"community": "https://example.com/feed.ics"}}')
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": "relative"}), patch("pathlib.Path.home", return_value=root):
                self.assertEqual(config_data()["feeds"]["community"], "https://example.com/feed.ics")

    def test_missing_and_invalid_config_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "cal" / "config.json"
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": directory}):
                with self.assertRaises(FileNotFoundError):
                    config_data()
                config.parent.mkdir()
                config.write_text("{not json")
                with self.assertRaisesRegex(ValueError, "Invalid JSON in .*config.json"):
                    config_data()
                config.write_text("[]")
                with self.assertRaisesRegex(ValueError, "must contain a JSON object"):
                    config_data()


class TestCalendarMappings(unittest.TestCase):
    def test_metadata_does_not_become_calendar_when_finding_busy_slots(self):
        calendars = {"work": {"name": "Work"}, "syncExclude": {"Focus Time": "work"}}
        event = {"start_date": "2026-06-15T09:00:00Z", "end_date": "2026-06-15T10:00:00Z", "availability": "busy"}
        with patch("cal.family.ical", return_value=[event]) as cli:
            slots = occupied_slots(calendars, "2026-06-15", "2026-06-16", timezone.utc)
        self.assertEqual(slots, [(datetime(2026, 6, 15, 9, tzinfo=timezone.utc),
                                  datetime(2026, 6, 15, 10, tzinfo=timezone.utc))])
        self.assertEqual(cli.call_count, 1)


if __name__ == "__main__":
    unittest.main()
