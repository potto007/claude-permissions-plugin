---
name: permission-update
description: Sync new permissions from the current project's .claude/settings.local.json to the global ~/.claude/settings.json. Use only when explicitly invoked with /permission-update. Never auto-trigger.
disable-model-invocation: true
user-invocable: true
---

# permission-update

Promote project-level allowed permissions to the global settings using bundled scripts.

## Steps

1. **Find new permissions** — run the comparison script:
   ```bash
   python3 <skill_dir>/scripts/find_new_permissions.py
   ```
   - Output is one permission per line, or `NONE` if nothing new.
   - If `NONE`, inform the user and stop.

2. **Ask the user** — use `AskUserQuestion` with `multiSelect: true`.
   - Options = the permissions printed by the script.
   - Max 4 options per question; split into multiple questions if needed.
   - If the user selects nothing, inform them and stop.

3. **Write to global settings** — run the write script with the selected permissions as arguments:
   ```bash
   python3 <skill_dir>/scripts/add_permissions.py "perm1" "perm2" ...
   ```
   The script merges and sorts alphabetically (case-insensitive) automatically.

4. **Confirm** — report which permissions were added and removed from project settings.

## Notes

- `<skill_dir>` is the directory containing this SKILL.md (shown in the skill header at invocation time).
- Scripts never remove existing global permissions.
- Promoted permissions are automatically removed from the project `.claude/settings.local.json` to avoid redundancy.
