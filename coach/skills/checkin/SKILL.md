---
name: checkin
description: Running coach check-in. Reviews last night's sleep, the HRV trend, resting HR, and the past week's runs, then recommends what to do today. Use when the athlete types /checkin or asks how they're doing or whether to run today.
---

Give the athlete a short check-in.

1. Pull last night's sleep (`get_sleep_summary`), the HRV trend for the
   last 14 days, today's resting HR, and training readiness.
2. Pull runs from the last 7 days with `get_activities_by_date`. For any
   run since the last log entry, get splits.
3. Compare with `athlete/profile.md` and the plan in `plan/`.

Reply in this order, keeping it brief:
- **Recovery:** one line each for sleep, HRV trend, resting HR. Say
  whether things look normal for them, not just the numbers.
- **Recent runs:** one or two lines per run. Note easy runs that weren't
  easy, or anything that stands out.
- **Today:** a clear recommendation (run as planned, go easier, or rest)
  and why.

Ask how they feel if they haven't said. If the profile lists injuries
or problem spots, ask about each by name, and factor the answer into
today's recommendation (see "Working around injuries" in AGENTS.md).
Add a dated entry to `athlete/log.md`, including anything they said
about those spots.
