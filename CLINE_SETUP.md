# Setting up with Cline Desktop

This guide sets up the running coach in **Cline Desktop**, a free app,
using your own AI key from Anthropic (Claude) or Google (Gemini). You pay
the AI company directly for what you use, usually a small amount.

Plan on 20 to 30 minutes.

## What you need

- A Mac or Windows computer (a personal one; work laptops often block
  this). Cline Desktop on Windows is still in beta.
- A Garmin watch and Garmin Connect account
- A credit card for the AI key

## 1. Install Cline Desktop

Download it from [cline.bot/desktop](https://cline.bot/desktop), install
it, and open it.

## 2. Get an AI key

An API key is like a password that lets Cline use an AI model and bills
your account. Pick **one** of these.

### Option A: Claude (Anthropic), recommended

Claude is very good at this kind of coaching and at building workouts
correctly.

1. Go to [platform.claude.com](https://platform.claude.com) and create an
   account. This is separate from a claude.ai chat subscription; a Pro
   plan does not include API use.
2. Open **Billing** and buy a small amount of credit, like $5 or $10.
   The key won't work until there's credit on the account. Leave
   auto-reload off so you can't get a surprise bill.
3. Open **API Keys**, click **Create Key**, and name it "Cline running
   coach".
4. Copy the key right away (it starts with `sk-ant-`). It's only shown
   once. Paste it somewhere safe, like your password manager.

Anthropic doesn't use API data to train its models by default.

### Option B: Gemini (Google AI Studio)

1. Go to [aistudio.google.com](https://aistudio.google.com) and sign in
   with your Google account.
2. Click **Get API key**, then **Create API key**. Copy it and save it
   somewhere safe.
3. **Turn on billing before you use it for the coach.** On Google's free
   tier, what you send is used to improve Google's products and can be
   read by human reviewers, and Google's terms say not to send personal
   information. Your sleep, heart rate and runs are personal health
   data. Linking a billing account moves you to the paid tier, where
   Google doesn't use your data that way. In AI Studio, open the billing
   or usage page for your key's project and follow **Set up billing**.
4. In the Google Cloud billing page, set a **budget alert**, like $10 a
   month, so you get an email before costs add up.

## 3. Add the key to Cline

1. In Cline Desktop, open **Settings** and find the model provider
   section.
2. Choose **Anthropic** (for a Claude key) or **Google Gemini** (for an
   AI Studio key).
3. Paste your key.
4. Pick a model:
   - Anthropic: a current **Sonnet** model is the best balance of
     quality and cost.
   - Gemini: the newest **Flash** model for low cost, or **Pro** for
     better planning.

Smaller or "lite" models are cheaper but more likely to make mistakes
when building workouts.

## 4. Open a coach folder

1. Make a new, empty folder, like `Documents/Running Coach`.
2. In Cline Desktop, open that folder as your workspace.

## 5. Let Cline set everything up

Paste this into Cline:

```text
Download the project at
https://github.com/mmccomiskey/garmin-coach-template into this folder
(use git if it's installed, otherwise download the ZIP from GitHub and
unzip it here, so AGENTS.md ends up directly in this folder). Then read
AGENTS.md and .claude/skills/setup/SKILL.md and walk me through setup.
I'm not a developer, so explain each step in plain words before you do
it.
```

What happens next:

- **Cline asks before running each command.** Read what it says it's
  doing and approve. It installs a small tool called uv, which runs the
  Garmin connector.
- **You do the Garmin login yourself.** Cline opens a terminal window
  with the Garmin login already started. On a Mac, the first time, you'll
  be asked to let Cline control Terminal; click OK. Type your Garmin
  email, password and verification code in that window, then tell Cline
  "done". Never paste your password into the chat.
- **Cline adds the Garmin connection to its settings.** Check that
  **garmin** shows up as connected in Cline's installed MCP servers
  list.
- **Cline asks you a few questions** about your goals, race, injuries
  and schedule to build your profile.

## 6. Start coaching

Put your current training plan in the `plan` folder (see
[plan/README.md](plan/README.md) for how to get one out of ChatGPT),
then type:

- `/week` to plan next week and create the workouts on Garmin
- `/checkin` for a recovery check and what to do today

Or just ask questions in plain words.

## Keep your key safe

- Treat the API key like a password. Don't share it, post it, or paste
  it into the chat.
- If you think it leaked, delete it in the Anthropic Console or AI
  Studio and make a new one.
- Check your usage page now and then, especially the first week.

## If something goes wrong

| What you see | What to do |
|---|---|
| "Invalid API key" or "credit balance" errors | Anthropic: check you bought credit. Gemini: check the key was copied fully and billing is linked. |
| "Rate limit" or "quota" errors | Wait a minute and try again. On Gemini, this usually means you're still on the free tier. |
| Garmin isn't connected | Ask Cline: "The garmin MCP server isn't connected. Check its entry in the MCP settings and fix it." |
| The coach seems to ignore its rules | Tell it: "Read AGENTS.md first." |
| Garmin login fails | Wait an hour before trying again. Garmin blocks repeated attempts. |
| Workouts look wrong on the watch | Ask the coach to read the workout back and fix it, or switch to a stronger model. |
