# cal-automation

Calendar automations using [`ical`](https://github.com/BRO3886/ical). The `cal-automation` command provides `sync`, `lunch`, `family`, and `babysitter`; `sync` also runs the lunch guard.

## Install

```sh
uv tool install --from git+https://github.com/athal7/cal.git@v0.2.0 cal-automation
cal-automation --help
```

Python's `icalendar` library is installed with the tool. The external `ical` CLI must be on `PATH`; `babysitter` also requires `remindctl`. Calendar access and Reminders permissions belong to those host tools.

## Configure

Create `$XDG_CONFIG_HOME/cal/config.json`, or `~/.config/cal/config.json` when `XDG_CONFIG_HOME` is unset or relative. The file must contain a JSON object. Keep it private: it contains your calendar names and feed URLs. For example:

```sh
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
case "$config_home" in /*) ;; *) config_home="$HOME/.config" ;; esac
mkdir -p "$config_home/cal"
# Write your JSON there, then restrict access:
chmod 600 "$config_home/cal/config.json"
```

Example `config.json` (replace names, URLs, and list names with your own):

```json
{
  "calendars": {
    "personal": {
      "name": "Personal",
      "sync_to": ["work"],
      "family_scheduler_target": true,
      "babysitter_check": true
    },
    "work": {
      "name": "Work",
      "sync_to": ["personal"],
      "lunch_guard": true,
      "inbound_start": 9,
      "inbound_end": 17,
      "inbound_days": ["mon", "tue", "wed", "thu", "fri"],
      "ignore_patterns": ["Do Not Copy"],
      "title_mappings": {"planning": "Busy"},
      "default_title": "Busy",
      "ooo_all_day": true
    }
  },
  "feeds": {"community": "https://example.com/calendar.ics"},
  "sites": {
    "events": {
      "strategy": "tribe_rest",
      "base_url": "https://events.example.com",
      "categories": ["family"],
      "days": 14
    }
  },
  "reminders": {"personal": {"name": "Personal", "babysitter_reminders": true}}
}
```

`calendars` is keyed by your own labels; each calendar needs an `ical` name. `sync_to` names destination labels. Optional sync settings include `lookahead_weeks`, `ignore_patterns`, `passthrough`, `ooo_all_day`, `default_title`, `title_mappings`, and destination `inbound_start`, `inbound_end`, `inbound_days` (three-letter weekday names). `syncExclude` maps exact event titles to source labels under `calendars`. `lunch_guard`, `family_scheduler_target`, and `babysitter_check` select calendars for those jobs; `babysitter_ignore_patterns` filters titles. `feeds` maps labels to ICS URLs. `sites` maps labels to API configurations: `tribe_rest` uses `base_url`, optional `categories` and `days`; `communico` uses `base_url`, optional `client`, `ages`, and `days`. `reminders` maps labels to lists with `name`; mark the target with `babysitter_reminders`.

Run only the subcommands you configure: `cal-automation sync`, `cal-automation family`, `cal-automation babysitter`, or `cal-automation lunch`. A missing, malformed, or non-object config fails instead of silently skipping scheduled work.

Run the tests from a checkout with `python3 -m unittest discover -s tests -q`.

Licensed under [MIT](LICENSE).
