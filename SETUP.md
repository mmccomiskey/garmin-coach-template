# Setup

Instructions for the AI assistant. The athlete pasted a message asking
you to set this folder up; this file is the whole procedure, and it
works in any supported assistant.

Read `AGENTS.md` first and follow its hard rules throughout. Then walk
the athlete through the steps below one at a time. Before each step,
say in one or two plain sentences what it does. Skip any step that's
already done, and say so. If setup was interrupted (for example by a
restart in step 5), pick up where it left off.

## 1. Check the computer

Detect macOS or Windows. Check whether `uv` and `uvx` are installed
(`uvx --version`).

Nothing in this setup needs Homebrew, git, Xcode, Python, or an admin
password. Don't run `git`, `brew`, `xcode-select`, `python`, or
`python3`: on a Mac without developer tools, `git` and `python3` pop up
a large Apple download that isn't needed here. To edit a file, use your
file-editing tools; if you need Python, use `uv run`.

## 2. Install uv if missing

Before running anything, explain it in plain words and wait for the
athlete's OK. Cover:

- What it is: uv is a free, widely used tool from Astral that downloads
  and runs Python programs. Here it runs the Garmin connector, the login
  page, and the script that sets up this assistant.
- Why it's safe: it installs only into their own user folder
  (`~/.local/bin`), needs no admin password, and doesn't change the
  system or other apps. It brings its own copy of Python.
- How to undo it: delete `~/.local/bin/uv` and `~/.local/bin/uvx`
  (Windows: the same files under `%USERPROFILE%\.local\bin`).
- That the install command comes from uv's official site, astral.sh.

Then run:

- macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

Find the full path to `uv` (macOS: usually `~/.local/bin/uv`; Windows:
usually `%USERPROFILE%\.local\bin\uv.exe`). Use the absolute path in
every later command; a new install often isn't on the PATH yet.

## 3. Garmin login (the athlete types, in their browser)

First tell the athlete what's about to happen: a Garmin login page will
open in their web browser; they sign in there with their Garmin email
and password, plus a verification code if Garmin sends one; and the
page will say when they're connected. Their password goes from that
page straight to Garmin, so remind them never to paste it into the
chat.

**Preferred: the browser login.** From this folder, run
`<full uv path> run scripts/garmin-login.py`. If a saved login already
works, it says so and exits. Otherwise it opens the page and keeps
running until the athlete finishes, for up to 15 minutes. If your app
can run a command in the background and tell you when it ends, do that;
otherwise run it normally and wait. It prints one status line at a
time:

- `ALREADY_CONNECTED` or `SUCCESS`: done, go to step 4.
- `OPEN_THIS: <link>`: the browser didn't open; give them the link.
- `WAITING: Garmin sent a verification code`: tell them to check their
  email or phone and type the code on the page.
- `RETRY`: Garmin rejected the password once; the page lets them try
  one more time.
- `FAILED` or `RATE_LIMITED`: follow the retry rule in AGENTS.md.
- `TIMED_OUT` or `STOPPED`: ask whether they want to try again.

Never put anything into the script's input, arguments, or env, and
don't open the page yourself. The athlete uses it, not you.

**Fallback: the terminal login.** Use it only if the script won't start.
Build the command from `coach/mcp.json`, so the version matches: the
absolute `uvx` path (next to `uv`), then the `args` from that file with
`garmin-mcp` replaced by `garmin-mcp-auth`. Tell them a terminal will
open and ask for their email, password and code, that password
characters won't show, and to come back and say "done". Then open the
terminal for them, using the first option that works:

1. **The app's own terminal**, if you have a tool that opens a terminal
   tab the athlete can see and type in.
2. **A new terminal window.**
   - macOS: `osascript -e 'tell application "Terminal" to activate' -e 'tell application "Terminal" to do script "<login command>"'`.
     The first time, macOS asks to let the app control Terminal; tell
     the athlete to click OK.
   - Windows: `Start-Process powershell -ArgumentList '-NoExit','-Command','& <login command>'`
3. **An editor's terminal panel**: in VS Code-based assistants, a
   normal command runs where the athlete can click and type.
