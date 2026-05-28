# meta-repo starter kit

Use this when your project hosts **many submodules** and authors
each one's production source prose-first as Org-mode. Examples in
the wild: `edo-literate`, multi-package LP repos.

## Layout

```
your-meta-repo/
├── CLAUDE.md
├── .literate-agent/
│   └── config.toml         # shape="meta-repo"
├── lp/                     # LP source tree
│   ├── INDEX.org           # auto-generated
│   ├── decisions-log.org   # accepted/rejected design decisions
│   ├── draft.org           # in-flight proposals
│   └── <sub>/              # one dir per submodule
│       ├── _project.org    # submodule overview
│       └── <concept>.org   # tangles to repos/<sub>/<...>
└── repos/                  # submodules check out here
    └── <sub>/              # tangled outputs land here
```

## Setup

```bash
git clone https://github.com/jingtaozf/literate-agent.git ~/projects/literate-agent
cp -r ~/projects/literate-agent/examples/meta-repo/.literate-agent ./
cp ~/projects/literate-agent/examples/meta-repo/CLAUDE.md ./
```

Edit `.literate-agent/config.toml`; describe each submodule under
`[groups.<sub>]`.

## Where to read next

- `~/projects/literate-agent/README.org` — plugin overview.
- `~/projects/literate-agent/docs/config.org` — config schema +
  meta-repo specifics.
- `~/projects/literate-agent/rules/lp-noweb-for-big-blocks.md` —
  noweb pattern, frequently needed in meta-repos.
- `~/projects/literate-agent/skills/lp-resync/SKILL.md` —
  source ↔ tangle drift roundtrip workflow.
