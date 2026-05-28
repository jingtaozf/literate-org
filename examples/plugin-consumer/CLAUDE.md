# ${PROJECT_DISPLAY_NAME} — agent instructions

This file is `@`-imported into every Claude Code session for this
project. literate-agent's full doctrine is inlined via the first
line below; project-specific overrides follow.

@~/projects/literate-agent/CLAUDE.md

## Project context

- **Namespace** (symbol prefix): `${PROJECT_NAMESPACE}`
- **Repo**: ${PROJECT_REPO}
- **Author**: ${PROJECT_AUTHOR}

## Local rules (override or extend literate-agent doctrine)

Add `.claude/rules/<rule-name>.md` files for project-specific
discipline. Examples a real project might add:

- `.claude/rules/no-backward-compatibility.md`
- `.claude/rules/e2e-testing-strategy.md`
- `.claude/rules/<your-project>-dev-conventions.md`

## Local skills

Add `.claude/skills/<skill>/SKILL.md` for project-specific skills.
These auto-activate when their trigger phrases appear.

## Per-tool conventions

(Describe how YOUR project uses Bash, Edit, MCP tools, etc.)
