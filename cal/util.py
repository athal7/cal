"""Shared utilities for the cal package."""
import functools
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


@functools.lru_cache(maxsize=1)
def ical_bin():
    """Find ical binary, caching result."""
    return (
        subprocess.run(["which", "ical"], capture_output=True, text=True).stdout.strip()
        or str(Path.home() / ".local/bin/ical")
    )


def ical(*args):
    """Run ical CLI and parse JSON output."""
    result = subprocess.run([ical_bin(), *args], capture_output=True, text=True)
    try:
        return json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return []


def ical_delete(event_id):
    """Delete one event, raising so callers can preserve state on failure."""
    result = subprocess.run(
        [ical_bin(), "delete", event_id, "--force"],
        capture_output=True, text=True,
    )
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(detail or f"ical delete exited with status {result.returncode}")


def ical_write(*args):
    """Run ical CLI for write operations (no JSON parsing)."""
    subprocess.run([ical_bin(), *args], capture_output=True, text=True)


def config_data():
    """Load private JSON configuration from the XDG config directory."""
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", ""))
    if not config_home.is_absolute():
        config_home = Path.home() / ".config"
    path = config_home / "cal" / "config.json"
    try:
        with path.open(encoding="utf-8") as stream:
            data = json.load(stream)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def calendar_entries(calendars):
    """Exclude metadata mappings such as syncExclude from real calendars."""
    return {label: value for label, value in calendars.items()
            if isinstance(value, dict) and "name" in value}


def local_tz():
    """Get local timezone from /etc/localtime symlink."""
    return ZoneInfo(os.readlink("/etc/localtime").split("zoneinfo/")[-1])


def to_local(dt_str, tz):
    """Parse ISO datetime string to timezone-aware local datetime."""
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(tz)


def log(msg, tag):
    """Log to stdout and syslog."""
    print(f"{datetime.now().strftime('%H:%M:%S')} {msg}", flush=True)
    subprocess.run(["logger", "-t", tag, msg], capture_output=True)


def is_eligible(dt, evening_start=17):
    """Return True for weekends (all day) or weekday evenings (after evening_start)."""
    if dt.weekday() >= 5:
        return True
    return dt.hour >= evening_start
