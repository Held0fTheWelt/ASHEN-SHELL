"""Resolve monorepo root and Contractify hub directory paths."""
from __future__ import annotations

from pathlib import Path

from fy_platform.core.project_resolver import resolve_project_root

FY_SUITES_DIRNAME = "'fy'-suites"



def _current_or_legacy_suite_dir(repo: Path, suite: str) -> Path:
    direct = repo / suite
    if direct.is_dir() or (repo / 'fy_platform').is_dir():
        return direct
    nested = repo / FY_SUITES_DIRNAME / suite
    return nested


def repo_root(*, start: Path | None = None) -> Path:
    """Return the World of Shadows repository root (directory containing hub ``pyproject.toml``).

    If the environment variable ``CONTRACTIFY_REPO_ROOT`` is set to an existing directory,
    that path is returned (useful for partial checkouts, CI slices, or ZIP extracts without
    walking from this file). Tests patch this function instead of relying on the env var.
    """
    return resolve_project_root(
        start=start,
        env_var="CONTRACTIFY_REPO_ROOT",
        marker_text=None,
    )


def contractify_hub_dir(repo: Path | None = None) -> Path:
    """Return the Contractify hub directory (``'fy'-suites/contractify``)."""
    r = repo or repo_root()
    return r / FY_SUITES_DIRNAME / "contractify"
