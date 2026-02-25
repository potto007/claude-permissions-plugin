# claude-permissions-plugin

A Claude Code plugin for managing Bash permissions efficiently.

## Features

### 1. Hook: `bash-compound-allow`

Automatically approves compound Bash commands (joined with `&&`, `||`, `;`, `|`, or newlines) when **every individual part** matches your existing `allow` rules — no more per-prompt interruptions.

**Solves:** [anthropics/claude-code#16561](https://github.com/anthropics/claude-code/issues/16561)

- Reads allow rules from all settings files (`~/.claude/settings.json`, `~/.claude/settings.local.json`, `.claude/settings.json`, `.claude/settings.local.json`)
- Shell builtins (`echo`, `printf`, `cd`, etc.) and variable assignments are auto-allowed
- Logs every decision to `/tmp/bash-compound-allow.log`
- When a part is **not** allowed, shows a `systemMessage` identifying the exact command

### 2. Skill: `/permission-update`

Promotes project-level allow rules from `.claude/settings.local.json` to the global `~/.claude/settings.json`.

Useful when you've added project-specific rules and want to graduate them to global scope.

### 3. Skill: `/permission-analyze`

Analyzes the hook log to find commands that triggered permission prompts, ranked by frequency. Lets you interactively add safe ones to your global allow list.

Run periodically to keep your allow list up to date.

## Installation

```bash
/plugin install claude-permissions-plugin@broven
```

Or add to a marketplace and install from there.

## Log

All hook decisions are written to `/tmp/bash-compound-allow.log`:

```
[14:23:01] APPROVE | parts: ['npm install', 'echo "done"']
[14:23:05] PROMPT  | not in allow list: 'unknowncmd foo'
```

Use `/permission-analyze` to turn PROMPT entries into allow rules.
