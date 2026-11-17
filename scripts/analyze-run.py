# /// script
# requires-python = ">=3.10"
# dependencies = ["garminconnect==0.3.2"]
# ///
"""Analyze a running activity with code-side metric crunching.

Fetches run data and splits directly from Garmin Connect (using saved tokens
in ~/.garminconnect) or reads from a JSON file, crunches paces, cadence,
elevation, and cardiac drift (aerobic decoupling), and prints a compact,
token-efficient summary for coaching analysis.

Run:  uv run scripts/analyze-run.py [activity_id | latest] [--miles | --km]
Exit: 0 on success, 1 on error.
"""

import argparse
import io
import json
import math
import os
import re
import sys
from contextlib import redirect_stderr
from pathlib import Path

from garminconnect import Garmin

ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = ROOT / "athlete" / "profile.md"


def token_dir() -> str:
    env = os.getenv("GARMINTOKENS")
    if env and len(env) <= 512:
        return os.path.expanduser(env)
    return os.path.expanduser("~/.garminconnect")


def format_duration(seconds: float) -> str:
    s = int(round(seconds))
    hrs = s // 3600
    mins = (s % 3600) // 60
    secs = s % 60
    if hrs > 0:
        return f"{hrs}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


def speed_to_pace_str(speed_mps: float, use_miles: bool = True) -> str:
    if not speed_mps or speed_mps <= 0:
        return "--:--"
    sec_per_unit = (1609.344 / speed_mps) if use_miles else (1000.0 / speed_mps)
    if sec_per_unit > 3600:
        return ">60m"
    mins = int(sec_per_unit // 60)
    secs = int(round(sec_per_unit % 60))
    if secs == 60:
        mins += 1
        secs = 0
    unit = "/mi" if use_miles else "/km"
    return f"{mins}:{secs:02d}{unit}"


def read_profile_easy_hr() -> int | None:
    if not PROFILE_PATH.exists():
        return None
    try:
        text = PROFILE_PATH.read_text(encoding="utf-8")
        m = re.search(r"Easy range:\s*.*?(\d{2,3})\s*(?:bpm)?$", text, re.M | re.I)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None


def get_garmin_client() -> Garmin:
    path = token_dir()
    if not os.path.isfile(os.path.join(path, "garmin_tokens.json")):
        sys.exit("ERROR: Garmin tokens not found in ~/.garminconnect. Please run setup first.")
    try:
        with redirect_stderr(io.StringIO()):
            g = Garmin()
            g.login(path)
            return g
    except Exception as e:
        sys.exit(f"ERROR: Garmin authentication failed: {e}")


def extract_splits(splits_data: dict) -> list[dict]:
    if not isinstance(splits_data, dict):
        return []
    for key in ("lapDTOs", "splitSummaries", "activitySplitSummaries"):
        laps = splits_data.get(key)
        if laps and isinstance(laps, list):
            return laps
    return []
def analyze_activity(act: dict, splits_raw: dict | list | None, use_miles: bool = True) -> str:
    title = act.get("activityName") or act.get("name") or "Running Activity"
    date_str = act.get("startTimeLocal") or act.get("startDate") or "Unknown Date"
    dist_m = float(act.get("distance", 0.0))
    dist_units = dist_m / (1609.344 if use_miles else 1000.0)
    unit_label = "mi" if use_miles else "km"
    
    duration_s = float(act.get("duration") or act.get("movingDuration") or 0.0)
    avg_speed = float(act.get("averageSpeed", 0.0))
    avg_hr = act.get("averageHR") or act.get("averageHeartRate")
    max_hr = act.get("maxHR") or act.get("maxHeartRate")
    elev_gain = act.get("totalElevationGain", 0.0)
    elev_units = (elev_gain * 3.28084) if use_miles else elev_gain
    elev_label = "ft" if use_miles else "m"
    cadence = act.get("averageRunningCadenceInStepsPerMinute") or act.get("averageCadence")
    easy_hr_ceiling = read_profile_easy_hr()

    lines = []
    lines.append(f"### Run Summary: {title} ({date_str[:10]})")
    lines.append(f"- **Distance:** {dist_units:.2f} {unit_label} | **Time:** {format_duration(duration_s)} | **Avg Pace:** {speed_to_pace_str(avg_speed, use_miles)}")
    
    hr_info = []
    if avg_hr:
        hr_info.append(f"Avg HR: {int(avg_hr)} bpm")
    if max_hr:
        hr_info.append(f"Max HR: {int(max_hr)} bpm")
    if cadence:
        hr_info.append(f"Cadence: {int(cadence)} spm")
    if elev_gain:
        hr_info.append(f"Gain: +{int(round(elev_units))} {elev_label}")
    if hr_info:
        lines.append(f"- **Heart Rate & Work:** {' | '.join(hr_info)}")

    laps = extract_splits(splits_raw) if isinstance(splits_raw, dict) else (splits_raw or [])
    valid_splits = []
    for lap in laps:
        l_dist = float(lap.get("distance", 0.0))
        l_dur = float(lap.get("duration", 0.0))
        l_speed = float(lap.get("averageSpeed", 0.0))
        if l_speed == 0 and l_dur > 0:
            l_speed = l_dist / l_dur
        l_hr = lap.get("averageHR") or lap.get("averageHeartRate")
        if l_dist >= 160.0 and l_speed > 0:
            valid_splits.append({
                "dist_m": l_dist,
                "duration_s": l_dur,
                "speed": l_speed,
                "hr": float(l_hr) if l_hr else None,
                "cadence": lap.get("averageRunCadence") or lap.get("averageRunningCadenceInStepsPerMinute"),
                "elev_gain": lap.get("elevationGain", 0.0),
            })

    if len(valid_splits) >= 2 and all(s["hr"] for s in valid_splits):
        mid = len(valid_splits) // 2
        first_half = valid_splits[:mid]
        second_half = valid_splits[mid:]

        s1 = sum(s["speed"] for s in first_half) / len(first_half)
        hr1 = sum(s["hr"] for s in first_half) / len(first_half)
        s2 = sum(s["speed"] for s in second_half) / len(second_half)
        hr2 = sum(s["hr"] for s in second_half) / len(second_half)

        if s1 > 0 and s2 > 0 and hr1 > 0:
            eff1 = hr1 / s1
            eff2 = hr2 / s2
            drift_pct = ((eff2 - eff1) / eff1) * 100.0
            drift_sign = "+" if drift_pct >= 0 else ""
            
            if drift_pct < 3.5:
                verdict = "Low / Stable (aerobically solid)"
            elif drift_pct <= 7.0:
                verdict = "Moderate (expected for longer runs or warm weather)"
            else:
                verdict = "Significant (cardiovascular fatigue or started too fast)"
                
            p1_str = speed_to_pace_str(s1, use_miles)
            p2_str = speed_to_pace_str(s2, use_miles)
            lines.append(f"- **Cardiac Drift (Aerobic Decoupling):** {drift_sign}{drift_pct:.1f}% -> *{verdict}*")
            lines.append(f"  - 1st Half: {p1_str} @ {int(round(hr1))} bpm | 2nd Half: {p2_str} @ {int(round(hr2))} bpm")

    if valid_splits:
        lines.append("\n**Splits Breakdown:**")
        lines.append(f"| # | Pace | Avg HR | Cadence | Elev Gain | Notes |")
        lines.append(f"|---|------|--------|---------|-----------|-------|")
        for i, s in enumerate(valid_splits, 1):
            p_str = speed_to_pace_str(s["speed"], use_miles)
            hr_str = f"{int(round(s['hr']))} bpm" if s["hr"] else "--"
            cad_str = f"{int(round(s['cadence']))}" if s["cadence"] else "--"
            el_val = (s["elev_gain"] * 3.28084) if use_miles else s["elev_gain"]
            el_str = f"+{int(round(el_val))} {elev_label}" if el_val > 1 else "-"
            
            notes = []
            if easy_hr_ceiling and s["hr"] and s["hr"] > (easy_hr_ceiling + 2):
                diff = int(round(s["hr"] - easy_hr_ceiling))
                notes.append(f"⚠️ +{diff}bpm over easy ceiling ({easy_hr_ceiling})")
            
            lines.append(f"| {i} | {p_str} | {hr_str} | {cad_str} | {el_str} | {', '.join(notes) or 'OK'} |")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("activity", nargs="?", default="latest",
                        help="Activity ID or 'latest' (default: latest)")
    parser.add_argument("--file", help="Path to JSON file with activity and split data (offline mode)")
    parser.add_argument("--km", action="store_true", help="Output metric splits in kilometers instead of miles")
    args = parser.parse_args()

    use_miles = not args.km

    if args.file:
        try:
            data = json.loads(Path(args.file).read_text(encoding="utf-8"))
            act = data.get("activity", data)
            splits = data.get("splits")
            print(analyze_activity(act, splits, use_miles=use_miles))
            return 0
        except Exception as e:
            sys.exit(f"ERROR reading file {args.file}: {e}")

    g = get_garmin_client()
    try:
        if args.activity.lower() == "latest":
            activities = g.get_activities(0, 5)
            running_acts = [
                a for a in activities
                if (a.get("activityType", {}).get("typeKey") in ("running", "trail_running", "treadmill_running", "track_running")
                    or "run" in (a.get("activityType", {}).get("typeKey") or "").lower())
            ]
            if not running_acts and activities:
                running_acts = [activities[0]]
            if not running_acts:
                sys.exit("No recent running activities found on Garmin.")
            act = running_acts[0]
            act_id = act["activityId"]
        else:
            act_id = args.activity
            act = g.get_activity(act_id)

        splits = g.get_activity_splits(act_id)
        print(analyze_activity(act, splits, use_miles=use_miles))
        return 0
    except Exception as e:
        sys.exit(f"ERROR analyzing activity: {e}")


if __name__ == "__main__":
    sys.exit(main())

