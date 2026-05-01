# literate-org hooks

Hooks for AI coding agents (Claude Code, Cursor, OpenCode) that interact
with literate-org-managed projects.

## post-tool-use-resync.py — PROTOTYPE

Detects when an agent edits a tangled Python artefact (`./lpy/*.py`) and
warns. Eventually it will patch the originating org src-block + retangle
to keep prose and code in sync.

Status: stub with structure + TODOs marking the matching/patching/tangle
logic. Plug it in via `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {"type": "command",
           "command": "python /Users/jingtao/projects/literate-org/hooks/post-tool-use-resync.py"}
        ]
      }
    ]
  }
}
```

## Why this matters

Strict literate programming (lens #5 of the AI codebase mastery research)
treats `.org` as source of truth and `.py` as a generated artefact. Agents
default to editing `.py` because that's where stack traces and line numbers
point. Without a hook, those edits silently drift from the org source —
next tangle overwrites them, agents re-make the same edit, and prose
stops describing reality.

The **2026 industry recipe** (apiad.net, byteiota, `tlehman/litprog-skill`
on GitHub) is to use a PostToolUse hook to either:

- (preferred) patch the org src-block from the diff and verify
  idempotence; OR
- (fallback) reject the edit with a message pointing at the org source.

This stub is the structural starting point.
