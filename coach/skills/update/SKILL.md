---
name: update
description: Check for and install updates to the Garmin running coach template from GitHub while preserving all personal data, logs, profile notes, and custom skills. Use when the athlete types /update or asks to update.
---

Check for and install updates to the Garmin running coach.

1. Run `uv run scripts/update.py` in the terminal.
2. Review the output:
   - If an update was installed, explain in plain words what was updated.
   - Reassure the athlete that their `athlete/` folder (profile, notes, logs, and custom skills) and `plan/` folder were completely preserved and untouched.
   - If the script mentions restarting or reloading the assistant session to load new tools or commands, let them know.
   - If it was already up to date, let them know they are running the latest version.
