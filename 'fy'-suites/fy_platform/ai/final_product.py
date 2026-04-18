from __future__ import annotations

from pathlib import Path
from typing import Any

from fy_platform.ai.contracts import (
    COMMAND_ENVELOPE_COMPATIBILITY,
    COMMAND_ENVELOPE_SCHEMA_VERSION,
    MANIFEST_COMPATIBILITY,
)
from fy_platform.ai.policy.suite_quality_policy import CORE_SUITES, OPTIONAL_SUITES, evaluate_suite_quality
from fy_platform.ai.production_readiness import workspace_production_readiness
from fy_platform.ai.release_readiness import suite_release_readiness, workspace_release_readiness
from fy_platform.ai.workspace import utc_now, workspace_root, write_json, write_text, write_platform_doc_artifacts
from fy_platform.ai.workspace_status_site import build_workspace_status_site

GENERIC_LIFECYCLE_COMMANDS = [
    'init',
    'inspect',
    'audit',
    'explain',
    'prepare-context-pack',
    'compare-runs',
    'clean',
    'reset',
    'triage',
    'prepare-fix',
    'self-audit',
    'release-readiness',
    'production-readiness',
]

SUITE_NATIVE_COMMANDS = {
    'contractify': ['consolidate', 'import', 'legacy-import'],
    'testify': [],
    'documentify': ['generate-track'],
    'docify': ['inline-explain'],
    'despaghettify': ['wave-plan'],
    'dockerify': ['stack-audit'],
    'postmanify': ['sync'],
    'templatify': ['list-templates', 'validate', 'render', 'check-drift'],
    'usabilify': ['inspect', 'evaluate', 'full'],
    'securify': ['scan', 'evaluate', 'autofix'],
    'observifyfy': ['inspect', 'audit', 'ai-pack', 'full'],
    'mvpify': ['inspect', 'plan', 'ai-pack', 'full'],
    'metrify': ['pricing', 'record', 'ingest', 'report', 'ai-pack', 'full'],
}

SUITE_SUMMARIES = {
    'contractify': 'Discovers, audits, explains, and consolidates contracts and projections.',
    'testify': 'Audits test governance and verifies ADR-to-test reflection, not just passing behavior.',
    'documentify': 'Builds and grows documentation tracks, including status and AI-readable exports.',
    'docify': 'Improves code documentation, docstrings, and dense inline explanations for Python code.',
    'despaghettify': 'Detects structural complexity and opens work for local spikes and broader cleanup.',
    'dockerify': 'Provides repo-serving Docker and compose governance when the target repository needs it.',
    'postmanify': 'Refreshes Postman surfaces from API evidence for repositories that use them.',
    'templatify': 'Owns and validates reusable templates for reports, docs, context packs, and suite outputs.',
    'usabilify': 'Surfaces human-usable status, UX guidance, and understandable next-step outputs.',
    'securify': 'Provides the security lane for scans, secret-risk review, and security-oriented guidance.',
    'observifyfy': 'Tracks internal fy-suite operations, internal docs roots, and non-contaminating cross-suite observability.',
    'mvpify': 'Imports prepared MVP bundles, mirrors their docs into the governed workspace, and orchestrates next-step implementation across suites.',
    'metrify': 'Measures AI usage, cost, model routing, and output volume across fy suites and summarizes the spending/utility picture.',
}


def _suite_dirs(workspace: Path) -> list[str]:
    names: list[str] = []
    for p in workspace.iterdir():
        if p.is_dir() and (p / 'adapter').is_dir():
            names.append(p.name)
    return sorted(set(names))


