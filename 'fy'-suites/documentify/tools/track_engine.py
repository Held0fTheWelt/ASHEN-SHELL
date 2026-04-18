from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from documentify.tools.document_builder import ROLE_MAP, collect_repository_context
from fy_platform.ai.workspace import workspace_root

try:
    from templatify.tools.template_render import render_with_header
except Exception:  # pragma: no cover
    render_with_header = None


MATURITY_LEVELS = ['inventory', 'skeleton', 'evidence-fill', 'cross-linked']


def _easy_doc(context: dict[str, Any]) -> str:
    services = ', '.join(context['services']) or 'no detected services'
    return (
        '# Easy Overview\n\n'
        'This repository is worked on with the autark fy suites.\n\n'
        f'Visible service/package areas: **{services}**.\n\n'
        '## Start points\n\n'
        '- Read the root README and docs/start-here first.\n'
        '- Use tests/run_tests.py to check the main Python test flow if present.\n'
        '- Use the generated role documents if you need a role-focused entry path.\n'
    )


def _technical_doc(context: dict[str, Any]) -> str:
    service_lines = ''.join(f'- `{svc}/`\n' for svc in context['services']) or '- none\n'
    workflow_lines = ''.join(f'- `{wf}`\n' for wf in context['workflows']) or '- none\n'
    key_doc_lines = ''.join(f'- `{doc}`\n' for doc in context['key_docs']) or '- none\n'
    return (
        '# Technical Reference\n\n'
        '## Service surfaces\n\n' + service_lines +
        '\n## Workflow surfaces\n\n' + workflow_lines +
        '\n## Key docs\n\n' + key_doc_lines
    )


def _role_doc(role: str, context: dict[str, Any], repo_root: Path) -> str:
    info = ROLE_MAP[role]
    existing = [p for p in info['paths'] if (repo_root / p).exists()]
    return (
        f'# {role.capitalize()} Guide\n\n'
        f"{info['summary']}\n\n"
        '## Relevant paths\n\n' + ''.join(f'- `{p}`\n' for p in existing)
    )


def _docs_site_blueprint(context: dict[str, Any]) -> str:
    services = ', '.join(context['services']) or 'none'
    docs_dirs = ', '.join(context['docs_dirs']) or 'none'
    workflows = ', '.join(context['workflows']) or 'none'
    return (
        '# Documentation Site Blueprint\n\n'
        'Recommended site model for the fy suites and exported outward docs.\n\n'
        '## Recommended structure\n\n'
        '- One main docs site can use multiple sidebars for easy, technical, role, and AI tracks.\n'
        '- If some documentation families later need different version histories or release lifecycles, move those families to distinct docs plugin instances.\n'
        '- Keep AI-readable bundles generated from the same source tree so search and export stay aligned.\n\n'
        '## Suggested sidebars\n\n'
        '- easy\n'
        '- technical\n'
        '- role-admin\n'
        '- role-developer\n'
        '- role-operator\n'
        '- role-writer\n'
        '- ai-read\n\n'
        '## Current repository signals\n\n'
        f'- services: {services}\n'
        f'- docs dirs: {docs_dirs}\n'
        f'- workflows: {workflows}\n'
    )


def _status_page(context: dict[str, Any]) -> str:
    services = ', '.join(context['services']) or 'no clear services found'
    docs_dirs = ', '.join(context['docs_dirs']) or 'no docs directories found'
    workflows = ', '.join(context['workflows']) or 'no workflows found'
    return (
        '# Documentation Status — Most-Recent-Next-Steps\n\n'
        'This page uses simple language.\n\n'
        '## What was found\n\n'
        f'- services: {services}\n'
        f'- docs directories: {docs_dirs}\n'
        f'- workflows: {workflows}\n\n'
        '## Most-Recent-Next-Steps\n\n'
        '- Read the easy overview first if you are new to this repository.\n'
        '- Use the technical reference when you need exact paths and system surfaces.\n'
        '- Open the role guide that matches your current job.\n'
        '- Use the AI-read bundle when another suite needs searchable structured context.\n'
        '- Build one main docs site with separate sidebars first. Only split into multiple docs instances when different version histories are really needed.\n'
    )


