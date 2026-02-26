# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Claude Code plugin with two components:
1. **`bash-compound-allow` hook** — PreToolUse hook that auto-approves compound Bash commands (joined with `&&`, `||`, `;`, `|`, or newlines) when every individual part matches existing allow rules.
2. **`/permission-update` skill** — Interactive skill to promote project-local allow rules and frequent hook log entries to global settings.

## Architecture

### Hook (`hooks/hooks.json` + `scripts/bash-compound-allow.py`)
- Registered as a `PreToolUse` hook on the `Bash` matcher
- Reads allow patterns from all four settings files: `~/.claude/settings.json`, `~/.claude/settings.local.json`, `.claude/settings.json`, `.claude/settings.local.json`
- Splits the command into parts, checks each against collected patterns
- Outputs `{"hookSpecificOutput": {"permissionDecision": "allow"}}` on full match, or `{"systemMessage": ...}` + exit 0 to let normal permission flow handle it
- Logs every decision to `/tmp/bash-compound-allow.log`

### Skill (`skills/permission-update/`)
- `SKILL.md` — skill definition and step-by-step instructions for Claude to follow
- `scripts/find_new_permissions.py` — compares `.claude/settings.local.json` vs `~/.claude/settings.json`, prints rules not yet in global
- `scripts/analyze_log.py` — parses `/tmp/bash-compound-allow.log` for PROMPT entries, groups by command prefix, returns JSON with frequency-ranked suggestions
- `scripts/add_permissions.py` — merges selected permissions into `~/.claude/settings.json` (sorted), removes promoted entries from `.claude/settings.local.json`

### Allow pattern format
Patterns are `Bash(...)` entries in settings files. Inside the parens:
- `*` — allow anything
- `git add:*` — command starts with `git add`, any args (colon separates command prefix from args glob)
- `jq` — plain glob against full command string

Shell builtins (`echo`, `cd`, `export`, etc.) and variable assignments are always trivially allowed regardless of rules.

## Installation (for this plugin itself)
```
/plugin marketplace add broven/claude-permissions-plugin
/plugin install claude-permissions-plugin@broven-claude-permissions-plugin
```

## Log
Hook decisions: `/tmp/bash-compound-allow.log`
```
[14:23:01] APPROVE | parts: ['npm install', 'echo "done"']
[14:23:05] PROMPT  | not in allow list: 'unknowncmd foo'
```
