# ${PROJECT_DISPLAY_NAME} — agent instructions (meta-repo)

This meta-repo hosts many submodules under `repos/`. Each
submodule's production source is authored prose-first as Org-mode
in `lp/<sub>/*.org` and tangled into `repos/<sub>/<...>`.

@~/projects/literate-agent/CLAUDE.md

## Meta-repo context

- **Namespace**: `${PROJECT_NAMESPACE}`
- **Repo**: ${PROJECT_REPO}
- **LP source root**: `${LP_ROOT}/<sub>/`
- **Submodule tree**: `${REPOS_ROOT}/<sub>/`

## Critical rules for this shape

- *Never* edit `${REPOS_ROOT}/<sub>/<...>.py` directly — those files
  are tangle outputs. Edit the matching `${LP_ROOT}/<sub>/<...>.org`
  source instead. (Enforced by literate-agent's
  `block-tangled-edit` PreToolUse hook.)
- `make tangle FILE=${LP_ROOT}/<sub>/<x>.org` to refresh a single
  submodule's output.
- `make tangle-all` to refresh everything (slow; CI gate).

## Where to read next

- `${LP_ROOT}/INDEX.org` — auto-generated catalogue of all submodules.
- `${LP_ROOT}/<sub>/README.org` — per-submodule entry point.
