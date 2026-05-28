"""Regenerate the LP README entry points across <meta-repo>.

Three artefacts in one script:

  1. Root ``README.org`` — the human-facing front door.
  2. ``lp/<group>/README.org`` for every group under ``lp/`` — per-
     submodule entry with Why / What / How files relate / Read order /
     full index.
  3. (Already lives in ``scripts/build_index.py``; this script does NOT
     touch ``lp/INDEX.org`` — invoke that script separately.)

Per-group narrative metadata is held in ``GROUP_NARRATIVE`` below. To
adjust an elevator pitch, file-role mapping, or read-order: edit the
metadata dict and re-run. The per-file alphabetical index at the bottom
of each README is auto-rebuilt from each .org file's ``#+TITLE``.

The root README's table of submodules is grouped into three buckets
declared in ``ROOT_BUCKETS`` so a senior engineer can scan by role.

Usage:
    uv run python scripts/build_readme.py            # rebuild all
    uv run python scripts/build_readme.py --check    # diff vs disk, exit 1 if drift

Companion: ``scripts/build_index.py`` for ``lp/INDEX.org``, and
``scripts/audit_lp.py`` for the file-level A-grade audit.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path
from textwrap import dedent

REPO_ROOT = Path(__file__).resolve().parent.parent
LP_ROOT = REPO_ROOT / "lp"

# ────────────────────────────────────────────────────────────────────
# Per-group narrative metadata — hand-curated.
#
# Each entry has:
#   elevator    — one-paragraph "what this submodule is" (10-20 lines).
#   groups      — [(label, role)] conceptual grouping for "How files
#                 relate"; empty list ⇒ single-file submodule.
#   read_order  — bulleted reading sequence for a senior engineer
#                 landing on the README.
#
# To add a new submodule: append a new key here. The renderer will
# pick it up. (lp/<new-group>/ also needs to exist on disk.)
# ────────────────────────────────────────────────────────────────────
# Per-group narrative metadata — loaded from TOML, never hardcoded.
#
# ``GROUP_NARRATIVE`` maps each submodule name to a dict with three
# keys consumed by ``render_group_readme``:
#
#   elevator    — one-paragraph "what this submodule is" (10-20 lines).
#   groups      — [[label, role], ...] for "How files relate"; empty
#                 list ⇒ single-file submodule.
#   read_order  — [step, ...] reading sequence for a senior engineer
#                 landing on the README.
#
# Resolution mirrors ``_load_buckets`` below — same TOML file, same
# discovery order. Schema:
#
#     [groups.<submodule-name>]
#     elevator = "..."
#     groups = [["label", "role"], ...]
#     read_order = ["step 1", "step 2"]
#
# If the TOML file is absent (or has no ``[groups.*]`` tables), the
# narrative dict is empty and the renderer emits a degraded shell —
# bucket tables stay empty and per-group READMEs are not regenerated.
# That is intentional: literate-agent ships ZERO project-specific
# prose. Every consumer repo curates its own.
# ────────────────────────────────────────────────────────────────────


def _load_narrative() -> dict[str, dict]:
    """Load per-group narrative from the same TOML as ``_load_buckets``."""
    import os

    candidates: list[Path] = []
    env = os.environ.get("LITERATE_AGENT_BUCKETS_TOML")
    if env:
        candidates.append(Path(env))
    lp_root = os.environ.get("LP_ROOT")
    if lp_root:
        candidates.append(Path(lp_root) / ".literate-agent" / "buckets.toml")
    candidates.append(Path.cwd() / ".literate-agent" / "buckets.toml")

    for p in candidates:
        if p.is_file():
            try:
                import tomllib
            except ImportError:  # pragma: no cover
                import tomli as tomllib  # type: ignore[no-redef]
            data = tomllib.loads(p.read_text(encoding="utf-8"))
            groups = data.get("groups", {})
            # Normalise: convert [[label, role]] arrays to tuples
            out: dict[str, dict] = {}
            for grp, info in groups.items():
                out[grp] = {
                    "elevator": info.get("elevator", ""),
                    "groups": [
                        tuple(g) if isinstance(g, (list, tuple)) else (g, "")
                        for g in info.get("groups", [])
                    ],
                    "read_order": list(info.get("read_order", [])),
                }
            return out
    return {}


GROUP_NARRATIVE: dict[str, dict] = _load_narrative()

# ────────────────────────────────────────────────────────────────────
# Root README — three buckets group the 14 submodules by role.
# ────────────────────────────────────────────────────────────────────

def _load_buckets() -> list[tuple[str, list[str]]]:
    """Load the (bucket-name, [submodule-names]) list that drives root README
    grouping.

    Resolution order (first one found wins):

      1. ``$LITERATE_AGENT_BUCKETS_TOML`` — explicit override env var pointing
         at a TOML file with ``[[buckets]]`` tables.
      2. ``$LP_ROOT/.literate-agent/buckets.toml`` — project-local config
         (per the LP_ROOT env var the rest of the build scripts already read).
      3. ``./.literate-agent/buckets.toml`` (cwd) — fallback if LP_ROOT unset.
      4. Empty list — the script then falls back to a flat alphabetical scan
         of ``lp/*/`` directories. No hardcoded project names.

    TOML schema:

        [[buckets]]
        name = "My applications"
        members = ["project-a", "project-b"]

        [[buckets]]
        name = "Shared platform"
        members = ["python-foundation"]

    This is intentionally project-neutral. literate-agent ships NO default
    bucket list — every consumer repo defines its own membership.
    """
    import os

    candidates: list[Path] = []
    env = os.environ.get("LITERATE_AGENT_BUCKETS_TOML")
    if env:
        candidates.append(Path(env))
    lp_root = os.environ.get("LP_ROOT")
    if lp_root:
        candidates.append(Path(lp_root) / ".literate-agent" / "buckets.toml")
    candidates.append(Path.cwd() / ".literate-agent" / "buckets.toml")

    for p in candidates:
        if p.is_file():
            try:
                import tomllib  # Python 3.11+
            except ImportError:  # pragma: no cover
                import tomli as tomllib  # type: ignore[no-redef]
            data = tomllib.loads(p.read_text(encoding="utf-8"))
            return [
                (b["name"], list(b.get("members", [])))
                for b in data.get("buckets", [])
            ]
    return []


ROOT_BUCKETS = _load_buckets()


# ────────────────────────────────────────────────────────────────────
# Renderers
# ────────────────────────────────────────────────────────────────────


def _read_title(f: Path) -> str:
    for line in f.read_text().splitlines()[:20]:
        m = re.match(r"^#\+TITLE:\s*(.+?)\s*$", line)
        if m:
            return m.group(1)
    return ""


def collect_lp_files(grp_dir: Path) -> list[tuple[str, str]]:
    """Return [(filename, #+TITLE)] for every .org in the group dir
    (recursing into a single ``tests/`` subdir for <scout-server>).
    Excludes README.org itself and underscore-prefixed scratch files."""
    out: list[tuple[str, str]] = []
    for f in sorted(grp_dir.iterdir()):
        if f.is_dir() and f.name == "tests":
            for sub in sorted(f.iterdir()):
                if (sub.name.startswith(("#", "_"))
                        or sub.suffix != ".org"
                        or sub.name.endswith("~")):
                    continue
                out.append((f"tests/{sub.name}", _read_title(sub)))
            continue
        if (f.name.startswith(("#",))
                or f.suffix != ".org"
                or f.name.endswith("~")
                or f.name == "README.org"):
            continue
        out.append((f.name, _read_title(f)))
    return out


def render_group_readme(grp: str, info: dict, lp_files: list[tuple[str, str]]) -> str:
    elevator = info["elevator"]
    groups = info["groups"]
    read_order = info["read_order"]

    if groups:
        how_block = "\n\n".join(f"- {label} — {role}" for label, role in groups)
    else:
        how_block = "(single file — see the index below.)"

    read_block = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(read_order))

    index_lines = []
    for fname, ftitle in lp_files:
        if ftitle:
            index_lines.append(f"- [[file:{fname}][{fname}]] — {ftitle}")
        else:
            index_lines.append(f"- [[file:{fname}][{fname}]]")
    index_block = "\n".join(index_lines) if index_lines else "(empty)"

    return f"""\
# -*- Mode: POLY-ORG; indent-tabs-mode: nil;  -*- ---
#+TITLE: {grp} — LP entry point
#+OPTIONS: tex:verbatim toc:nil \\n:nil @:t ::t |:t ^:nil -:t f:t *:t <:t
#+STARTUP: noindent

* Table of Contents                                            :noexport:TOC:

* Why this file exists

Entry-point document for ``lp/{grp}/``. A senior engineer landing here
should be able to: (1) understand what this submodule is, (2) know
which file owns which subsystem, (3) pick a sensible read order. For
deeper architectural prose see ``_project.org`` in this folder; for
the file-by-file index scroll to the bottom of this README.

* What this submodule is

{elevator}

* How files relate

{how_block}

* Read order for newcomers

{read_block}

* LP files (full index)

Auto-generated from each ``.org``'s ``#+TITLE``. Regenerate via
``scripts/build_readme.py``.

{index_block}
"""


def render_root_readme() -> str:
    """Render the root README.org with three-bucket submodule table."""
    bucket_blocks = []
    for bucket_name, members in ROOT_BUCKETS:
        rows = []
        for grp in members:
            if grp not in GROUP_NARRATIVE:
                continue
            # First sentence of elevator → root-table cell
            first = GROUP_NARRATIVE[grp]["elevator"].split(". ")[0].rstrip(".")
            # Strip the leading =grp= label if it duplicates the row name
            first = re.sub(rf"^=*{re.escape(grp)}=*\s+(?:is\s+)?", "", first)
            first = first[:1].upper() + first[1:] if first else ""
            rows.append(
                f"| [[file:lp/{grp}/README.org][={grp}=]] | {first} |"
            )
        bucket_blocks.append(
            f"** {bucket_name}\n\n"
            "| Submodule | Elevator |\n"
            "|-----------+----------|\n"
            + "\n".join(rows)
        )
    submodules_section = "\n\n".join(bucket_blocks)

    n = sum(len(m) for _, m in ROOT_BUCKETS)
    return f"""\
# -*- Mode: POLY-ORG; indent-tabs-mode: nil;  -*- ---
#+TITLE: literate-programming meta-repo
#+OPTIONS: tex:verbatim toc:nil \\n:nil @:t ::t |:t ^:nil -:t f:t *:t <:t
#+STARTUP: noindent

* Table of Contents                                            :noexport:TOC:

* Why this file exists

Front door of this literate-programming meta-repo. A senior
engineer landing here should be able to leave with three things
settled: (1) what this repo is, (2) which submodule owns the
problem they came for, and (3) where to read next.

This README is auto-generated by
=$LITERATE_AGENT_HOME/scripts/build_readme.py= from the bucket
+ narrative config at =.literate-agent/buckets.toml=. Hand-edits
will be overwritten on the next ``make build-readme``.

* What this is

A *literate-programming meta-repo*. Production source for each
submodule under =repos/= is authored prose-first as Org-mode under
=lp/<sub>/*.org=, then tangled back into the matching submodule's
source files. Read the .org for the *why*; the tangled file
exists for tooling that doesn't speak Org.

* How submodules relate

{n} submodules configured (see =.literate-agent/buckets.toml=):

{submodules_section if submodules_section else "_(no buckets configured yet — populate `.literate-agent/buckets.toml`.)_"}

* Read order for newcomers

1. *This file* — front-door overview.
2. =CLAUDE.md= — the agent-only layer at the root.
3. =lp/INDEX.org= — auto-generated catalogue.
4. =lp/<group>/README.org= — per-submodule entry.
5. =lp/<group>/<file>.org= — individual literate source; tangles
   to =repos/<group>/<…>=. Edit *here*, never the tangled file.

* Top-level Org files

- [[file:lp/INDEX.org][lp/INDEX.org]] — auto-generated cross-submodule index. Regenerate
  via ``make build-index``.
- [[file:lp/draft.org][lp/draft.org]] — open design proposals queue (if used).
- [[file:lp/decisions-log.org][lp/decisions-log.org]] — accepted / rejected design proposals +
  research notes (if used).

* Build + lint commands

These targets are provided by ``templates/Makefile.lp.mk`` from
=literate-agent=. Drop the snippet into your project's =Makefile=:

#+begin_src bash
include $(HOME)/projects/literate-agent/templates/Makefile.lp.mk
#+end_src

Then:

#+begin_src bash
make tangle FILE=lp/<sub>/<x>.org    # tangle one .org back to repos/<sub>/
make tangle-all                       # every non-underscore lp/**/*.org

