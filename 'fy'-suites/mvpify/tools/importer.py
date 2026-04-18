from __future__ import annotations

import shutil
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

from fy_platform.ai.workspace import sha256_text, slugify, utc_now, write_json, write_text
from .models import MVPArtifact, SuiteSignal
from .repo_paths import docs_imports_root, imports_root

KEY_FILES = {
    'README.md': 'project_readme',
    'docker-compose.yml': 'docker_stack',
    'docker-up.py': 'docker_entrypoint',
    'fy-manifest.yaml': 'fy_manifest',
    'tests/run_tests.py': 'test_runner',
    'pyproject.toml': 'python_project',
}

SUITE_NAMES = (
    'contractify', 'despaghettify', 'docify', 'documentify', 'dockerify',
    'testify', 'templatify', 'usabilify', 'securify', 'observifyfy', 'mvpify',
)


def _scan_root(root: Path) -> dict:
    artifacts: list[MVPArtifact] = []
    counters = Counter()
    doc_files: list[str] = []
    implementation_files: list[str] = []
    for path in root.rglob('*'):
        if path.is_dir():
            continue
        rel = path.relative_to(root).as_posix()
        for suffix, kind in KEY_FILES.items():
            if rel.endswith(suffix):
                artifacts.append(MVPArtifact(rel, kind, 'key surface'))
                counters[kind] += 1
        if '/docs/' in f'/{rel}/' or rel.startswith('docs/'):
            counters['docs_files'] += 1
            doc_files.append(rel)
        if 'MVP' in rel or 'implementation' in rel.lower():
            implementation_files.append(rel)
        if '/tests/' in f'/{rel}/' or rel.startswith('tests/'):
            counters['test_files'] += 1
        if '/.github/workflows/' in f'/{rel}/':
            counters['workflow_files'] += 1
        if "'fy'-suites/" in rel or rel.startswith("'fy'-suites/"):
            counters['fy_suite_files'] += 1
        if rel.endswith('.md'):
            counters['markdown_files'] += 1
        if rel.endswith('.py'):
            counters['python_files'] += 1
        if rel.endswith('.json'):
            counters['json_files'] += 1
        if rel.endswith('.yml') or rel.endswith('.yaml'):
            counters['yaml_files'] += 1
    suite_signals = []
    for suite in SUITE_NAMES:
        evidence = []
        for path in root.rglob('*'):
            rel = path.relative_to(root).as_posix()
            if suite in rel:
                evidence.append(rel)
                if len(evidence) == 5:
                    break
        suite_signals.append(SuiteSignal(suite, bool(evidence), evidence, relevance='primary' if suite in {'contractify', 'despaghettify', 'mvpify'} else 'supporting'))
    return {
        'root': str(root),
        'artifact_count': sum(1 for _ in root.rglob('*') if _.is_file()),
        'artifacts': [a.to_dict() for a in artifacts],
        'counters': dict(counters),
        'suite_signals': [s.to_dict() for s in suite_signals],
        'mvp_candidate_roots': [p.relative_to(root).as_posix() for p in root.iterdir() if p.is_dir()][:20],
        'doc_files': sorted(doc_files)[:200],
        'implementation_files': sorted(implementation_files)[:200],
    }


def _detect_extracted_root(base: Path) -> Path:
    entries = [p for p in base.iterdir() if p.name != '__MACOSX']
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return base


def _prepare_source(*, source_root: str = '', mvp_zip: str = '') -> tuple[Path, tempfile.TemporaryDirectory[str] | None, str]:
    if bool(source_root) == bool(mvp_zip):
        raise ValueError('Provide exactly one of source_root or mvp_zip')
    if source_root:
        return Path(source_root).resolve(), None, str(Path(source_root).resolve())
    zip_path = Path(mvp_zip).resolve()
    temp = tempfile.TemporaryDirectory(prefix='mvpify-import-')
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(temp.name)
    root = _detect_extracted_root(Path(temp.name))
    return root, temp, str(zip_path)


