#!/usr/bin/env python3
"""PostToolUse reverse-sync hook for literate-org (PROTOTYPE).

What this is for
----------------

literate-org's contract: ``.org`` files are the source of truth, and Python
modules are *artefacts* tangled out to ``./lpy/`` for downstream consumers
that don't read org. Trouble: AI agents (Claude Code, Cursor, OpenCode)
edit Python files when fixing bugs, because that's where the stack trace
points and where line numbers come from. That edit silently bypasses the
org source — next ``literate-elisp-load`` (or next tangle) overwrites the
agent's fix. The agent re-makes the same fix the next session. The
literate document drifts from the running code.

The 2026 fix ("AGENTS.md vs CLAUDE.md" research lens #5 + litprog-skill
PostToolUse reverse-sync hook):

    - Claude Code / Cursor fire a PostToolUse hook after every Edit/Write
      tool call.
    - This hook detects edits to ``./lpy/*.py`` (or any tangled output
      path).
    - It ``git diff``s the change vs the file's previous state, finds the
      enclosing src-block in the originating ``.org`` file (matching by
      function name / line markers / chunk name), patches THE ORG with the
      same diff, and tangles forward to validate idempotence.
    - If it can't reconcile, it FAILS the hook with a clear message —
      forcing the agent to switch and edit the .org instead.

Status
------

PROTOTYPE. This file is a working **stub** with the structure in place
and clearly-marked TODOs for the matching/patching/tangle logic. It logs
the right thing on every tool call, but does not yet rewrite org files.

Plug it into Claude Code via ``~/.claude/settings.json``:

    {
      "hooks": {
        "PostToolUse": [
          {
            "matcher": "Edit|Write",
            "hooks": [
              {"type": "command",
               "command": "python /Users/jingtao/projects/literate-org/hooks/post-tool-use-resync.py"}
            ]
          }
        ]
      }
    }

Then test by editing a Python file under ``./lpy/`` — the hook should
log a warning to stderr.

Source
------

Lens #5 (Documentation as agent context) cross-references the
strict-LP research's litprog-skill PostToolUse pattern. See
``~/projects/dummy/notes/ai-codebase-mastery.org`` and
``tasks/ai-codebase-mastery-action-plan.org`` (Quarter-1, item #6).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Configuration
TANGLED_OUTPUT_DIRS = ["lpy"]  # paths relative to repo root with generated .py
ORG_SOURCES = ["literate-org.org", "marimo.org"]  # primary literate sources


def main() -> int:
    """Read the Claude Code hook payload from stdin, decide whether to
    intervene, log a warning if a tangled artefact was edited.

    PROTOTYPE: returns 0 (allow) on every input. Real version would
    return non-zero to block bad edits.
    """
    # Claude Code passes the tool-call payload as JSON on stdin.
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # If we can't parse, don't block — best-effort hook.
        return 0

    # Extract the file path the tool just edited.
    tool_name = payload.get("tool_name") or payload.get("toolName") or ""
    if tool_name not in ("Edit", "Write", "MultiEdit"):
        return 0

    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    file_path = tool_input.get("file_path") or tool_input.get("path")
    if not file_path:
        return 0

    abs_path = Path(file_path).resolve()
    repo_root = Path(__file__).resolve().parent.parent

    # Only intervene if the edit lands inside one of the tangled output dirs.
    if not _is_tangled_artefact(abs_path, repo_root):
        return 0

    # TODO: locate originating .org src-block by walking ORG_SOURCES, match
    # on function name + nearest line marker.
    # TODO: re-apply the diff to the matching org src-block.
    # TODO: re-run literate-elisp-load (or tangle) on the org and verify
    # the resulting .py matches what the agent wrote (idempotence check).
    # TODO: if matching fails, return non-zero with a JSON envelope:
    #     {"decision": "block", "reason": "edit ./lpy/foo.py without
    #     corresponding .org change — please edit the .org instead"}.

    print(
        f"[literate-org reverse-sync] PROTOTYPE warning: edit landed at "
        f"{abs_path.relative_to(repo_root)} which is a tangled artefact. "
        f"In a real run this hook would patch the originating .org src-block "
        f"and re-tangle. For now, please mirror the change manually in "
        f"the .org source.",
        file=sys.stderr,
    )
    return 0


def _is_tangled_artefact(abs_path: Path, repo_root: Path) -> bool:
    """Return True if ABS_PATH is inside a directory we manage as
    tangle-output (i.e., agent should not edit directly).
    """
    try:
        rel = abs_path.relative_to(repo_root)
    except ValueError:
        return False
    parts = rel.parts
    return any(part in TANGLED_OUTPUT_DIRS for part in parts)


if __name__ == "__main__":
    sys.exit(main())
