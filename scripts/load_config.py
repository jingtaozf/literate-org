"""Loader for ``.literate-agent/config.toml``.

Walks upward from CWD (or an explicit start) looking for the file,
parses it via ``tomllib`` (Python 3.11+), applies defaults, and
returns a flat ``dict[str, str]`` keyed by placeholder name.

Other scripts pipe the dict into ``string.Template`` to expand
``${PROJECT_NAMESPACE}`` and friends in templates / rule prose.

See ``docs/config.org`` for the full schema.
"""

from __future__ import annotations

import os
import string
import sys
import tomllib
from pathlib import Path

CONFIG_DIRNAME = ".literate-agent"
CONFIG_FILENAME = "config.toml"

# Default values used when no config.toml is found or when a key is
# absent. Match the table in docs/config.org § "Default fallback".
DEFAULTS: dict[str, str] = {
    "PROJECT_NAMESPACE": "project",
    "PROJECT_DISPLAY_NAME": "project",
    "PROJECT_AUTHOR": "",
    "PROJECT_REPO": "",
    "LITERATE_AGENT_HOME": "~/projects/literate-agent",
    "LP_ROOT": "lp",
    "REPOS_ROOT": "repos",
    "TANGLE_MAKE_TARGET": "tangle",
}

# Mapping from (toml-table, toml-key) → placeholder name.
# Order matters only for documentation; lookup is by tuple.
_TOML_MAP: list[tuple[str, str, str]] = [
    ("project", "namespace", "PROJECT_NAMESPACE"),
    ("project", "display_name", "PROJECT_DISPLAY_NAME"),
    ("project", "author", "PROJECT_AUTHOR"),
    ("project", "repo_url", "PROJECT_REPO"),
    ("paths", "literate_agent_home", "LITERATE_AGENT_HOME"),
    ("paths", "lp_root", "LP_ROOT"),
    ("paths", "repos_root", "REPOS_ROOT"),
    ("paths", "tangle_make_target", "TANGLE_MAKE_TARGET"),
]


def discover_config_path(start: Path | None = None) -> Path | None:
    """Find ``.literate-agent/config.toml`` by walking upward from *start*.

    Respects ``$LITERATE_AGENT_CONFIG_PATH`` env override.

    Returns ``None`` if no config file is found.
    """
    explicit = os.environ.get("LITERATE_AGENT_CONFIG_PATH")
    if explicit:
        path = Path(explicit).expanduser()
        return path if path.is_file() else None

    current = (start or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        candidate = parent / CONFIG_DIRNAME / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
    return None


def load_config(start: Path | None = None) -> dict[str, str]:
    """Discover + parse + apply defaults.

    Returns a flat ``dict[str, str]`` ready for ``string.Template``.
    Missing config file ⇒ all defaults.
    """
    resolved: dict[str, str] = dict(DEFAULTS)
    path = discover_config_path(start)
    if path is None:
        return resolved

    try:
        with path.open("rb") as f:
            raw = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        # Surface loud — silent corruption of the placeholder map
        # would render placeholders to defaults and the consumer
        # would chase phantom bugs.
        print(
            f"[load_config] failed to parse {path}: {exc}",
            file=sys.stderr,
        )
        return resolved

    # Top-level [project], [layout], [paths]
    for table_name, key_name, placeholder in _TOML_MAP:
        table = raw.get(table_name, {})
        if not isinstance(table, dict):
            continue
        value = table.get(key_name)
        if isinstance(value, str) and value:
            resolved[placeholder] = value

    # Special-case: [project] display_name defaults to namespace if absent
    if (
        "PROJECT_NAMESPACE" in resolved
        and resolved["PROJECT_DISPLAY_NAME"] == DEFAULTS["PROJECT_DISPLAY_NAME"]
    ):
        # Only override default if a namespace was provided
        ns = resolved["PROJECT_NAMESPACE"]
        if ns != DEFAULTS["PROJECT_NAMESPACE"]:
            resolved["PROJECT_DISPLAY_NAME"] = ns

    # [layout].shape — store as SHAPE placeholder for templates
    layout = raw.get("layout", {})
    if isinstance(layout, dict) and isinstance(layout.get("shape"), str):
        resolved["SHAPE"] = layout["shape"]
    else:
        resolved.setdefault("SHAPE", "plugin-consumer")

    # [placeholders.extra] — consumer-defined extras
    placeholders = raw.get("placeholders", {})
    if isinstance(placeholders, dict):
        extras = placeholders.get("extra", {})
        if isinstance(extras, dict):
            for k, v in extras.items():
                if isinstance(k, str) and isinstance(v, str):
                    resolved[k] = v

    return resolved


def expand_placeholders(text: str, cfg: dict[str, str] | None = None) -> str:
    """Expand ``${VAR}`` placeholders in *text* using *cfg*.

    Unknown placeholders pass through unchanged (``safe_substitute``)
    — loud surface > silent empty string.
    """
    if cfg is None:
        cfg = load_config()
    return string.Template(text).safe_substitute(cfg)


def main() -> int:
    """CLI helper: print resolved config as ``KEY=VALUE`` lines (sh-eval-able)."""
    cfg = load_config()
    for key in sorted(cfg):
        print(f"{key}={cfg[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
