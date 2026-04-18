from __future__ import annotations

import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fy_platform.ai.workspace import sha256_text, slugify, utc_now, write_json, write_text

CURRENT_HINTS = [
    'contractify/reports/contract_audit.json',
    'contractify/reports/contract_discovery.json',
    'docs/ADR',
    'docs/platform',
]
LEGACY_HINTS = [
    "'fy'-suites/docs/ADR",
    "'fy'-suites/docs/platform",
    'docs/platform',
    'contractify/reports/contract_audit.json',
]


@dataclass
class ImportedArtifact:
    source: str
    destination: str
    kind: str


def _candidate_roots(base: Path) -> list[Path]:
    roots = [base]
    entries = [p for p in base.iterdir() if p.name != '__MACOSX'] if base.is_dir() else []
    if len(entries) == 1 and entries[0].is_dir():
        roots.append(entries[0])
    for child in entries:
        if child.is_dir() and child not in roots:
            roots.append(child)
    unique: list[Path] = []
    for item in roots:
        if item not in unique:
            unique.append(item)
    return unique


def _detect_extracted_root(base: Path) -> Path:
    for candidate in _candidate_roots(base):
        if (candidate / 'pyproject.toml').exists() or (candidate / 'fy_platform').exists() or (candidate / 'contractify').exists() or (candidate / "'fy'-suites").exists():
            return candidate
    return base


def _prepare_source(bundle: Path) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    if bundle.is_dir():
        return bundle.resolve(), None
    if bundle.suffix.lower() != '.zip':
        raise RuntimeError('unsupported_bundle_type')
    temp = tempfile.TemporaryDirectory(prefix='contractify-import-')
    with zipfile.ZipFile(bundle) as zf:
        zf.extractall(temp.name)
    return _detect_extracted_root(Path(temp.name)), temp


def _resolve_current_root(root: Path) -> Path:
    if (root / "'fy'-suites").is_dir() and not (root / 'fy_platform').is_dir() and not (root / 'contractify').is_dir():
        return root / "'fy'-suites"
    return root


def detect_bundle_layout(bundle: Path) -> dict[str, Any]:
    root, temp = _prepare_source(bundle)
    try:
        roots = _candidate_roots(root)
        for candidate in roots:
            current_root = _resolve_current_root(candidate)
            current_signals = [hint for hint in CURRENT_HINTS if (current_root / hint).exists()]
            legacy_signals = [hint for hint in LEGACY_HINTS if (candidate / hint).exists() or (current_root / hint).exists()]
            if (current_root / 'contractify').is_dir() and current_signals:
                return {'layout': 'current', 'root': str(current_root), 'signals': current_signals}
            if legacy_signals:
                return {'layout': 'legacy', 'root': str(candidate), 'signals': legacy_signals}
        return {'layout': 'unknown', 'root': str(root), 'signals': []}
    finally:
        if temp is not None:
            temp.cleanup()


def _copy_if_exists(src: Path, dst: Path, kind: str, collected: list[ImportedArtifact]) -> None:
    if src.is_dir():
        for item in src.rglob('*'):
            if item.is_dir():
                continue
            target = dst / item.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            collected.append(ImportedArtifact(str(item), str(target), kind))
    elif src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        collected.append(ImportedArtifact(str(src), str(dst), kind))


def import_contractify_bundle(bundle: Path, workspace: Path, *, legacy: bool = False) -> dict[str, Any]:
    source_root, temp = _prepare_source(bundle)
    try:
        layout_info = detect_bundle_layout(bundle)
        if layout_info['layout'] == 'unknown':
            raise RuntimeError('unknown_contractify_bundle_layout')
        current_root = _resolve_current_root(Path(layout_info['root']))
        layout = 'legacy-request-current-shape' if legacy and layout_info['layout'] != 'legacy' else layout_info['layout']

        import_id = f"{slugify(bundle.stem)}-{sha256_text(str(bundle.resolve()))[:8]}"
        import_root = workspace / 'contractify' / 'imports' / import_id
        normalized = import_root / 'normalized'
        normalized.mkdir(parents=True, exist_ok=True)
        collected: list[ImportedArtifact] = []

        roots_to_try = [current_root, Path(layout_info['root']), source_root]
        unique_roots: list[Path] = []
        for candidate in roots_to_try:
            if candidate not in unique_roots:
                unique_roots.append(candidate)
        for root in unique_roots:
            _copy_if_exists(root / 'contractify' / 'reports', normalized / 'contractify' / 'reports', 'contractify_reports', collected)
            _copy_if_exists(root / 'contractify' / 'state', normalized / 'contractify' / 'state', 'contractify_state', collected)
            _copy_if_exists(root / 'docs' / 'ADR', normalized / 'docs' / 'ADR', 'adr_docs', collected)
            _copy_if_exists(root / 'docs' / 'platform', normalized / 'docs' / 'platform', 'platform_docs', collected)
            _copy_if_exists(root / "'fy'-suites" / 'docs' / 'ADR', normalized / 'docs' / 'ADR', 'adr_docs_legacy', collected)
            _copy_if_exists(root / "'fy'-suites" / 'docs' / 'platform', normalized / 'docs' / 'platform', 'platform_docs_legacy', collected)
            _copy_if_exists(root / "'fy'-suites" / 'contractify' / 'reports', normalized / 'contractify' / 'reports', 'contractify_reports_legacy', collected)
            _copy_if_exists(root / 'contractify' / 'README.md', normalized / 'contractify' / 'README.md', 'contractify_readme', collected)

        report_dir = normalized / 'contractify' / 'reports'
        report_candidates = list(report_dir.glob('*.json')) if report_dir.is_dir() else []
        report_names = sorted(p.name for p in report_candidates)
        adr_dir = normalized / 'docs' / 'ADR'
        imported_adrs = sorted(str(p.relative_to(normalized)).replace('\\', '/') for p in adr_dir.rglob('*.md')) if adr_dir.is_dir() else []
        summary = {
            'bundle_path': str(bundle),
            'bundle_layout': layout,
            'import_id': import_id,
            'imported_at': utc_now(),
            'artifact_count': len(collected),
            'report_names': report_names,
            'imported_adr_count': len(imported_adrs),
            'imported_adrs': imported_adrs[:20],
            'notes': [
                'Current import is for bundles already shaped like modern fy-suite workspaces.' if not legacy else 'Legacy import translates older or nested bundle layouts into the current internal form.',
                'Imported data is normalized under contractify/imports/<id>/normalized and does not overwrite current workspace truth.',
            ],
        }
        write_json(import_root / 'import_summary.json', summary)
        md = ['# Contractify Import Summary', '', f"- import_id: `{import_id}`", f"- bundle_layout: `{layout}`", f"- artifact_count: {len(collected)}", f"- imported_adr_count: {len(imported_adrs)}", '', '## Imported reports', '']
        if report_names:
            md.extend(f'- `{name}`' for name in report_names)
        else:
            md.append('- none detected')
        md.extend(['', '## Notes', ''])
        md.extend(f'- {item}' for item in summary['notes'])
        write_text(import_root / 'IMPORT_SUMMARY.md', '\n'.join(md) + '\n')
        return {
            'ok': True,
            'import_id': import_id,
            'bundle_layout': layout,
            'artifact_count': len(collected),
            'normalized_root': str(import_root.relative_to(workspace)),
            'report_names': report_names,
            'imported_adr_count': len(imported_adrs),
        }
    finally:
        if temp is not None:
            temp.cleanup()
