---
description: How am I doing? Recovery, recent runs, and what to do today
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

Ask how they feel if they haven't said. Add a dated entry to
`athlete/log.md`. $ARGUMENTS
