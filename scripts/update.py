# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Update the Garmin running coach template from GitHub.

Downloads the latest template files from GitHub and updates coach/, scripts/,
AGENTS.md, SETUP.md, and documentation, while strictly protecting and
preserving all athlete personal files in athlete/ (profile, logs, custom skills)
and plan/.

Run:  uv run scripts/update.py [--check] [--force] [--repo OWNER/REPO]
Exit: 0 on success, 1 on error.
"""

import argparse
import io
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO = os.getenv("GARMIN_COACH_REPO", "mmccomiskey/garmin-coach-template")
DEFAULT_BRANCH = os.getenv("GARMIN_COACH_BRANCH", "main")

TEMPLATE_PATHS = [
    "coach",
    "scripts",
    "AGENTS.md",
    "SETUP.md",
    "README.md",
    "CLINE_SETUP.md",
    "version.json",
    ".gitignore",
]

PROTECTED_PREFIXES = [
    "athlete",
    "plan",
    ".claude/settings.local.json",
    ".env",
]


def get_local_version() -> str:
    v_file = ROOT / "version.json"
    if v_file.exists():
        try:
            return json.loads(v_file.read_text(encoding="utf-8")).get("version", "1.0.0")
        except Exception:
            pass
    return "1.0.0"


def fetch_remote_version(repo: str, branch: str) -> str | None:
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/version.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Garmin-Coach-Updater"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("version")
    except Exception:
        return None


def download_zip(repo: str, branch: str) -> bytes:
    url = f"https://github.com/{repo}/archive/refs/heads/{branch}.zip"
    req = urllib.request.Request(url, headers={"User-Agent": "Garmin-Coach-Updater"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR downloading update from {url} (HTTP {e.code}): {e.reason}")
    except Exception as e:
        sys.exit(f"ERROR downloading update from {url}: {e}")


def is_protected(rel_path_str: str) -> bool:
    for p in PROTECTED_PREFIXES:
        if rel_path_str == p or rel_path_str.startswith(p + "/"):
            return True
    return False


def is_template_target(rel_path_str: str) -> bool:
    for t in TEMPLATE_PATHS:
        if rel_path_str == t or rel_path_str.startswith(t + "/"):
            return True
    return False



def apply_update(zip_bytes: bytes) -> tuple[int, list[str]]:
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    namelist = zf.namelist()
    if not namelist:
        sys.exit("ERROR: Downloaded archive is empty.")

    prefix = namelist[0].split("/")[0] + "/"
    updated_files = []

    for member in zf.infolist():
        if not member.filename.startswith(prefix) or member.is_dir():
            continue
        rel = member.filename[len(prefix):]
        if not rel or is_protected(rel) or not is_template_target(rel):
            continue

        target_path = ROOT / rel
        target_path.parent.mkdir(parents=True, exist_ok=True)
        content = zf.read(member)

        if target_path.exists() and target_path.read_bytes() == content:
            continue

        target_path.write_bytes(content)
        updated_files.append(rel)

    return len(updated_files), updated_files


def resync_harnesses() -> None:
    harness_script = ROOT / "scripts" / "install-harness.py"
    if not harness_script.exists():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("install_harness", harness_script)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            plan = mod.Plan(dry=False)
            destinations = [
                ROOT / ".claude" / "skills",
                ROOT / ".cline" / "skills",
                ROOT / ".agents" / "skills",
                ROOT / ".cursor" / "skills",
                ROOT / ".github" / "skills",
            ]
            for dest in destinations:
                if dest.parent.exists():
                    mod.copy_skills(plan, dest)
    except Exception as e:
        print(f"Note: Could not automatically re-sync skills ({e}). Run install-harness.py manually.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="check for updates without installing")
    parser.add_argument("--force", action="store_true", help="force reinstall even if already up to date")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"GitHub repo (default: {DEFAULT_REPO})")
    parser.add_argument("--branch", default=DEFAULT_BRANCH, help=f"branch (default: {DEFAULT_BRANCH})")
    args = parser.parse_args()

    local_ver = get_local_version()
    print(f"Current local version: {local_ver}")

    remote_ver = fetch_remote_version(args.repo, args.branch)
    if remote_ver:
        print(f"Latest remote version: {remote_ver}")
        if args.check:
            if remote_ver > local_ver:
                print("An update is available! Run 'uv run scripts/update.py' to update.")
            else:
                print("You are already on the latest version.")
            return 0
        if remote_ver <= local_ver and not args.force:
            print("Already up to date. (Use --force to reinstall anyway)")
            return 0
    else:
        print("Note: Could not check remote version directly, proceeding with update...")
        if args.check:
            return 0

    print(f"Downloading update from {args.repo} ({args.branch})...")
    zip_bytes = download_zip(args.repo, args.branch)
    count, changed = apply_update(zip_bytes)

    if count > 0:
        print(f"Updated {count} template file(s):")
        for f in changed[:10]:
            print(f"  - {f}")
        if len(changed) > 10:
            print(f"  ... and {len(changed) - 10} more.")
    else:
        print("All template files are already current.")

    resync_harnesses()
    print("\nUpdate complete! Your athlete profile, training logs, and custom skills were preserved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
