# plugin-consumer starter kit

Use this when your project is a **single repo** that wants
literate-agent's doctrine as a Claude Code plugin + `@`-imported
rules. Examples in the wild: `emacs-agent`, most single-tool repos.

## Layout

```
your-project/
├── CLAUDE.md                       # @-imports literate-agent/CLAUDE.md + project addenda
├── .literate-agent/
│   └── config.toml                 # consumer-specific values (namespace, author, etc.)
└── (your project's existing files)
```

## Setup

1. Clone literate-agent once at a stable path:

   ```bash
   git clone https://github.com/jingtaozf/literate-agent.git ~/projects/literate-agent
   ```

2. From this starter, copy the two files into your project root:

   ```bash
   cp -r ~/projects/literate-agent/examples/plugin-consumer/.literate-agent ./
   cp ~/projects/literate-agent/examples/plugin-consumer/CLAUDE.md ./
   ```

3. Edit `.literate-agent/config.toml` to match your project.

4. Launch Claude Code with the plugin loaded:

   ```bash
   claude --plugin-dir ~/projects/literate-agent ...
   ```

That's it. literate-agent's doctrine + skills + hooks + commands
become available; placeholders in any rendered doc (via
`build_readme.py`) expand using your `config.toml`.

## Where to read next

- `~/projects/literate-agent/README.org` — full plugin overview.
- `~/projects/literate-agent/docs/config.org` — `config.toml`
  schema reference.
- `~/projects/literate-agent/rules/placeholder-convention.md` —
  what `${PROJECT_NAMESPACE}` etc. mean.
