from __future__ import annotations

from pathlib import Path

LEGACY_NESTED_DIRNAME = "'fy'-suites"
INTERNAL_DIRNAME = 'internal'


def resolve_repo_root(start: str | Path | None = None) -> Path:
    path = Path(start or '.').resolve()
    for candidate in [path, *path.parents]:
        if (candidate / 'pyproject.toml').exists() and ((candidate / '.fydata').exists() or (candidate / 'fy_platform').exists()):
            return candidate
    return path


def fy_internal_root(repo_root: Path) -> Path:
    return repo_root


def fy_docs_root(repo_root: Path) -> Path:
    direct = repo_root / 'docs'
    legacy = repo_root / LEGACY_NESTED_DIRNAME / 'docs'
    if legacy.exists() and not direct.exists():
        return legacy
    return direct


def fy_internal_root_mirror(repo_root: Path) -> Path:
    return repo_root / INTERNAL_DIRNAME


def fy_adr_root(repo_root: Path) -> Path:
    return fy_docs_root(repo_root) / 'ADR'


def fy_observifyfy_root(repo_root: Path) -> Path:
    direct = repo_root / 'observifyfy'
    legacy = repo_root / LEGACY_NESTED_DIRNAME / 'observifyfy'
    internal = repo_root / INTERNAL_DIRNAME / 'observifyfy'
    if direct.exists():
        return direct
    if internal.exists():
        return internal
    if legacy.exists():
        return legacy
    return direct


def ensure_internal_layout(repo_root: Path) -> dict[str, str]:
    created = {}
    for path in [fy_docs_root(repo_root), fy_adr_root(repo_root), fy_observifyfy_root(repo_root), fy_observifyfy_root(repo_root) / 'reports', fy_observifyfy_root(repo_root) / 'state']:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created[str(path.relative_to(repo_root))] = 'created'
    return created
