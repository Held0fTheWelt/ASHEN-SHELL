"""Resolve monorepo root and Contractify hub directory paths."""
from __future__ import annotations

import os
from pathlib import Path

FY_SUITES_DIRNAME = "'fy'-suites"


def repo_root(*, start: Path | None = None) -> Path:
    """Return the World of Shadows repository root (directory containing hub ``pyproject.toml``).

    If the environment variable ``CONTRACTIFY_REPO_ROOT`` is set to an existing directory,
    that path is returned (useful for partial checkouts, CI slices, or ZIP extracts without
    walking from this file). Tests patch this function instead of relying on the env var.
    """
    env = os.environ.get("CONTRACTIFY_REPO_ROOT", "").strip()
    if env:
        forced = Path(env).expanduser().resolve()
        if forced.is_dir():
            marker = forced / "pyproject.toml"
            if marker.is_file() and "world-of-shadows-hub" in marker.read_text(
                encoding="utf-8",
                errors="replace",
            ):
                return forced
    p = (start or Path(__file__)).resolve()
    for ancestor in p.parents:
        toml = ancestor / "pyproject.toml"
        if not toml.is_file():
            continue
        try:
            if "world-of-shadows-hub" not in toml.read_text(encoding="utf-8", errors="replace"):
                continue
        except OSError:
            continue
        return ancestor
    msg = f"Could not resolve repository root from {p}"
    raise RuntimeError(msg)


def contractify_hub_dir(repo: Path | None = None) -> Path:
    """Return the Contractify hub directory (``'fy'-suites/contractify``)."""
    r = repo or repo_root()
    return r / FY_SUITES_DIRNAME / "contractify"
