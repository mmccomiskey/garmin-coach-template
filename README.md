# Garmin Running Coach

A folder that turns an AI assistant into a running coach connected to
your Garmin account. It can read your runs, sleep, HRV and training
status, and build workouts that sync to your watch. Works best with
**Claude Code** or **Cline**, and also sets itself up for Codex, Cursor,
and VS Code with Copilot.

Everything runs on your own computer. Your Garmin password is typed once
into a login page in your browser that sends it straight to Garmin. The
AI never sees it, and neither does anyone else.

## Pick an assistant

| | Claude Code | Cline |
|---|---|---|
| What it is | The **Code** tab in the Claude Desktop app | A free, open-source extension for VS Code |
| Cost | Claude **Pro** plan or higher ($20/month). Not on the free plan. | The extension is free. You pay for the AI model: Cline offers some free models (limited and they change), a $9.99/month ClinePass, or you can use your own API key. |
| AI quality | Strong | Depends on the model you pick. Smaller free models can struggle with planning and building workouts. |
| Setup | About the same | About the same. Setup adds the Garmin connection to Cline's settings for you. |

Either way you need a Garmin watch, a Garmin Connect account, and a
personal Mac or Windows computer (work laptops often block this).

## Get started

### With Claude Code

1. Install [Claude Desktop](https://claude.ai/download) and sign in with
   your personal account.
2. Make a new, empty folder, like `Documents/Running Coach`. In Claude
   Desktop, open the **Code** tab and choose that folder.
3. Paste the setup message below and follow along.

### With Cline Desktop and your own AI key

See **[CLINE_SETUP.md](CLINE_SETUP.md)** for a full walkthrough: installing
Cline Desktop, getting a Claude or Gemini API key, and keeping your health
data private.

### With Cline in VS Code

1. Install [VS Code](https://code.visualstudio.com/), then install the
   **Cline** extension from the Extensions panel.
2. Open the Cline panel and sign in or add a model provider. Pick a
   capable model if you can.
3. Make a new, empty folder, like `Documents/Running Coach`, and open it
   in VS Code (**File > Open Folder**).
4. Paste the setup message below into Cline and follow along. Cline asks
   before running each command; approve them as it explains each one.

### The setup message

```text
Download this ZIP and unzip it into this folder, so AGENTS.md ends up
directly in this folder (don't use git):
https://github.com/mmccomiskey/garmin-coach-template/archive/refs/heads/main.zip
Then read AGENTS.md and SETUP.md and walk me through setup.
I'm not a developer, so explain each step in plain words before you do
it.
```

Setup takes about 15 minutes. In Claude Code, you'll be asked partway
through to start a new session in the same folder so it can load the
Garmin connection; type `/setup` there and it picks up where it left
off.

When it's done, put your current training plan in the `plan` folder and
type `/week`. See [plan/README.md](plan/README.md) for how to get a plan
out of ChatGPT.

Prefer to download it yourself? Click the green **Code** button on this
page, then **Download ZIP**, unzip it, open that folder in your
assistant, and tell it: "Read AGENTS.md and SETUP.md and walk me through
setup."

### Other assistants

Setup works out which assistant you're using and configures it, so the
same setup message works in:

- **OpenAI Codex** (app, VS Code extension, or CLI), included with paid
  ChatGPT plans. Commands start with `$`: `$checkin`, `$week`.
- **Cursor**.
- **VS Code with GitHub Copilot** in Agent mode. This one is
  experimental; Copilot's setup is changing in early 2027.

## Using it

- `/checkin`: how's recovery, how did recent runs go, what to do today
- `/week`: plan next week and create the workouts on Garmin
- Or just ask: "How did I sleep?", "Break down Saturday's long run",
  "Am I ready for a hard workout?"

The coach keeps notes about you in `athlete/profile.md` and a training
log in `athlete/log.md`, so it remembers your goals and history between
chats.

## Good to know

- The Garmin login lasts about six months. When it expires, the coach
  will tell you and walk you through logging in again.
- If the Garmin login fails, wait an hour before retrying. Garmin blocks
  repeated attempts.
- Your notes and plan files are excluded from git, so they stay private
  even if you fork this repo.
- Built on the open-source [Taxuspt/garmin_mcp](https://github.com/Taxuspt/garmin_mcp),
  pinned to a tested version in `coach/mcp.json`.

## For maintainers

- `AGENTS.md` holds the coach's instructions. Codex, Cursor, Cline and
  Copilot read it directly; Claude Code gets a generated `CLAUDE.md`
  that imports it.
- `SETUP.md` is the setup procedure. The `/setup` command just points
  to it, so setup also works before any commands exist.
- `coach/` is the source for everything assistant-specific:
  `coach/skills/` holds the commands and `coach/mcp.json` the Garmin
  server, its tool list, and which tools are read-only.
- `scripts/install-harness.py <name>` copies `coach/` into each
  assistant's own files (`.claude/`, `.cline/`, `.agents/`, `.cursor/`,
  `.github/skills/`, `.mcp.json`) and merges the server into user-level
  configs where an assistant has no project config (Cline, Codex,
  Copilot, Claude Desktop), backing those up first. The generated files
  are gitignored. Run `--list` for names, `--dry-run` to preview.
- The server is pinned by commit as a GitHub ZIP (`.../archive/<sha>.zip`),
  not `git+`, so a Mac without developer tools never needs git. To
  update, bump the sha in `coach/mcp.json`; users re-run the install
  script to pick it up.
- `scripts/garmin-login.py` is the browser login. It pins its own
  `garminconnect` version in the header; keep it matched to the one the
  pinned `garmin_mcp` uses, and copy any login-flow changes from
  `garmin_mcp/auth_cli.py`.

This is a coaching helper, not medical advice. See a doctor or physical
therapist for pain that's sharp, getting worse, or not going away.
