#!/usr/bin/env python3
# PreToolUse hook: warn (default) when an Edit/Write/MultiEdit on a .org
# file would NEWLY introduce an oversized atomic `:tangle` src block — a
# whole source file pasted as ONE `#+begin_src` block over the resplit
# threshold, instead of the per-def section shape literate-org-import
# emits (one section per top-level def/class).
#
# WHY a hook, not just a rule: the graph.py incident happened *with*
# lp-noweb-for-big-blocks.md + lp-module-section-hierarchy.md already
# loaded — agents skip prose rules under generation pressure. Same
# reasoning that made block-bare-star-in-src.sh a hook.
#
# WHY diff-only + warn (not a hard block): the LP corpus legitimately
# carries hundreds of large atomic blocks (fast-path onboarding backlog,
# genuinely-one-big-class/def/terraform-resource). A blanket gate would
# flood. So this hook fires ONLY on a block the *current* edit newly
# introduces (before/after diff), and only nudges — the agent can finish,
# then restructure via literate-org-import / literate-org-resplit-buffer.
# Escalate to a hard block with LITERATE_AGENT_OVERSIZE_BLOCK_MODE=block.
#
# Reads the Claude Code tool payload from stdin (JSON), reconstructs the
# AFTER-edit buffer in memory (reusing the bare-star hook's edit replay),
# scans it for oversized atomic tangle blocks, subtracts any that already
# existed in the before-buffer, and emits a stderr nudge for the rest.
#
# The file is named .sh because that is how Claude Code's matcher is
# wired; the shebang forces python so the suffix is cosmetic. Self-
# contained (scanner inlined) for cold-clone usability — mirrors
# block-bare-star-in-src.sh.

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# --- knobs (boundary-object: sane default + consumer override via _env.sh) ---
# Strict ">" to match the Emacs literate-org-resplit-threshold defcustom
# (the splitter fires on `(> body 120)`).
THRESHOLD = int(os.environ.get("LITERATE_AGENT_RESPLIT_THRESHOLD", "120"))
# warn (default) | block | off
MODE = os.environ.get("LITERATE_AGENT_OVERSIZE_BLOCK_MODE", "warn").strip().lower()
_DEFAULT_CODE_EXTS = (
    ".py,.ts,.tsx,.rs,.tf,.el,.clj,.go,.rb,.js,.jsx,.java,.kt,"
    ".swift,.cpp,.c,.h,.hpp,.cs"
)
CODE_EXTS = tuple(
    s.strip().lower()
    for s in os.environ.get("LITERATE_AGENT_PROSE_BEFORE_SRC_EXTS", _DEFAULT_CODE_EXTS).split(",")
    if s.strip()
)

HEADING_RE = re.compile(r"^(\*+)\s+\S")
SRC_BEGIN_RE = re.compile(r"^\s*#\+begin_src\b", re.I)
SRC_END_RE = re.compile(r"^\s*#\+end_src\b", re.I)
DRAWER_BEGIN_RE = re.compile(r"^\s*:PROPERTIES:\s*$", re.I)
DRAWER_END_RE = re.compile(r"^\s*:END:\s*$", re.I)
TANGLE_RE = re.compile(r":tangle\s+(\S+)")
NOWEB_REF_RE = re.compile(r":noweb-ref\b", re.I)
# A standalone <<chunk>> line is a noweb skeleton placeholder. NOTE: ":noweb
# yes" is deliberately NOT a noweb signal — it is a file-level #+PROPERTY on
# every block (e.g. langsmith.org's header-args), so treating it as "skeleton"
# would exempt every block and defeat the hook. Only :noweb-ref (leaf/skeleton)
# and a <<chunk>> body line are real signals.
NOWEB_CHUNK_RE = re.compile(r"^\s*<<[^>\n]+>>\s*$")
PIN_RE = re.compile(r"^\s*:(?:LITERATE_ORG_PIN|LITERATE_ORG_NO_SPLIT):\s*yes\s*$", re.I)


def _is_code(tangle: str) -> bool:
    low = tangle.strip().strip('"').lower()
    return any(low.endswith(ext) for ext in CODE_EXTS)


