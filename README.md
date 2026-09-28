# cal-automation

Calendar automations driven by [`ical`](https://github.com/BRO3886/ical), `remindctl`, and `chezmoi data`. The `cal-automation` command offers `babysitter`, `family`, `lunch`, and `sync` subcommands. `sync` also runs the lunch guard.

Install the tool into its own Python environment:

```sh
uv tool install --from git+https://github.com/athal7/cal.git@v0.1.0 cal-automation
cal-automation --help
```

The `family` subcommand's ICS parser (`icalendar`) is installed with the tool. The external `ical`, `remindctl`, and `chezmoi` commands must be on `PATH`. Calendar names, sync rules, feed URLs, and reminder lists come from machine-local `chezmoi data` (`calendars`, `feeds`, and `reminders`); no personal calendar config is bundled.

Run the tests from a checkout with `python3 -m unittest discover -s tests -q`.
