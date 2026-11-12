---
name: setup
description: One-time setup for the Garmin running coach. Installs uv, walks the athlete through the Garmin login in their browser, connects the Garmin MCP server in Claude Code or Cline, and creates the athlete profile. Use when the athlete types /setup or the Garmin server isn't connected yet.
---

Walk the athlete through setup one step at a time. Before each step, say
in one or two plain sentences what it does. Skip any step that's already
done, and say so.

1. **Check the computer.** Detect macOS or Windows. Check whether `uv` and
   `uvx` are installed (`uvx --version`).

   Nothing in this setup needs Homebrew, git, Xcode, Python, or an admin
   password. Don't run `git`, `brew`, `xcode-select`, `python`, or
   `python3`: on a Mac without developer tools, `git` and `python3` pop
   up a large Apple download that isn't needed here. To edit a config
   file, use your file-editing tools; if you need Python, use `uv run`.

2. **Install uv if missing.** Before running anything, explain it in
   plain words and wait for the athlete's OK. Cover:
   - What it is: uv is a free, widely used tool from Astral that
     downloads and runs Python programs. Here it runs the Garmin
     connector and the login page.
   - Why it's safe: it installs only into their own user folder
     (`~/.local/bin`), needs no admin password, and doesn't change the
     system or other apps. It brings its own copy of Python.
   - How to undo it: delete `~/.local/bin/uv` and `~/.local/bin/uvx`
     (Windows: the same files under `%USERPROFILE%\.local\bin`).
   - That the install command comes from uv's official site,
     astral.sh.

   Then run:
   - macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

   Then find the full path to `uvx` (macOS: usually `~/.local/bin/uvx`;
   Windows: usually `%USERPROFILE%\.local\bin\uvx.exe`). Write it down
   as an absolute path; later steps need it.

