#!/usr/bin/env python3
"""
Read project .claude/settings.local.json and global ~/.claude/settings.json,
then print permissions that are in the project but NOT in the global allow list.
Output: one permission per line (for easy parsing).
"""
import json
import re
import sys
from pathlib import Path

# Shell reserved words that are not valid command prefixes.
# These appear when the fallback splitter breaks apart for/while/if constructs.
_SHELL_RESERVED = {
    "do", "done", "then", "fi", "else", "elif", "in", "esac", "case",
    "for", "while", "until", "if", "select",
}


def _is_bogus_pattern(perm: str) -> bool:
    """Return True if the permission looks like a shell-syntax artifact."""
    m = re.match(r"^Bash\((.+)\)$", perm)
    if not m:
        return False
    inner = m.group(1)
    # Strip trailing :* or * glob
    cmd_part = inner.split(":")[0].strip()
    first_word = cmd_part.split()[0] if cmd_part.split() else ""
    return first_word in _SHELL_RESERVED


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
new_perms = [p for p in new_perms if not _is_bogus_pattern(p)]

if not new_perms:
    print("NONE")
else:
    for p in new_perms:
        print(p)
