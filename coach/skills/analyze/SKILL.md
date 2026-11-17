---
name: analyze
description: Token-efficient, code-driven deep dive into a run. Analyzes cardiac drift (aerobic decoupling), pacing stability, splits, and heart rate vs easy ceilings using scripts/analyze-run.py. Use when the athlete types /analyze, asks how their run went, asks to break down a long run or workout splits, asks about their cardiac drift, or asks how they performed today or yesterday.
---

Perform a token-efficient, code-driven breakdown of a run.

1. Run `uv run scripts/analyze-run.py latest` (or pass a specific activity ID if the athlete specified one).
2. Read the compact summary produced by the script (distance, pace, cardiac drift / aerobic decoupling, split table).
3. Cross-reference with `athlete/profile.md` (easy HR ceiling, current training goals, and any active injury spots).
4. Provide a clear coaching breakdown:
   - **Aerobic & Cardiac Drift:** Explain what their cardiac drift percentage means in plain words (e.g., whether they paced aerobically well, or drifted due to fatigue, heat, or starting too fast).
   - **Pacing & Cadence:** Highlight their pacing discipline and cadence stability across splits and hills.
   - **Form / Effort Flags:** Note any splits where heart rate drifted above their easy range.
   - **Recovery Advice:** Based on the effort and how they felt, suggest what to focus on tomorrow (hydration, rest, easy shakeout).