def suite_catalog_payload(root: Path | None = None) -> dict[str, Any]:
    workspace = workspace_root(root)
    suites = sorted({*CORE_SUITES, *OPTIONAL_SUITES, *_suite_dirs(workspace)})
    rows: list[dict[str, Any]] = []
    for suite in suites:
        suite_root = workspace / suite
        quality = evaluate_suite_quality(workspace, suite)
        readiness = suite_release_readiness(workspace, suite) if suite_root.exists() else None
        rows.append(
            {
                'suite': suite,
                'category': 'core' if suite in CORE_SUITES else 'optional',
                'summary': SUITE_SUMMARIES.get(suite, 'No catalog summary recorded yet.'),
                'has_adapter': (suite_root / 'adapter' / 'service.py').is_file(),
                'has_tools': (suite_root / 'tools').is_dir(),
                'has_docs': (suite_root / 'docs').is_dir() or (suite_root / 'README.md').is_file(),
                'has_templates': (suite_root / 'templates').is_dir(),
                'has_status': (suite_root / 'reports' / 'status' / 'most_recent_next_steps.json').is_file(),
                'lifecycle_commands': GENERIC_LIFECYCLE_COMMANDS,
                'native_commands': SUITE_NATIVE_COMMANDS.get(suite, []),
                'quality_ok': quality['ok'],
                'quality_missing': quality['missing'],
                'quality_warnings': quality['warnings'],
                'release_ready': bool(readiness and readiness.get('ready')),
                'latest_run_id': ((readiness or {}).get('latest_run') or {}).get('run_id'),
            }
        )
    return {
        'schema_version': 'fy.suite-catalog.v1',
        'generated_at': utc_now(),
        'suite_count': len(rows),
        'core_count': sum(1 for row in rows if row['category'] == 'core'),
        'optional_count': sum(1 for row in rows if row['category'] == 'optional'),
        'suites': rows,
    }


def render_suite_catalog_markdown(payload: dict[str, Any]) -> str:
    lines = [
        '# fy Suite Catalog',
        '',
        'This is the product-facing catalog of all suites currently present in the autark fy workspace.',
        '',
        f"- suite_count: `{payload.get('suite_count', 0)}`",
        f"- core_count: `{payload.get('core_count', 0)}`",
        f"- optional_count: `{payload.get('optional_count', 0)}`",
        '',
    ]
    for row in payload.get('suites', []):
        lines.extend([
            f"## {row['suite']}",
            '',
            f"- category: `{row['category']}`",
            f"- quality_ok: `{str(row['quality_ok']).lower()}`",
            f"- release_ready: `{str(row['release_ready']).lower()}`",
            f"- latest_run_id: `{row.get('latest_run_id') or 'none'}`",
            '',
            row['summary'],
            '',
            '### Lifecycle commands',
            '',
        ])
        for cmd in row.get('lifecycle_commands', []):
            lines.append(f'- `{cmd}`')
        if row.get('native_commands'):
            lines.extend(['', '### Native commands', ''])
            for cmd in row['native_commands']:
                lines.append(f'- `{cmd}`')
        if row.get('quality_missing'):
            lines.extend(['', '### Missing required surfaces', ''])
            for item in row['quality_missing']:
                lines.append(f'- `{item}`')
        if row.get('quality_warnings'):
            lines.extend(['', '### Warnings', ''])
            for item in row['quality_warnings']:
                lines.append(f'- `{item}`')
        lines.append('')
    return '\n'.join(lines).strip() + '\n'


def command_reference_payload(root: Path | None = None) -> dict[str, Any]:
    workspace = workspace_root(root)
    catalog = suite_catalog_payload(workspace)
    return {
        'schema_version': 'fy.command-reference.v1',
        'generated_at': utc_now(),
        'command_envelope_current': COMMAND_ENVELOPE_SCHEMA_VERSION,
        'command_envelope_compatibility': COMMAND_ENVELOPE_COMPATIBILITY,
        'manifest_compatibility': MANIFEST_COMPATIBILITY,
        'generic_lifecycle_commands': GENERIC_LIFECYCLE_COMMANDS,
        'suite_native_commands': {row['suite']: row['native_commands'] for row in catalog['suites']},
    }


def render_command_reference_markdown(payload: dict[str, Any]) -> str:
    lines = [
        '# fy Command Reference',
        '',
        'This page lists the stable shared lifecycle commands and the suite-specific native commands.',
        '',
        f"- command_envelope_current: `{payload['command_envelope_current']}`",
        f"- supported_read_versions: `{', '.join(payload['command_envelope_compatibility']['supported_read_versions'])}`",
        f"- supported_write_versions: `{', '.join(payload['command_envelope_compatibility']['supported_write_versions'])}`",
        '',
        '## Generic lifecycle commands',
        '',
    ]
    for cmd in payload.get('generic_lifecycle_commands', []):
        lines.append(f'- `{cmd}`')
    lines.extend(['', '## Suite-native commands', ''])
    for suite, commands in payload.get('suite_native_commands', {}).items():
        lines.append(f'### {suite}')
        lines.append('')
        if commands:
            for cmd in commands:
                lines.append(f'- `{cmd}`')
        else:
            lines.append('- no additional native commands')
        lines.append('')
    return '\n'.join(lines).strip() + '\n'


