---
description: One-time setup - connect Garmin and create the athlete profile
---

Walk the athlete through setup one step at a time. Before each step, say
in one or two plain sentences what it does. Skip any step that's already
done, and say so.

1. **Check the computer.** Detect macOS or Windows. Check whether `uv` and
   `uvx` are installed (`uvx --version`).

2. **Install uv if missing.** It downloads and runs the Garmin connector.
   - macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

   Then find the full path to `uvx` (macOS: usually `~/.local/bin/uvx`;
   Windows: usually `%USERPROFILE%\.local\bin\uvx.exe`).

3. **Garmin login (the athlete does this part).** Check whether
   `~/.garminconnect` exists (don't open it). If it doesn't, tell them:
   - Open a terminal (macOS: Cmd+Space, type Terminal; Windows: Start
     menu, type PowerShell). If the app offers a terminal panel, that
     works too.
   - Paste the command below, using the full uvx path if `uvx` alone
     isn't found:
     `uvx --python 3.12 --from git+https://github.com/Taxuspt/garmin_mcp@a2ca5fcac34524b83814fe2fcf3d479f8a75983f garmin-mcp-auth`
   - Type their Garmin email, password, and the verification code if
     Garmin sends one. Password characters won't show; that's normal.
   - Tell you when it says the tokens were saved.

   Never ask for the password in chat. If the login fails, follow the
   retry rule in CLAUDE.md.

4. **Connect the server.** The `garmin` server is already defined in
   `.mcp.json`. Tell the athlete to restart Claude Code (or start a new
   session in this folder) and approve the `garmin` server when asked.
   If it fails to start because `uvx` isn't found, add a local override
   with the full path:
   `claude mcp add garmin --scope local -e GARMIN_ENABLED_TOOLS=<same list as .mcp.json> -- <full uvx path> --python 3.12 --from <same git URL as .mcp.json> garmin-mcp`
   then restart again.

5. **Test it.** Call `get_devices` and `get_activities` (limit 3), and
   `get_sleep_summary` for today. Show the watch model, the last 3
   activities, and last night's sleep in a short friendly summary.

6. **Build the profile.** Copy `athlete/profile.example.md` to
   `athlete/profile.md`. Fill in what you can from Garmin (recent weekly
   mileage, typical easy pace and HR, race predictions, devices). Then
   ask the athlete the remaining questions a few at a time, not all at
   once: goal race and date, goal time, injuries, which days they can
   run, long run day, and whether they know their max HR. If there's a
   plan in `plan/`, read it and fill in from it too.

7. **Optional: free-plan fallback.** Ask if they also want Garmin in
   regular Claude Desktop chats, which works on the free plan if they
   ever stop paying for Claude Code. If yes, add a `garmin` entry to
   Claude Desktop's config (`~/Library/Application Support/Claude/claude_desktop_config.json`
   on macOS, `%APPDATA%\Claude\claude_desktop_config.json` on Windows)
   with the same args and env as `.mcp.json` and the full uvx path. Keep
   any servers already in the file. Tell them to fully quit and reopen
   Claude Desktop.

8. **Wrap up.** Start `athlete/log.md` with a dated "Setup done" entry.
   Tell them the three commands: `/checkin` for a recovery and training
   check, `/week` to build next week's workouts, and that they can just
   ask questions in plain words. Remind them the Garmin login lasts about
   six months.