def _ai_read_bundle(context: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    aliases = {
        'repo': [repo_root.name, 'target-repo'],
        'tests': ['testing', 'verification', 'pytest'],
        'docs': ['documentation', 'manuals'],
    }
    chunks = [
        {'id': 'services', 'title': 'Services', 'text': ', '.join(context['services'])},
        {'id': 'docs_dirs', 'title': 'Documentation dirs', 'text': ', '.join(context['docs_dirs'])},
        {'id': 'workflows', 'title': 'CI workflows', 'text': ', '.join(context['workflows'])},
    ]
    return {'aliases': aliases, 'chunks': chunks, 'context': context}


def _render_template_or_fallback(family: str, name: str, context: dict[str, object], fallback: str) -> str:
    if render_with_header is None:
        return fallback
    try:
        ws = workspace_root(Path(__file__))
        rendered, _record = render_with_header(ws, family, name, context)
        return rendered
    except Exception:
        return fallback


def generate_track_bundle(repo_root: Path, out_dir: Path, maturity: str = 'evidence-fill') -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    context = collect_repository_context(repo_root)
    generated_files: list[str] = []

    tpl_context = {
        'services_csv': ', '.join(context['services']) or 'no detected services',
        'docs_dirs_csv': ', '.join(context['docs_dirs']) or 'none',
        'workflows_csv': ', '.join(context['workflows']) or 'none',
        'service_lines': ''.join(f'- `{svc}/`\n' for svc in context['services']) or '- none\n',
        'workflow_lines': ''.join(f'- `{wf}`\n' for wf in context['workflows']) or '- none\n',
        'key_doc_lines': ''.join(f'- `{doc}`\n' for doc in context['key_docs']) or '- none\n',
    }

    easy = out_dir / 'easy' / 'OVERVIEW.md'
    easy.parent.mkdir(parents=True, exist_ok=True)
    easy.write_text(_render_template_or_fallback('documentify', 'easy_overview', tpl_context, _easy_doc(context)), encoding='utf-8')
    generated_files.append(easy.relative_to(out_dir).as_posix())

    technical = out_dir / 'technical' / 'SYSTEM_REFERENCE.md'
    technical.parent.mkdir(parents=True, exist_ok=True)
    technical.write_text(_render_template_or_fallback('documentify', 'technical_reference', tpl_context, _technical_doc(context)), encoding='utf-8')
    generated_files.append(technical.relative_to(out_dir).as_posix())

    blueprint = out_dir / 'technical' / 'DOCS_SITE_BLUEPRINT.md'
    blueprint.write_text(_docs_site_blueprint(context), encoding='utf-8')
    generated_files.append(blueprint.relative_to(out_dir).as_posix())

    for role in ROLE_MAP:
        role_path = out_dir / f'role-{role}' / 'README.md'
        role_path.parent.mkdir(parents=True, exist_ok=True)
        info = ROLE_MAP[role]
        role_ctx = {
            'role_title': role.capitalize(),
            'role_summary': info['summary'],
            'relevant_path_lines': ''.join(f'- `{p}`\n' for p in info['paths'] if (repo_root / p).exists()) or '- none\n',
        }
        role_path.write_text(_render_template_or_fallback('documentify', 'role_guide', role_ctx, _role_doc(role, context, repo_root)), encoding='utf-8')
        generated_files.append(role_path.relative_to(out_dir).as_posix())

    ai_read = _ai_read_bundle(context, repo_root)
    ai_dir = out_dir / 'ai-read'
    ai_dir.mkdir(parents=True, exist_ok=True)
    (ai_dir / 'bundle.json').write_text(json.dumps(ai_read, indent=2), encoding='utf-8')
    fallback_md = '# AI Read Bundle\n\n' + ''.join(
        f"## {chunk['title']}\n\n{chunk['text']}\n\n" for chunk in ai_read['chunks']
    )
    (ai_dir / 'bundle.md').write_text(_render_template_or_fallback('documentify', 'ai_read', tpl_context, fallback_md), encoding='utf-8')
    generated_files.extend([
        (ai_dir / 'bundle.json').relative_to(out_dir).as_posix(),
        (ai_dir / 'bundle.md').relative_to(out_dir).as_posix(),
    ])

    status_dir = out_dir / 'status'
    status_dir.mkdir(parents=True, exist_ok=True)
    status_page = status_dir / 'MOST_RECENT_NEXT_STEPS.md'
    status_page.write_text(_status_page(context), encoding='utf-8')
    generated_files.append(status_page.relative_to(out_dir).as_posix())

    manifest = {
        'maturity': maturity,
        'tracks': ['easy', 'technical', *[f'role-{r}' for r in ROLE_MAP], 'ai-read', 'status'],
        'generated_files': generated_files,
        'context': context,
        'template_engine': 'templatify' if render_with_header is not None else 'builtin-fallback',
    }
    manifest_path = out_dir / 'document_manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    generated_files.append(manifest_path.relative_to(out_dir).as_posix())

    index_path = out_dir / 'INDEX.md'
    index_lines = ['# Documentify Index', '', f'- maturity: `{maturity}`', f"- template_engine: `{manifest['template_engine']}`", '', '## Tracks', '']
    index_lines.extend(f'- `{track}`' for track in manifest['tracks'])
    index_lines.extend(['', '## Generated files', ''])
    index_lines.extend(f'- `{path}`' for path in generated_files)
    index_path.write_text('\n'.join(index_lines) + '\n', encoding='utf-8')
    generated_files.append(index_path.relative_to(out_dir).as_posix())
    manifest['generated_count'] = len(generated_files)
    return manifest