4. **If none of those work**, tell them how to open a terminal
   themselves (macOS: Cmd+Space, type Terminal; Windows: Start menu,
   type PowerShell) and give them the command to paste.

Never type into the terminal yourself or pass credentials any other
way. When they say done, run the same command with `--verify` added. If
it fails, follow the retry rule in AGENTS.md.

## 4. Set up this assistant

Different assistants keep their slash commands, Garmin connection and
permissions in different places. A script writes them, so you don't
edit those files by hand.

1. Work out which app you're running in (for example Claude Code, Cline,
   Codex, Cursor, or VS Code with Copilot) and, if you know it, which
   model. See what's supported:
   `<full uv path> run scripts/install-harness.py --list`
2. Tell the athlete what you think it is and ask them to confirm, in
   plain words: "It looks like you're using Cline with Claude Sonnet. Is
   that right?"
3. Explain that the script adds the coach's commands and the Garmin
   connection to this assistant's settings, keeps anything already
   there, and saves a backup of any settings file it changes. Then run:
   `<full uv path> run scripts/install-harness.py <name>`
4. It prints what it wrote, then `NEXT:` lines. Follow those exactly
   and explain them to the athlete.

If the app isn't on the list, say so plainly. `AGENTS.md` may still
work in it, but the Garmin connection and commands won't be set up
automatically. Suggest one of the supported apps instead of improvising
config files.

If the athlete's model is a small or "fast" one, mention that building
workouts (`/week`) works best with a stronger model, and they can
switch for that.

## 5. Load the Garmin connection

Most apps only load new MCP servers after a reload or a new session,
which the `NEXT:` lines from step 4 explain. If you have to restart,
tell the athlete to come back and type `/setup` (or "continue setup")
in the new session, and that you'll pick up at step 6.

## 6. Test it

Use only the Garmin MCP tools themselves: call `get_devices` and
`get_activities` (limit 3), and `get_sleep_summary` for today. Show the
watch model, the last 3 activities, and last night's sleep in a short
friendly summary.

Never test the server by running `garmin-mcp` in a terminal or writing
a script to talk to it. It's a stdio server meant to be run by the app;
run by hand it just waits for input, and that hangs or times out the
session.

If the Garmin tools aren't available yet, the app probably hasn't
loaded them. Follow the reload step from step 4 again, or check the
server's status in the app's MCP list. If it shows an error, read it
and re-run the script from step 4 rather than editing the config by
hand.

## 7. Build the profile

Copy `athlete/profile.example.md` to `athlete/profile.md`. Fill in what
you can from Garmin (recent weekly mileage, typical easy pace and HR,
race predictions, devices). Then ask the athlete the remaining
questions a few at a time, not all at once: goal race and date, goal
time, which days they can run, long run day, and whether they know
their max HR. If there's a plan in `plan/`, read it and fill in from it
too.

Then ask about injuries as their own short conversation, not one item
in a list:

- Anything hurting or bothering them right now, even a little?
- Past running injuries, especially ones that have come back (shin
  splints, tendon or IT band trouble, stress fractures, plantar
  fasciitis), and any surgeries.
- Are they seeing, or have they seen, a PT or doctor for it? What did
  they say to do or avoid?
- What tends to set it off: hills, speed work, long runs, certain shoes
  or surfaces, back-to-back days?
- Any early warning signs they've learned to notice.

Write the answers in the profile's "Injuries and things to watch"
section, including any limits a PT or doctor gave. If they have none,
write "None reported" with the date.

## 8. Optional: Garmin in Claude Desktop chats

Ask if they also want Garmin in regular Claude Desktop chats, which
works on the free Claude plan. If yes, run
`<full uv path> run scripts/install-harness.py claude-desktop` and
follow its `NEXT:` lines.

## 9. Wrap up

Start `athlete/log.md` with a dated "Setup done" entry. Tell them the
commands: `/checkin` for a recovery and training check, `/week` to
build next week's workouts, and that they can just ask questions in
plain words. Remind them the Garmin login lasts about six months.
