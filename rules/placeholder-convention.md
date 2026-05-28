# Placeholder Convention for Project-Specific References

> *Last-validated*: 2026-05-28
> *Review cadence*: quarterly — drop if 6 months without a triggering incident
> *Origin*: 2026-05-27 OSS-publish scrub of literate-agent identified
> hardcoded "claude-agent" references in rules. Switching to shell-style
> placeholders makes the rules truly project-neutral and lets
> `scripts/build_readme.py` / `scripts/build_index.py` render consumer-
> specific output without find/replace.

literate-agent rules are read by AI agents and human authors working
across many consumer projects. Project-specific identifiers — function
names, repo URLs, file paths — appear as **shell-style placeholders**
that the build pipeline expands at render time using the consumer's
`.literate-agent/config.toml`.

## Canonical placeholders

| Placeholder | Source field in config.toml | Example expansion |
|---|---|---|
| `${PROJECT_NAMESPACE}` | `[project] namespace` | `code-agent` |
| `${PROJECT_DISPLAY_NAME}` | `[project] display_name` | `Claude Agent SDK for Emacs` |
| `${PROJECT_AUTHOR}` | `[project] author` | `Jingtao Xu` |
| `${PROJECT_REPO}` | `[project] repo_url` | `https://github.com/jingtaozf/emacs-agent` |
| `${LP_ROOT}` | `[paths] lp_root` (meta-repo) | `lp` |
| `${REPOS_ROOT}` | `[paths] repos_root` (meta-repo) | `repos` |
| `${LITERATE_AGENT_HOME}` | `[paths] literate_agent_home` | `~/projects/literate-agent` |

If a rule needs a placeholder not in this table, add it to
[`docs/config.org`](../docs/config.org) **before** using it in a rule.
Rules should never depend on values the renderer cannot supply.

## What this rule asks of authors

When writing or editing a rule under `rules/*.md`:

1. **Never hardcode a real project's identifier.** "claude-agent",
   "edo-literate", "skill-scout-server" all qualify as hardcoded.
   Replace with `${PROJECT_NAMESPACE}` (or the matching placeholder).
2. **Examples can be real symbols if and only if** they describe the
   doctrine literate-agent itself ships (e.g. citing
   `literate-programming-document-first.md` is fine; that file IS in
   literate-agent's tree).
3. **Cite consumer projects by `[GH-link]`** when you need to anchor
   to a real-world incident or trigger ("trigger: 2026-05-15
   mega-code-infra deploy" is fine — it's a one-time historical anchor,
   not a place the reader is meant to copy).

## Anti-patterns

- *Inline literal*: `(cl-defmethod claude-agent-backend-query ...)` —
  reader copies as-is, hits "void function" because their project
  isn't called claude-agent. Fix: `(cl-defmethod ${PROJECT_NAMESPACE}-backend-query ...)`.
- *Placeholder that breaks the language syntax*: `<reference-project>`
  is not valid Elisp / Python / TS — readers running the example
  before substitution get a parse error and assume the rule is broken.
  Fix: shell-style `${...}` is also invalid in those languages, but
  it visually signals "needs substitution" and won't be mistaken for
  a real identifier.
- *Half-placeholder, half-literal*: "Origin: ${PROJECT_NAMESPACE};
  see claude-agent's session.py" — the second name leaks the same
  hardcode the first cleaned up. Audit the whole paragraph.

## Why shell-style `${VAR}`

- Looks like a variable to every reader, in every language. Elisp,
  Python, TypeScript, shell, prose — `${VAR}` reliably reads as
  "needs to be expanded."
- Easy to grep: `grep -r '\${PROJECT_' rules/` lists every rule
  with placeholders.
- Compatible with `string.Template` in Python and most shells, so
  the renderer doesn't need a custom parser.
- Matches the `LITERATE_AGENT_HOME` env var convention already
  established in `CLAUDE.md`.

## Renderer behaviour

`scripts/build_readme.py` reads the consumer's
`.literate-agent/config.toml` (discovered upward from CWD), builds an
expansion dict, and `string.Template(text).safe_substitute(dict)`
each rule before writing to the consumer's destination README. Unknown
placeholders pass through unchanged so a missing config key surfaces
loudly rather than silently producing empty strings.

For consumers that just want to read rules unrendered (via Claude
Code's `@`-import), placeholders stay visible in chat — agents handle
this fine because `${PROJECT_NAMESPACE}` reads as a clear hole to fill
from session context.

## Enforcement

Reviewed during PR review of any rule edit. Grep check before merge:

```bash
# No literal claude-agent / edo-literate / etc. in rules/
grep -rE "claude-agent|edo-literate|skill-scout-server" rules/
```

Hits get flagged and replaced with `${PROJECT_NAMESPACE}`.