def _oversized_blocks(text: str) -> list[dict]:
    """Return one dict per oversized atomic :tangle block:
    {tangle, line, body, inline}. A block qualifies when its effective
    tangle (inline on #+begin_src, else nearest-ancestor :header-args:,
    else file-level #+PROPERTY) is a code extension, its body exceeds
    THRESHOLD lines, it is not a noweb skeleton/leaf, and no enclosing
    section is pinned (:LITERATE_ORG_PIN: / :LITERATE_ORG_NO_SPLIT:)."""
    lines = text.splitlines()

    file_htangle: str | None = None
    for raw in lines:
        low = raw.lower()
        if low.startswith("#+property:") and "header-args" in low:
            m = TANGLE_RE.search(raw)
            if m:
                file_htangle = m.group(1)

    stack: list[dict] = []  # each: {depth, htangle, noweb, pinned}
    pending: dict | None = None
    in_drawer = False
    in_src = False
    blk: dict | None = None
    out: list[dict] = []

    def eff_htangle() -> str | None:
        for s in reversed(stack):
            if s["htangle"] is not None:
                return s["htangle"]
        return file_htangle

    def anc_noweb() -> bool:
        return any(s["noweb"] for s in stack)

    def any_pinned() -> bool:
        return any(s["pinned"] for s in stack)

    for n, raw in enumerate(lines, 1):
        if in_src:
            if SRC_END_RE.match(raw):
                in_src = False
                eff = blk["inline"] if blk["inline"] is not None else eff_htangle()
                noweb = blk["noweb_ref"] or blk["chunk"] or anc_noweb()
                if (
                    eff is not None
                    and eff.strip().strip('"').lower() != "no"
                    and _is_code(eff)
                    and blk["body"] > THRESHOLD
                    and not noweb
                    and not any_pinned()
                ):
                    out.append(
                        {"tangle": eff, "line": blk["begin_n"],
                         "body": blk["body"], "inline": blk["inline"] is not None}
                    )
                blk = None
                continue
            blk["body"] += 1
            if NOWEB_CHUNK_RE.match(raw):
                blk["chunk"] = True
            continue

        hm = HEADING_RE.match(raw)
        if hm:
            in_drawer = False
            depth = len(hm.group(1))
            while stack and stack[-1]["depth"] >= depth:
                stack.pop()
            sec = {"depth": depth, "htangle": None, "noweb": False, "pinned": False}
            stack.append(sec)
            pending = sec
            continue
        if DRAWER_BEGIN_RE.match(raw):
            in_drawer = True
            continue
        if in_drawer:
            if DRAWER_END_RE.match(raw):
                in_drawer = False
            elif pending is not None:
                if "header-args" in raw.lower():
                    m = TANGLE_RE.search(raw)
                    if m:
                        pending["htangle"] = m.group(1)
                    if NOWEB_REF_RE.search(raw):
                        pending["noweb"] = True
                if PIN_RE.match(raw):
                    pending["pinned"] = True
            continue
        if SRC_BEGIN_RE.match(raw):
            in_src = True
            inline = TANGLE_RE.search(raw)
            blk = {
                "begin_n": n,
                "inline": inline.group(1) if inline else None,
                "noweb_ref": bool(NOWEB_REF_RE.search(raw)),
                "body": 0,
                "chunk": False,
            }
            continue
        # other body line — ignored

    return out


def _apply_edit(current: str, old: str, new: str, replace_all: bool) -> str:
    if not old:
        return current
    return current.replace(old, new) if replace_all else current.replace(old, new, 1)


def _resolve_proposed_content(tool: str, inp: dict, target: Path) -> tuple[str, str]:
    before = target.read_text(encoding="utf-8") if target.is_file() else ""
    if tool == "Write":
        return before, inp.get("content", "") or ""
    if tool == "Edit":
        return before, _apply_edit(
            before, inp.get("old_string", "") or "", inp.get("new_string", "") or "",
            bool(inp.get("replace_all", False)),
        )
    if tool == "MultiEdit":
        cur = before
        for edit in inp.get("edits", []) or []:
            cur = _apply_edit(
                cur, edit.get("old_string", "") or "", edit.get("new_string", "") or "",
                bool(edit.get("replace_all", False)),
            )
        return before, cur
    return before, before


def main() -> int:
    if MODE == "off":
        return 0
    payload = json.loads(sys.stdin.read())
    tool = payload.get("tool_name", "")
    inp = payload.get("tool_input", {}) or {}
    path = inp.get("file_path", "") or ""

    if tool not in {"Edit", "Write", "MultiEdit"}:
        return 0
    if not path.endswith(".org"):
        return 0

    before_text, after_text = _resolve_proposed_content(tool, inp, Path(path))
    before_sigs = {b["tangle"] for b in _oversized_blocks(before_text)}
    new = [b for b in _oversized_blocks(after_text) if b["tangle"] not in before_sigs]
    if not new:
        return 0

    block = MODE == "block"
    verb = "Refusing to edit" if block else "Heads-up on"
    print(
        f"{verb} {path}: this change introduces {len(new)} oversized atomic "
        f":tangle block(s) (> {THRESHOLD} lines). A whole source file pasted as "
        f"ONE #+begin_src block should be imported via literate-org-import (which "
        f"auto-resplits into one section per top-level def/class).",
        file=sys.stderr,
    )
    print("", file=sys.stderr)
    for b in new:
        note = "  [also: :tangle is INLINE — move it into the section " \
               ":header-args: drawer first, else literate-org-resplit-block-at-point " \
               "errors 'No :tangle target']" if b["inline"] else ""
        print(f"  ~line {b['line']}: {b['body']} lines -> {b['tangle']}{note}", file=sys.stderr)
    print("", file=sys.stderr)
    print(
        "Fix: import via literate-org-import, or run literate-org-resplit-buffer "
        "/ literate-org-resplit-block-at-point on the section, then verify the "
        "tangle output is byte-equivalent. See rules/lp-noweb-for-big-blocks.md + "
        "rules/lp-module-section-hierarchy.md. Tune: LITERATE_AGENT_RESPLIT_THRESHOLD; "
        "silence one section with a :LITERATE_ORG_NO_SPLIT: yes drawer property; "
        "set LITERATE_AGENT_OVERSIZE_BLOCK_MODE=off to disable.",
        file=sys.stderr,
    )
    return 2 if block else 0


if __name__ == "__main__":
    sys.exit(main())
