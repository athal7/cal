"""cal — calendar management automations via the ical CLI.

Run subcommands on a schedule as needed; sync includes the lunch guard.
Config: $XDG_CONFIG_HOME/cal/config.json (default ~/.config/cal/config.json).

Subcommands:
    sync        Mirror busy blocks between configured calendars.
    lunch       Block lunch on calendar when meetings threaten the 11am–1pm window.
    family      Fetch events from ICS feeds and add conflict-free ones to a family calendar.
    babysitter  Flag evening/weekend events that may need babysitter coverage.

Usage:
    cal-automation <subcommand>
"""
import sys, traceback


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(0 if sys.argv[1:] in (["-h"], ["--help"]) else 1)

    subcommand = sys.argv[1]

    if subcommand == "babysitter":
        from cal.babysitter import main as cmd_main
    elif subcommand == "family":
        from cal.family import main as cmd_main
    elif subcommand == "lunch":
        from cal.lunch import main as cmd_main
    elif subcommand == "sync":
        from cal.sync import main as cmd_main
    else:
        print(f"Unknown subcommand: {subcommand}", file=sys.stderr)
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)

    try:
        cmd_main()
    except Exception as e:
        from cal.util import log
        log(f"FATAL: {e}", subcommand)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