make check-structure                  # depth ≤ 5, prose-before-src
make build-index                      # regenerate lp/INDEX.org
make build-readme                     # regenerate this file + lp/<group>/README.org
make build-tangle-map                 # refresh .cache/tangle-map.tsv
#+end_src
"""


# ────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────


def _write_or_check(path: Path, content: str, check_only: bool) -> bool:
    """Return True if content matches disk (or was written)."""
    if check_only:
        existing = path.read_text() if path.is_file() else ""
        if existing == content:
            return True
        print(f"DRIFT: {path.relative_to(REPO_ROOT)}")
        diff = difflib.unified_diff(
            existing.splitlines(), content.splitlines(),
            fromfile=f"a/{path.name}", tofile=f"b/{path.name}", lineterm="",
        )
        for line in list(diff)[:30]:
            print(f"    {line}")
        return False
    path.write_text(content)
    print(f"wrote: {path.relative_to(REPO_ROOT)}")
    return True


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Don't write; exit 1 if any README would change.",
    )
    args = parser.parse_args(argv[1:])

    ok = True

    # Per-group READMEs
    for grp, info in sorted(GROUP_NARRATIVE.items()):
        grp_dir = LP_ROOT / grp
        if not grp_dir.is_dir():
            print(f"SKIP (missing): {grp}")
            continue
        lp_files = collect_lp_files(grp_dir)
        content = render_group_readme(grp, info, lp_files)
        ok &= _write_or_check(grp_dir / "README.org", content, args.check)

    # Root README
    ok &= _write_or_check(REPO_ROOT / "README.org", render_root_readme(), args.check)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
