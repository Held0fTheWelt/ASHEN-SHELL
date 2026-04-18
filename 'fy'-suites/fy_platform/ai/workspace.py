from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LEGACY_NESTED_DIRNAME = "'fy'-suites"
INTERNAL_DIRNAME = 'internal'


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    out = []
    for ch in value.lower():
        out.append(ch if ch.isalnum() else '-')
    text = ''.join(out).strip('-')
    while '--' in text:
        text = text.replace('--', '-')
    return text or 'unknown'


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_text_safe(path: Path) -> str:
    return path.read_text(encoding='utf-8', errors='replace')


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def workspace_root(start: Path | None = None) -> Path:
    start = (start or Path(__file__)).resolve()
    explicit_dir = start if start.is_dir() else None
    for ancestor in [start, *start.parents]:
        if ancestor.is_dir() and (ancestor / 'fy_governance_enforcement.yaml').is_file():
            return ancestor
        if ancestor.is_dir() and (ancestor / 'README.md').is_file() and (ancestor / 'fy_platform').is_dir():
            return ancestor
    if explicit_dir is not None:
        return explicit_dir
    raise RuntimeError(f'Could not resolve fy workspace root from {start}')


def legacy_nested_root(workspace: Path) -> Path:
    return workspace / LEGACY_NESTED_DIRNAME


def internal_root(workspace: Path) -> Path:
    return workspace / INTERNAL_DIRNAME


def fy_suites_root(workspace: Path) -> Path:
    """Return the canonical current suite root.

    The current layout treats the workspace root itself as the fy-suite root.
    Older packages may still contain a nested ``'fy'-suites`` directory; callers
    can use :func:`legacy_nested_root` if they need to inspect or migrate it.
    """
    return workspace


def internal_docs_root(workspace: Path) -> Path:
    return fy_suites_root(workspace) / 'docs'


def internal_adr_root(workspace: Path) -> Path:
    return internal_docs_root(workspace) / 'ADR'


def internal_platform_docs_root(workspace: Path) -> Path:
    return internal_docs_root(workspace) / 'platform'


def migrate_legacy_nested_layout(workspace: Path) -> dict[str, list[str]]:
    """Move selected legacy nested doc paths into the current top-level layout.

    The migration is intentionally conservative: it only lifts documentation
    surfaces that are safe to merge into the current canonical layout. Suite code
    is not moved automatically here; package import paths resolve the current
    layout first and only use legacy migration helpers where transitional
    compatibility is still required.
    """
    migrated: list[str] = []
    legacy = legacy_nested_root(workspace)
    if not legacy.is_dir():
        return {'migrated': migrated}

    for rel in ['docs', 'docs/ADR', 'docs/platform']:
        src = legacy / rel
        dst = workspace / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            for item in src.rglob('*'):
                if item.is_dir():
                    continue
                target = dst / item.relative_to(src)
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    shutil.copy2(item, target)
                    migrated.append(str(target.relative_to(workspace)))
    return {'migrated': migrated}


def ensure_workspace_layout(root: Path) -> dict[str, list[str] | str]:
    created: list[str] = []
    for rel in [
        '.fydata/registry/objects',
        '.fydata/index',
        '.fydata/journal',
        '.fydata/runs',
        '.fydata/cache',
        '.fydata/bindings',
        '.fydata/backups',
        '.fydata/metrics',
        'docs',
        'docs/ADR',
        'docs/platform',
        'internal',
        'internal/docs',
        'internal/docs/ADR',
        'internal/docs/platform',
    ]:
        p = root / rel
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            created.append(rel)
    migration = migrate_legacy_nested_layout(root)
    return {'workspace_root': str(root), 'created': created, 'migrated': migration['migrated']}


def write_platform_doc_artifacts(
    workspace: Path,
    *,
    stem: str,
    json_payload: Any | None = None,
    markdown_text: str | None = None,
) -> dict[str, str | None]:
    """Write platform-facing docs to the current canonical docs location.

    Current canonical location is ``docs/platform`` under the workspace root.
    Legacy nested consumers should be migrated to this form. Compatibility keys
    are still returned so older callers can adapt without crashing. Internal
    mirrors now live under `internal/`, while the canonical release-facing path
    remains `docs/platform` at the workspace root.
    """
    workspace = workspace_root(workspace)
    out_dir = internal_platform_docs_root(workspace)
    out_dir.mkdir(parents=True, exist_ok=True)

    json_rel = md_rel = None
    if json_payload is not None:
        out_json = out_dir / f'{stem}.json'
        write_json(out_json, json_payload)
        json_rel = str(out_json.relative_to(workspace))
    if markdown_text is not None:
        out_md = out_dir / f'{stem}.md'
        write_text(out_md, markdown_text)
        md_rel = str(out_md.relative_to(workspace))

    internal_platform = internal_root(workspace) / 'docs' / 'platform'
    internal_platform.mkdir(parents=True, exist_ok=True)
    if json_payload is not None:
        write_json(internal_platform / f'{stem}.json', json_payload)
    if markdown_text is not None:
        write_text(internal_platform / f'{stem}.md', markdown_text)
    return {
        'json_path': json_rel,
        'md_path': md_rel,
        'canonical_json_path': json_rel,
        'canonical_md_path': md_rel,
        'legacy_json_path': json_rel,
        'legacy_md_path': md_rel,
        'internal_json_path': str((internal_root(workspace) / 'docs' / 'platform' / f'{stem}.json').relative_to(workspace)) if json_payload is not None else None,
        'internal_md_path': str((internal_root(workspace) / 'docs' / 'platform' / f'{stem}.md').relative_to(workspace)) if markdown_text is not None else None,
    }


def target_repo_id(target_repo_root: Path) -> str:
    return slugify(target_repo_root.name) + '-' + sha256_text(str(target_repo_root.resolve()))[:8]


def suite_hub_dir(workspace: Path, suite: str) -> Path:
    return workspace / suite


def internal_run_dir(workspace: Path, suite: str, run_id: str) -> Path:
    return workspace / '.fydata' / 'runs' / suite / run_id


def binding_path(workspace: Path, suite: str) -> Path:
    return workspace / '.fydata' / 'bindings' / f'{suite}.json'