def _schema_for_object(name: str, fields: dict[str, Any], *, schema_version: str) -> dict[str, Any]:
    return {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'title': name,
        'type': 'object',
        'schema_version': schema_version,
        'properties': fields,
        'additionalProperties': True,
    }


def export_contract_schemas(root: Path | None = None) -> dict[str, Any]:
    workspace = workspace_root(root)
    out_dir = workspace / 'docs' / 'platform' / 'schemas'
    internal_out_dir = workspace / 'internal' / 'docs' / 'platform' / 'schemas'
    out_dir.mkdir(parents=True, exist_ok=True)
    internal_out_dir.mkdir(parents=True, exist_ok=True)
    files = {
        'command_envelope.schema.json': _schema_for_object(
            'CommandEnvelope',
            {
                'ok': {'type': 'boolean'},
                'suite': {'type': 'string'},
                'command': {'type': 'string'},
                'payload': {'type': 'object'},
                'warnings': {'type': 'array', 'items': {'type': 'string'}},
                'errors': {'type': 'array', 'items': {'type': 'string'}},
                'recovery_hints': {'type': 'array', 'items': {'type': 'string'}},
                'error_code': {'type': 'string'},
                'exit_code': {'type': 'integer'},
                'timestamp': {'type': 'string'},
                'schema_version': {'type': 'string'},
                'contract_version': {'type': 'string'},
                'compatibility_mode': {'type': 'string'},
            },
            schema_version='fy.command-envelope.schema.v1',
        ),
        'retrieval_hit.schema.json': _schema_for_object(
            'RetrievalHit',
            {
                'chunk_id': {'type': 'string'},
                'suite': {'type': 'string'},
                'score_lexical': {'type': 'number'},
                'score_semantic': {'type': 'number'},
                'score_hybrid': {'type': 'number'},
                'source_path': {'type': 'string'},
                'excerpt': {'type': 'string'},
                'scope': {'type': 'string'},
                'target_repo_id': {'type': ['string', 'null']},
                'score_recency': {'type': 'number'},
                'score_scope': {'type': 'number'},
                'score_suite_affinity': {'type': 'number'},
                'matched_terms': {'type': 'array', 'items': {'type': 'string'}},
                'confidence': {'type': 'string'},
                'rationale': {'type': 'string'},
            },
            schema_version='fy.retrieval-hit.schema.v1',
        ),
        'context_pack.schema.json': _schema_for_object(
            'ContextPack',
            {
                'pack_id': {'type': 'string'},
                'query': {'type': 'string'},
                'suite_scope': {'type': 'array', 'items': {'type': 'string'}},
                'audience': {'type': 'string'},
                'hits': {'type': 'array', 'items': {'type': 'object'}},
                'summary': {'type': 'string'},
                'artifact_paths': {'type': 'array', 'items': {'type': 'string'}},
                'related_suites': {'type': 'array', 'items': {'type': 'string'}},
                'evidence_confidence': {'type': 'string'},
                'priorities': {'type': 'array', 'items': {'type': 'string'}},
                'next_steps': {'type': 'array', 'items': {'type': 'string'}},
                'uncertainty': {'type': 'array', 'items': {'type': 'string'}},
            },
            schema_version='fy.context-pack.schema.v1',
        ),
        'model_route_decision.schema.json': _schema_for_object(
            'ModelRouteDecision',
            {
                'task_type': {'type': 'string'},
                'selected_tier': {'type': 'string'},
                'selected_model': {'type': 'string'},
                'reason': {'type': 'string'},
                'budget_class': {'type': 'string'},
                'fallback_chain': {'type': 'array', 'items': {'type': 'string'}},
                'reproducibility_mode': {'type': 'string'},
                'safety_mode': {'type': 'string'},
                'estimated_cost_class': {'type': 'string'},
            },
            schema_version='fy.model-route-decision.schema.v1',
        ),
        'compare_runs_delta.schema.json': _schema_for_object(
            'CompareRunsDelta',
            {
                'left_run_id': {'type': 'string'},
                'right_run_id': {'type': 'string'},
                'left_status': {'type': 'string'},
                'right_status': {'type': 'string'},
                'artifact_delta': {'type': 'integer'},
                'added_roles': {'type': 'array', 'items': {'type': 'string'}},
                'removed_roles': {'type': 'array', 'items': {'type': 'string'}},
                'left_artifact_count': {'type': 'integer'},
                'right_artifact_count': {'type': 'integer'},
                'left_evidence_count': {'type': 'integer'},
                'right_evidence_count': {'type': 'integer'},
                'left_review_state_counts': {'type': 'object'},
                'right_review_state_counts': {'type': 'object'},
                'left_journal_event_count': {'type': 'integer'},
                'right_journal_event_count': {'type': 'integer'},
                'left_duration_seconds': {'type': ['number', 'null']},
                'right_duration_seconds': {'type': ['number', 'null']},
                'mode_changed': {'type': 'boolean'},
                'target_repo_changed': {'type': 'boolean'},
                'target_repo_id_changed': {'type': 'boolean'},
                'added_formats': {'type': 'array', 'items': {'type': 'string'}},
                'removed_formats': {'type': 'array', 'items': {'type': 'string'}},
            },
            schema_version='fy.compare-runs-delta.schema.v1',
        ),
    }
    written = []
    for name, payload in files.items():
        path = out_dir / name
        write_json(path, payload)
        write_json(internal_out_dir / path.name, payload)
        written.append(str(path.relative_to(workspace)))
    return {
        'schema_version': 'fy.schema-export.v1',
        'generated_at': utc_now(),
        'schema_count': len(written),
        'written_paths': written,
    }


