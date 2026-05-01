# Lessons

Append-only log of mistakes the agent (or maintainer) made and the rule
that prevents them next time. Two-tier promotion contract:

1. *Every* user correction → a new entry below.
2. After **≥3 entries of the same kind**, promote the corrective rule
   into `.claude/rules/<topic>.md` (or, if it's a top-level project
   constraint, into `CLAUDE.md` with `IMPORTANT/ALWAYS/NEVER` emphasis).
3. Promotion deletes the lessons entries that motivated it (so this
   file stays small) and adds a `Promoted: <date> → <rule path>` note
   in their place.

## Format

```
### YYYY-MM-DD — <one-line summary>

- *Mistake type:* <e.g. depth-cap drilling, .py edit attempt, missing prose>
- *Context:* <what was being done; which file; which session>
- *Correction:* <what the user said>
- *Rule for next time:* <one sentence the agent can act on>
```

Entries newest-on-top.

## Entries

(none yet — will accumulate as we go)

## Promoted entries (history)

(none yet)
