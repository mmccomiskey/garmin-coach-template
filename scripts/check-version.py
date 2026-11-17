# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check and enforce version bumps when template files change.

Ensures version.json is updated whenever coach/, scripts/, or AGENTS.md
are modified, so athletes using /update detect new releases.

Usage:
  uv run scripts/check-version.py                # Verify version bump
  uv run scripts/check-version.py --bump [patch|minor|major]
  uv run scripts/check-version.py --install-hook  # Set up git pre-commit hook
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "version.json"

TEMPLATE_PATTERNS = [
    r"^coach/",
    r"^scripts/",
    r"^AGENTS\.md$",
    r"^SETUP\.md$",
    r"^README\.md$",
    r"^CLINE_SETUP\.md$",
]


def load_version() -> str:
    if not VERSION_FILE.exists():
        sys.exit("ERROR: version.json not found.")
    data = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    return data.get("version", "1.0.0")


def save_version(v: str) -> None:
    VERSION_FILE.write_text(json.dumps({"version": v}, indent=2) + "\n", encoding="utf-8")


def bump_version(kind: str = "minor") -> str:
    cur = load_version()
    parts = [int(p) for p in cur.split(".")]
    while len(parts) < 3:
        parts.append(0)
    
    if kind == "major":
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif kind == "minor":
        parts[1] += 1
        parts[2] = 0
    else:  # patch
        parts[2] += 1
        
    new_v = ".".join(str(p) for p in parts)
    save_version(new_v)
    print(f"Bumped version: {cur} -> {new_v}")
    return new_v


def install_hook() -> None:
    hook_dir = ROOT / ".git" / "hooks"
    if not hook_dir.exists():
        sys.exit("ERROR: .git/hooks directory not found.")
    hook_path = hook_dir / "pre-commit"
    hook_content = """#!/bin/sh
# Enforce version bump on template changes
uv run scripts/check-version.py
"""
    hook_path.write_text(hook_content, encoding="utf-8")
    hook_path.chmod(0o755)
    print(f"Installed pre-commit hook at {hook_path}")


def get_staged_or_changed_files() -> list[str]:
    # Check staged files first
    res = subprocess.run(["git", "diff", "--cached", "--name-only"],
                         capture_output=True, text=True, cwd=ROOT)
    files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
    if not files:
        # Check working tree changes vs HEAD
        res = subprocess.run(["git", "diff", "HEAD", "--name-only"],
                             capture_output=True, text=True, cwd=ROOT)
        files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
    return files


def check_version() -> int:
    changed_files = get_staged_or_changed_files()
    if not changed_files:
        print("No changes detected.")
        return 0

    template_changed = False
    version_changed = "version.json" in changed_files

    for f in changed_files:
        for pat in TEMPLATE_PATTERNS:
            if re.search(pat, f):
                template_changed = True
                break

    if template_changed and not version_changed:
        # Check if HEAD already has a version change vs remote
        res = subprocess.run(["git", "diff", "origin/main", "--name-only"],
                             capture_output=True, text=True, cwd=ROOT)
        if "version.json" not in res.stdout:
            print("\n❌ VERSION CHECK FAILED:")
            print("Template files were modified, but version.json was not updated.")
            print("Run:  uv run scripts/check-version.py --bump [minor|patch]")
            return 1

    cur = load_version()
    print(f"✅ Version check passed: v{cur}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--bump", choices=["patch", "minor", "major"], nargs="?", const="minor",
                        help="Bump version in version.json (default: minor)")
    parser.add_argument("--install-hook", action="store_true",
                        help="Install git pre-commit hook to catch missing version bumps")
    args = parser.parse_args()

    if args.install_hook:
        install_hook()
        return 0

    if args.bump:
        bump_version(args.bump)
        return 0

    return check_version()


if __name__ == "__main__":
    sys.exit(main())