def doctor_payload(root: Path | None = None) -> dict[str, Any]:
    workspace = workspace_root(root)
    release = workspace_release_readiness(workspace)
    production = workspace_production_readiness(workspace)
    status = build_workspace_status_site(workspace)
    catalog = suite_catalog_payload(workspace)
    top: list[str] = []
    top.extend(production.get('top_next_steps', []))
    if release.get('core_blocked_suites'):
        top.append('Focus first on blocked core suites before starting optional suite work.')
    if status.get('blocked_suite_count', 0):
        top.append("Use the workspace status site to read each suite's most recent next steps in simple language.")
    if not top:
        top.append('The workspace looks healthy. Keep running self-audit, release-readiness, and production-readiness before outward release work.')
    return {
        'schema_version': 'fy.doctor.v1',
        'generated_at': utc_now(),
        'ok': bool(release['ok'] and production['ok']),
        'workspace_release': release,
        'workspace_production': production,
        'workspace_status': status,
        'catalog': catalog,
        'top_next_steps': top[:8],
    }


def render_doctor_markdown(payload: dict[str, Any]) -> str:
    lines = [
        '# fy Doctor',
        '',
        'This page is the top-level health view for the current workspace.',
        '',
        f"- ok: `{str(payload['ok']).lower()}`",
        f"- workspace_ready: `{str(payload['workspace_release']['ok']).lower()}`",
        f"- production_ready: `{str(payload['workspace_production']['ok']).lower()}`",
        f"- catalog_suites: `{payload['catalog']['suite_count']}`",
        '',
        '## Top Next Steps',
        '',
    ]
    for step in payload.get('top_next_steps', []):
        lines.append(f'- {step}')
    lines.extend(['', '## Core blocked suites', ''])
    blocked = payload['workspace_release'].get('core_blocked_suites', [])
    if blocked:
        for suite in blocked:
            lines.append(f'- `{suite}`')
    else:
        lines.append('- none')
    return '\n'.join(lines).strip() + '\n'


