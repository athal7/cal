# cal-automation package

Python package with entry point `cal-automation {babysitter,family,lunch,sync}`. Tests: `python3 -m unittest discover -s tests -q`.

## Config source

All calendar config comes from `$XDG_CONFIG_HOME/cal/config.json` (default `~/.config/cal/config.json`):
- `calendars` — calendar names, sync rules, inbound windows, ignore patterns
- `feeds` — ICS feed URLs for family-scheduler
- `reminders` — reminders list config for babysitter-check; `sites` — other family event APIs

## Dependencies

- `icalendar` (third-party) — declared in `pyproject.toml`, installed with the tool. Used only by `family.py` for ICS feed parsing (lazy import with ImportError fallback).
- `ical` CLI and `remindctl` — called via subprocess from `util.py` and subcommand modules.

## util.py patterns

- `ical_bin()` uses `functools.lru_cache` — cached for process lifetime, no repeated `which` calls.
- `ical()` catches `json.JSONDecodeError` and returns `[]` — ical CLI can return non-JSON on errors.
- `log(msg, tag)` writes to both stdout and syslog via `logger -t`. Each subcommand passes its own tag to preserve per-service log identity.
