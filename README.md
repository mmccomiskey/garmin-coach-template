# Garmin Running Coach

A folder that turns an AI assistant into a running coach connected to
your Garmin account. It can read your runs, sleep, HRV and training
status, and build workouts that sync to your watch. Works with
**Claude Code** or **Cline**.

Everything runs on your own computer. Your Garmin password is typed once
into Garmin's login tool and never shared with the AI or anyone else.

## Pick an assistant

| | Claude Code | Cline |
|---|---|---|
| What it is | The **Code** tab in the Claude Desktop app | A free, open-source extension for VS Code |
| Cost | Claude **Pro** plan or higher ($20/month). Not on the free plan. | The extension is free. You pay for the AI model: Cline offers some free models (limited and they change), a $9.99/month ClinePass, or you can use your own API key. |
| AI quality | Strong | Depends on the model you pick. Smaller free models can struggle with planning and building workouts. |
| Setup | Slightly easier | One extra step: Cline needs the Garmin connection added to its settings, which `/setup` does for you |

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
Download the project at
https://github.com/mmccomiskey/garmin-coach-template into this folder
(use git if it's installed, otherwise download the ZIP from GitHub and
unzip it here, so AGENTS.md ends up directly in this folder). Then read
AGENTS.md and .claude/skills/setup/SKILL.md and walk me through setup.
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
page, then **Download ZIP**, unzip it, open that folder in Claude Code or
VS Code, and type `/setup`.

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
  pinned to a tested version in `.mcp.json`.

## For maintainers

- `AGENTS.md` holds the coach's instructions. `CLAUDE.md` imports it so
  Claude Code and Cline share one file.
- Skills live in `.claude/skills/`, which both tools load as slash
  commands.
- `.mcp.json` is the source of truth for the server version and tool
  list. Claude Code reads it directly; Cline gets a copy in its own MCP
  settings during `/setup`, so after updating the pin, Cline users need
  to re-run `/setup` to pick it up.

This is a coaching helper, not medical advice. See a doctor or physical
therapist for pain that's sharp, getting worse, or not going away.