def inspect_source(*, source_root: str = '', mvp_zip: str = '') -> dict:
    root, temp, source = _prepare_source(source_root=source_root, mvp_zip=mvp_zip)
    try:
        payload = _scan_root(root)
        payload['source_mode'] = 'directory' if source_root else 'zip'
        payload['source'] = source
        return payload
    finally:
        if temp is not None:
            temp.cleanup()


def _copy_tree(src: Path, dst: Path, refs: list[dict[str, Any]]) -> int:
    count = 0
    if not src.exists():
        return count
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        refs.append({'source': str(src), 'destination': str(dst), 'kind': 'file'})
        return 1
    for item in src.rglob('*'):
        if item.is_dir():
            continue
        target = dst / item.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        refs.append({'source': str(item), 'destination': str(target), 'kind': 'file'})
        count += 1
    return count


def materialize_import(*, repo_root: Path, source_root: str = '', mvp_zip: str = '') -> dict[str, Any]:
    root, temp, source = _prepare_source(source_root=source_root, mvp_zip=mvp_zip)
    try:
        inventory = _scan_root(root)
        import_id = f"{slugify(Path(source).stem)}-{sha256_text(source)[:8]}"
        normalized_root = imports_root(repo_root) / import_id / 'normalized'
        mirrored_docs_root = docs_imports_root(repo_root) / import_id
        normalized_root.mkdir(parents=True, exist_ok=True)
        mirrored_docs_root.mkdir(parents=True, exist_ok=True)
        refs: list[dict[str, Any]] = []

        copied_docs = 0
        copied_docs += _copy_tree(root / 'docs', normalized_root / 'docs', refs)
        copied_docs += _copy_tree(root / "'fy'-suites" / 'docs', normalized_root / 'docs', refs)
        copied_docs += _copy_tree(root / 'reports', normalized_root / 'reports', refs)

        mirrored = 0
        mirrored += _copy_tree(normalized_root / 'docs', mirrored_docs_root, refs)
        readme = root / 'README.md'
        if readme.exists():
            mirrored += _copy_tree(readme, mirrored_docs_root / 'README.md', refs)

        reference_manifest = {
            'import_id': import_id,
            'source': source,
            'source_mode': 'directory' if source_root else 'zip',
            'mirrored_docs_root': str(mirrored_docs_root.relative_to(repo_root)),
            'normalized_root': str(normalized_root.relative_to(repo_root)),
            'mirrored_file_count': mirrored,
            'copied_doc_like_count': copied_docs,
            'created_at': utc_now(),
            'notes': [
                'Imported MVP docs are mirrored into docs/MVPs/imports/<id> so temporary implementation folders may later be removed.',
                'The normalized import lane remains under mvpify/imports/<id>/normalized for traceability and restartability.',
            ],
        }
        write_json(normalized_root / 'import_inventory.json', inventory)
        write_json(normalized_root / 'reference_manifest.json', reference_manifest)
        write_json(mirrored_docs_root / 'mvpify_reference_manifest.json', reference_manifest)
        write_text(
            mirrored_docs_root / 'README.md',
            "\n".join(
                [
                    '# Imported MVP documentation',
                    '',
                    f"- import_id: `{import_id}`",
                    f"- source: `{source}`",
                    f"- normalized_root: `{reference_manifest['normalized_root']}`",
                    '',
                    'This directory mirrors the MVP documentation that was read from the imported bundle.',
                    'It exists so a temporary implementation folder can later be removed without losing the documentation trail.',
                    '',
                ]
            ),
        )
        return {
            'ok': True,
            'import_id': import_id,
            'source': source,
            'source_mode': 'directory' if source_root else 'zip',
            'artifact_count': inventory['artifact_count'],
            'inventory': inventory,
            'normalized_root': str(normalized_root.relative_to(repo_root)),
            'mirrored_docs_root': str(mirrored_docs_root.relative_to(repo_root)),
            'mirrored_file_count': mirrored,
            'references_recorded': len(refs),
        }
    finally:
        if temp is not None:
            temp.cleanup()
