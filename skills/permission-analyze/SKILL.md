---
name: permission-analyze
description: Analyze the bash-compound-allow hook log to find commands that triggered permission prompts, and interactively add safe ones to the global allow list. Use when invoked with /permission-analyze. Never auto-trigger.
disable-model-invocation: true
user-invocable: true
---

# permission-analyze

Scan the hook log for blocked compound commands, rank by frequency, and promote safe ones to global allow rules.

## Steps

1. **Analyze the log** — run the analysis script:
   ```bash
   python3 <skill_dir>/scripts/analyze_log.py
   ```
   Output is JSON: `{"suggestions": [{"pattern": "Bash(sort:*)", "count": 9, "examples": ["sort -rn", ...]}, ...]}`
   - If output is `{"suggestions": []}`, tell the user nothing to add and stop.

2. **Ask the user** — use `AskUserQuestion` with `multiSelect: true`.
   - Show each suggestion as: `Bash(cmd:*)  ×N times` (e.g. `Bash(sort:*)  ×9 times`)
   - description = example commands seen
   - Max 4 options per question; split into multiple questions if needed.
   - If the user selects nothing, inform them and stop.

3. **Add to global settings** — for each selected suggestion, run:
   ```bash
   python3 <skill_dir>/scripts/add_permissions.py "Bash(cmd:*)" ...
   ```

4. **Confirm** — report which rules were added.

## Notes

- `<skill_dir>` is the directory containing this SKILL.md.
- The log file is at `/tmp/bash-compound-allow.log` (written by the bash-compound-allow hook).
- Only PROMPT entries (commands that triggered prompts) are analyzed — APPROVE entries are skipped.
- The script groups by first word (command name) and suggests `Bash(cmd:*)` patterns.
