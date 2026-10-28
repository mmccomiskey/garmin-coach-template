# Garmin Running Coach for Claude Code

A folder that turns Claude Code into a running coach connected to your
Garmin account. It can read your runs, sleep, HRV and training status,
and build workouts that sync to your watch.

Everything runs on your own computer. Your Garmin password is typed once
into Garmin's login tool and never shared with Claude or anyone else.

## What you need

- A Garmin watch and Garmin Connect account
- A Mac or Windows computer (a personal one; work laptops often block
  this)
- A personal Claude account on the **Pro** plan or higher. Claude Code
  isn't on the free plan.

## Get started

1. Install [Claude Desktop](https://claude.ai/download) and sign in with
   your personal account.
2. Make a new, empty folder, like `Documents/Running Coach`. In Claude
   Desktop, open the **Code** tab and choose that folder.
3. Paste this and follow along (about 15 minutes):

   ```text
   Download the project at
   https://github.com/mmccomiskey/garmin-coach-template into this folder
   (use git if it's installed, otherwise download the ZIP from GitHub and
   unzip it here, so CLAUDE.md ends up directly in this folder). Then read
   CLAUDE.md and .claude/commands/setup.md and walk me through setup. I'm
   not a developer, so explain each step in plain words before you do it.
   ```

   Partway through, Claude asks you to start a new session in the same
   folder so it can load the Garmin connection. Type `/setup` there and it
   picks up where it left off.
4. Put your current training plan in the `plan` folder and type `/week`.
   See [plan/README.md](plan/README.md) for how to get a plan out of
   ChatGPT.

Prefer to download it yourself? Click the green **Code** button on this
page, then **Download ZIP**, unzip it, open that folder in the Code tab,
and type `/setup`.

## Using it

- `/checkin`: how's recovery, how did recent runs go, what to do today
- `/week`: plan next week and create the workouts on Garmin
- Or just ask: "How did I sleep?", "Break down Saturday's long run",
  "Am I ready for a hard workout?"

Claude keeps notes about you in `athlete/profile.md` and a training log in
`athlete/log.md`, so it remembers your goals and history between chats.

## Good to know

- The Garmin login lasts about six months. When it expires, Claude will
  tell you and walk you through logging in again.
- If the Garmin login fails, wait an hour before retrying. Garmin blocks
  repeated attempts.
- Your notes and plan files are excluded from git, so they stay private
  even if you fork this repo.
- Built on the open-source [Taxuspt/garmin_mcp](https://github.com/Taxuspt/garmin_mcp),
  pinned to a tested version in `.mcp.json`.

This is a coaching helper, not medical advice. See a doctor or physical
therapist for pain that's sharp, getting worse, or not going away.
