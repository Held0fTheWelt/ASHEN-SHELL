from __future__ import annotations

import json
import zipfile
from pathlib import Path

from contractify.adapter.service import ContractifyAdapter


def _make_bundle(tmp_path: Path, *, legacy: bool) -> Path:
    src = tmp_path / ('legacy_bundle' if legacy else 'current_bundle')
    root = src
    if not legacy:
        (root / 'fy_platform').mkdir(parents=True, exist_ok=True)
        (root / 'pyproject.toml').write_text('[project]\nname="fy-suites"\nversion="1.0.0"\n', encoding='utf-8')
        adr_dir = root / 'docs' / 'ADR'
    else:
        adr_dir = root / "'fy'-suites" / 'docs' / 'ADR'
    (root / 'contractify' / 'reports').mkdir(parents=True, exist_ok=True)
    adr_dir.mkdir(parents=True, exist_ok=True)
    (root / 'contractify' / 'reports' / 'contract_audit.json').write_text(json.dumps({'ok': True}), encoding='utf-8')
    (adr_dir / 'ADR-0001-example.md').write_text('# ADR-0001\n\nExample\n', encoding='utf-8')
    bundle = tmp_path / ('legacy_bundle.zip' if legacy else 'current_bundle.zip')
    with zipfile.ZipFile(bundle, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for item in src.rglob('*'):
            if item.is_dir():
                continue
            zf.write(item, arcname=str(item.relative_to(src)))
    return bundle


def _make_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    (workspace / 'fy_governance_enforcement.yaml').write_text('enforce: true\n', encoding='utf-8')
    (workspace / 'README.md').write_text('# fy\n', encoding='utf-8')
    (workspace / 'pyproject.toml').write_text('[project]\nname="fy-suites"\nversion="1.0.0"\n', encoding='utf-8')
    for name in ['requirements.txt', 'requirements-dev.txt', 'requirements-test.txt']:
        (workspace / name).write_text('', encoding='utf-8')
    suite = workspace / 'contractify'
    for rel in ['adapter', 'tools', 'reports', 'state', 'templates']:
        (suite / rel).mkdir(parents=True, exist_ok=True)
    (suite / 'README.md').write_text('# contractify\n', encoding='utf-8')
    (suite / 'adapter' / 'service.py').write_text('class X: pass\n', encoding='utf-8')
    (suite / 'adapter' / 'cli.py').write_text('def main():\n    return 0\n', encoding='utf-8')
    return workspace


def test_contractify_imports_current_bundle(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    adapter = ContractifyAdapter(workspace)
    bundle = _make_bundle(tmp_path, legacy=False)
    result = adapter.import_bundle(str(bundle), legacy=False)
    assert result['ok'] is True
    assert result['bundle_layout'] in {'current', 'legacy-request-current-shape'}
    assert result['artifact_count'] >= 1


def test_contractify_imports_legacy_bundle(tmp_path: Path) -> None:
    workspace = _make_workspace(tmp_path)
    adapter = ContractifyAdapter(workspace)
    bundle = _make_bundle(tmp_path, legacy=True)
    result = adapter.import_bundle(str(bundle), legacy=True)
    assert result['ok'] is True
    assert result['bundle_layout'].startswith('legacy')
    assert result['imported_adr_count'] >= 1
