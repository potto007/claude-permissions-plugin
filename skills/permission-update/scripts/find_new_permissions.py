#!/usr/bin/env python3
"""
Read project .claude/settings.local.json and global ~/.claude/settings.json,
then print permissions that are in the project but NOT in the global allow list.
Output: one permission per line (for easy parsing).
"""
import json
import sys
from pathlib import Path

project_settings = Path(".claude/settings.local.json")
global_settings = Path.home() / ".claude/settings.json"

if not project_settings.exists():
    print("ERROR: .claude/settings.local.json not found", file=sys.stderr)
    sys.exit(1)

if not global_settings.exists():
    print("ERROR: ~/.claude/settings.json not found", file=sys.stderr)
    sys.exit(1)

project_allow = set(json.loads(project_settings.read_text()).get("permissions", {}).get("allow", []))
global_allow = set(json.loads(global_settings.read_text()).get("permissions", {}).get("allow", []))

new_perms = sorted(project_allow - global_allow, key=str.lower)

if not new_perms:
    print("NONE")
else:
    for p in new_perms:
        print(p)