3. **Garmin login (the athlete types, in their browser).** Check
   whether `~/.garminconnect` exists (don't open it). If it does, skip to
   the verify command at the end of this step.

   First tell the athlete what's about to happen: a Garmin login page
   will open in their web browser; they sign in there with their Garmin
   email and password, plus a verification code if Garmin sends one; and
   the page will say when they're connected. Their password goes from
   that page straight to Garmin, so remind them never to paste it into
   the chat.

   **Preferred: the browser login.** From this folder, run
   `<full uv path> run scripts/garmin-login.py` (`uv` sits next to
   `uvx`). It opens the page itself and keeps running until the athlete
   finishes, for up to 15 minutes. In Claude Code, run it in the
   background and wait for it to exit; in Cline, run it normally. It
   prints one status line at a time:
   - `ALREADY_CONNECTED` or `SUCCESS`: done, go to the verify command.
   - `OPEN_THIS: <link>`: the browser didn't open; give them the link.
   - `WAITING: Garmin sent a verification code`: tell them to check
     their email or phone and type the code on the page.
   - `RETRY`: Garmin rejected the password once; the page lets them try
     one more time.
   - `FAILED` or `RATE_LIMITED`: follow the retry rule in AGENTS.md.
   - `TIMED_OUT` or `STOPPED`: ask whether they want to try again.

   Never put anything into the script's input, arguments, or env, and
   don't open the page yourself. The athlete uses it, not you.

   **Fallback: the terminal login.** Use it only if the script won't
   start (for example, `uv` can't download its one dependency). The
   command, with the absolute uvx path and the `--from` URL in `.mcp.json`
   so the version matches:
   `<full uvx path> --python 3.12 --from <URL from .mcp.json> garmin-mcp-auth`

   Tell them a terminal will open and ask for their email, password and
   code, that password characters won't show, and to come back and say
   "done". Then open the terminal for them, using the first option that
   works:

   a. **The app's own terminal.** If you have a tool that opens a
      terminal tab the athlete can see and type in (Claude Desktop's
      Code tab has one), start the command there.
   b. **A new terminal window.**
      - macOS: `osascript -e 'tell application "Terminal" to activate' -e 'tell application "Terminal" to do script "<login command>"'`.
        The first time, macOS asks to let the app control Terminal;
        tell the athlete to click OK.
      - Windows: `Start-Process powershell -ArgumentList '-NoExit','-Command','& "<full uvx path>" --python 3.12 --from <URL from .mcp.json> garmin-mcp-auth'`
   c. **Cline in VS Code:** run the command normally; it opens in VS
      Code's terminal panel, where the athlete can click and type.
   d. **If none of those work**, tell them how to open a terminal
      themselves (macOS: Cmd+Space, type Terminal; Windows: Start menu,
      type PowerShell) and give them the command to paste.

   Never type into the terminal yourself or pass credentials any other
   way.

   **Verify.** Either way, confirm it worked without asking them to read
   anything back:
   `<full uvx path> --python 3.12 --from <URL from .mcp.json> garmin-mcp-auth --verify`

   If the login or verify fails, follow the retry rule in AGENTS.md.

4. **Connect the server.** This step depends on the assistant.

   **Claude Code:** the `garmin` server is already defined in
   `.mcp.json`. Tell the athlete to start a new session in this folder
   and approve the `garmin` server when asked. If it fails to start
   because `uvx` isn't found, add a local override with the full path:
   `claude mcp add garmin --scope local -e GARMIN_ENABLED_TOOLS=<same list as .mcp.json> -- <full uvx path> --python 3.12 --from <same URL as .mcp.json> garmin-mcp`
   then start a new session again.

   **Cline:** add the server to Cline's MCP settings file,
   `cline_mcp_settings.json`. Look for it at
   `~/.cline/data/settings/cline_mcp_settings.json`, then under the
   editor's extension storage (on macOS,
   `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/`;
   on Windows, `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\`).
   If you can't find it, ask the athlete to click the MCP Servers icon
   in the Cline panel, then Configure, then "Configure MCP Servers",
   which opens the file, and tell you its path.

   Add a `garmin` entry inside `mcpServers`, keeping any servers already
   there:
   - `command`: the **absolute** uvx path (Cline may not find a bare
     `uvx`).
   - `args` and `env`: copied exactly from `.mcp.json`.
   - `disabled`: `false`.
   - `autoApprove`: the read-only tool names, the same `get_*` tools
     listed in `.claude/settings.json` without the `mcp__garmin__`
     prefix. Leave out `upload_workout`, `create_*`, `delete_workout`
     and `schedule_workout` so those still ask first.

   Cline reloads the file on save. Ask the athlete to check that
   `garmin` shows a green dot in the MCP Servers panel; if it shows an
   error, read it and fix the entry.

5. **Test it.** Use only the Garmin MCP tools themselves: call
   `get_devices` and `get_activities` (limit 3), and `get_sleep_summary`
   for today. Show the watch model, the last 3 activities, and last
   night's sleep in a short friendly summary.

   Never test the server by running `garmin-mcp` in a terminal or
   writing a script to talk to it. It's a stdio server meant to be run by
   the app; run by hand it just waits for input, and that hangs or times
   out the session.

   If the Garmin tools aren't available yet, that's normal right after
   connecting: the app may not load new MCP tools until the next message
   or a new session. Tell the athlete to send another message (in Cline)
   or start a new session in this folder (in Claude Code), then try the
   tools again. If they still don't appear, check the server's status in
   the app's MCP list and fix the config entry.

6. **Build the profile.** Copy `athlete/profile.example.md` to
   `athlete/profile.md`. Fill in what you can from Garmin (recent weekly
   mileage, typical easy pace and HR, race predictions, devices). Then
   ask the athlete the remaining questions a few at a time, not all at
   once: goal race and date, goal time, which days they can run, long
   run day, and whether they know their max HR. If there's a plan in
   `plan/`, read it and fill in from it too.

   Then ask about injuries as their own short conversation, not one
   item in a list:
   - Anything hurting or bothering them right now, even a little?
   - Past running injuries, especially ones that have come back
     (shin splints, tendon or IT band trouble, stress fractures,
     plantar fasciitis), and any surgeries.
   - Are they seeing, or have they seen, a PT or doctor for it? What
     did they say to do or avoid?
   - What tends to set it off: hills, speed work, long runs, certain
     shoes or surfaces, back-to-back days?
   - Any early warning signs they've learned to notice.

   Write the answers in the profile's "Injuries and things to watch"
   section, including any limits a PT or doctor gave. If they have none,
   write "None reported" with the date.

7. **Optional, Claude Code only: free-plan fallback.** Ask if they also
   want Garmin in regular Claude Desktop chats, which works on the free
   Claude plan. If yes, add a `garmin` entry to Claude Desktop's config
   (`~/Library/Application Support/Claude/claude_desktop_config.json`
   on macOS, `%APPDATA%\Claude\claude_desktop_config.json` on Windows)
   with the same args and env as `.mcp.json` and the full uvx path. Keep
   any servers already in the file. Tell them to fully quit and reopen
   Claude Desktop.

8. **Wrap up.** Start `athlete/log.md` with a dated "Setup done" entry.
   Tell them the commands: `/checkin` for a recovery and training check,
   `/week` to build next week's workouts, and that they can just ask
   questions in plain words. Remind them the Garmin login lasts about
   six months.