def final_release_bundle(root: Path | None = None) -> dict[str, Any]:
    workspace = workspace_root(root)
    catalog = suite_catalog_payload(workspace)
    command_reference = command_reference_payload(workspace)
    schemas = export_contract_schemas(workspace)
    doctor = doctor_payload(workspace)
    release = workspace_release_readiness(workspace)
    production = workspace_production_readiness(workspace)
    bundle = {
        'schema_version': 'fy.final-release-bundle.v1',
        'generated_at': utc_now(),
        'workspace_root': str(workspace),
        'catalog': catalog,
        'command_reference': command_reference,
        'schemas': schemas,
        'doctor': doctor,
        'workspace_release': release,
        'workspace_production': production,
    }
    docs_dir = workspace / 'docs' / 'platform'
    write_json(docs_dir / 'suite_catalog.json', catalog)
    write_text(docs_dir / 'SUITE_CATALOG.md', render_suite_catalog_markdown(catalog))
    write_json(docs_dir / 'command_reference.json', command_reference)
    write_text(docs_dir / 'SUITE_COMMAND_REFERENCE.md', render_command_reference_markdown(command_reference))
    write_json(docs_dir / 'doctor.json', doctor)
    write_text(docs_dir / 'DOCTOR.md', render_doctor_markdown(doctor))
    write_json(docs_dir / 'final_release_bundle.json', bundle)
    write_text(
        docs_dir / 'FINAL_RELEASE_BUNDLE.md',
        '\n'.join([
            '# fy Final Release Bundle',
            '',
            'This bundle captures the current suite catalog, command reference, schemas, doctor output, release readiness, and production readiness in one place.',
            '',
            f"- generated_at: `{bundle['generated_at']}`",
            f"- catalog_suites: `{catalog['suite_count']}`",
            f"- schemas_exported: `{schemas['schema_count']}`",
            f"- workspace_release_ok: `{str(release['ok']).lower()}`",
            f"- workspace_production_ok: `{str(production['ok']).lower()}`",
            '',
        ]),
    )
    return bundle



def ai_capability_payload(root: Path | None = None) -> dict[str, Any]:
    return {
        'schema_version': 'fy.ai-capability.v1',
        'generated_at': utc_now(),
        'shared': {
            'langgraph_ready': ['inspect_graph', 'audit_graph', 'context_pack_graph', 'triage_graph'],
            'langchain_ready': ['structured-output-compatible envelopes', 'tool-like suite commands', 'retrieval/context-pack surfaces'],
            'rag_ready': ['semantic_index', 'context_packs', 'cross_suite_intelligence'],
            'slm_llm_routing': ['model_router', 'decision_policy'],
        },
        'per_suite': {
            'contractify': ['decision_policy', 'import/legacy-import', 'consolidate', 'ADR reflection'],
            'testify': ['ADR reflection checks', 'cross-suite status use'],
            'documentify': ['template-aware generation', 'AI-readable tracks'],
            'docify': ['inline-explain guidance', 'public API doc checks'],
            'despaghettify': ['local spike surfacing'],
            'templatify': ['template inventory/validation/drift'],
            'usabilify': ['human-readable next steps'],
            'securify': ['security lane + secret-risk review'],
            'observifyfy': ['internal suite-memory and non-contaminating tracking'],
            'mvpify': ['prepared MVP import', 'doc mirroring', 'cross-suite orchestration'],
            'metrify': ['usage ledger', 'cost reporting', 'observify bridge', 'AI spend summaries'],
        },
        'aspirational': [
            'Swap graph recipe stubs for real LangGraph checkpointers and human-interrupt resume once external runtime dependencies are allowed.',
            'Bind model-router task classes to concrete LangChain model backends and provider-native structured output in production deployments.',
            'Promote semantic index scoring to stronger embedding/vector backends when cost/runtime policy permits.',
        ],
        'sources_of_truth': ['registry', 'journal', 'status pages', 'suite reports', 'docs/platform'],
    }


def render_ai_capability_markdown(payload: dict[str, Any]) -> str:
    lines = [
        '# AI Capability Matrix',
        '',
        'This report shows which AI/graph/retrieval mechanisms are already wired into the current fy workspace and which ones are still aspirational.',
        '',
    ]
    lines.extend(['## Shared mechanisms', ''])
    for key, value in payload.get('shared', {}).items():
        lines.append(f'- {key}: {", ".join(value)}')
    lines.extend(['', '## Per-suite mechanisms', ''])
    for suite, items in payload.get('per_suite', {}).items():
        lines.append(f'### {suite}')
        lines.append('')
        for item in items:
            lines.append(f'- {item}')
        lines.append('')
    lines.extend(['## Aspirational next upgrades', ''])
    for item in payload.get('aspirational', []):
        lines.append(f'- {item}')
    return "\n".join(lines).strip() + "\n"
