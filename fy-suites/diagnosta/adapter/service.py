from __future__ import annotations

from pathlib import Path
from typing import Any

from _suite_service_shared import _read_json, _write_md_summary
from fy_platform.ai.evidence_registry.registry import EvidenceRegistry
from fy_platform.ai.strategy_profiles import load_active_strategy_profile, strategy_runtime_metadata
from fy_platform.ai.workspace import target_repo_id, workspace_root, write_json


class DiagnostaAdapter:
    def __init__(self, root: Path | None = None) -> None:
        self.root = workspace_root(root)
        self.registry = EvidenceRegistry(self.root)

    def audit(self, target_repo_root: str | Path) -> dict[str, Any]:
        root = workspace_root(Path(target_repo_root))
        meta = strategy_runtime_metadata(root)
        profile = load_active_strategy_profile(root)
        contract = _read_json(root / 'contractify/reports/audit_latest.json')
        testify = _read_json(root / 'testify/reports/testify_audit.json')
        claims = _read_json(root / 'testify/generated/repo/testify-run/evolution_graph/claim_proof_status.json')
        despag = _read_json(root / 'despaghettify/reports/latest_check_with_metrics.json')
        docker = _read_json(root / 'dockerify/reports/dockerify_audit.json')
        docify = _read_json(root / 'docify/baseline_docstring_coverage.json')
        doc_manifest = _read_json(root / 'documentify/generated/repo/documentify-run/document_manifest.json')
        mvpify = _read_json(root / 'mvpify/reports/mvpify_import_inventory.json')

        blocker_items: list[dict[str, Any]] = []
        warning_items: list[dict[str, Any]] = []
        obligations: list[dict[str, Any]] = []
        evidence_sources: list[str] = []

        for item in contract.get('drift_findings', []) or []:
            blocker_id = item.get('id', 'blocker:contractify:drift')
            blocker_items.append({'id': blocker_id, 'suite': 'contractify', 'severity': item.get('severity', 'high'), 'summary': item.get('summary', 'Contract drift detected.')})
            evidence_sources.extend(item.get('evidence_sources', []) or [])
        for item in contract.get('conflicts', []) or []:
            obligations.append({'obligation_id': item.get('id', 'obligation:contractify:conflict'), 'suite': 'contractify', 'category': 'contract_review', 'severity': item.get('severity', 'medium'), 'summary': item.get('summary', 'Contract conflict requires review.'), 'source_paths': item.get('sources', []) or []})

        tf_findings = list(testify.get('findings', []) or [])
        tf_warnings = list(testify.get('warnings', []) or [])
        family_gap_count = int(claims.get('family_gap_count', 0) or 0)
        linked_claims = list(claims.get('linked_claims', []) or [])
        linked_claim_count = int(claims.get('linked_claim_count', len(linked_claims)) or len(linked_claims))
        if tf_findings:
            for item in tf_findings:
                blocker_items.append({'id': item.get('id', 'blocker:testify:finding'), 'suite': 'testify', 'severity': item.get('severity', 'high'), 'summary': item.get('summary', 'Test gap detected.')})
        else:
            if tf_warnings:
                warning_items.append({'id': 'warning:testify:proof-items', 'warning_id': 'warning:testify:proof-items', 'suite': 'testify', 'summary': tf_warnings[0]})
            if family_gap_count > 0:
                blocker_items.append({'id': 'blocker:testify:proof-family-gap', 'suite': 'testify', 'severity': 'high', 'summary': f'{family_gap_count} proof family gaps remain.'})
            elif linked_claim_count > 0:
                obligations.append({'obligation_id': 'obligation:testify:linked-claims', 'suite': 'testify', 'category': 'proof_review', 'severity': 'medium', 'summary': 'Linked claims remain part of the bounded proof surface.', 'source_paths': [row.get('workflow_path', '') for row in linked_claims if row.get('workflow_path')]})
                warning_items.append({'id': 'warning:testify:linked-claims-visible', 'warning_id': 'warning:testify:linked-claims-visible', 'suite': 'testify', 'summary': 'Linked claims stay visible in the bounded proof surface.'})

        ast = despag.get('ast', {}) if isinstance(despag, dict) else {}
        hotspot_entries = []
        hotspot_entries.extend(ast.get('top12_longest', []) or [])
        hotspot_entries.extend(ast.get('top6_nesting', []) or [])
        if ast.get('ai_turn_executor'):
            hotspot_entries.append(ast.get('ai_turn_executor'))
        if ast.get('global_category') == 'high' or tf_findings:
            for idx, entry in enumerate(hotspot_entries[:3], start=1):
                blocker_items.append({'id': f'blocker:despaghettify:hotspot:{idx}', 'suite': 'despaghettify', 'severity': 'medium', 'summary': entry.get('summary', 'Structural hotspot remains.'), 'path': entry.get('path', '')})
        elif ast.get('local_spike_count', 0):
            warning_items.append({'id': 'warning:despaghettify:local-spikes', 'warning_id': 'warning:despaghettify:local-spikes', 'suite': 'despaghettify', 'summary': f"{ast.get('local_spike_count', 0)} local hotspot signals remain visible."})

        docker_warnings = list(docker.get('warnings', []) or [])
        if docker_warnings:
            warning_items.append({'id': 'warning:dockerify:warnings', 'warning_id': 'warning:dockerify:warnings', 'suite': 'dockerify', 'summary': docker_warnings[0]})

        doc_summary = (docify.get('summary') or {}) if isinstance(docify, dict) else {}
        doc_findings = int(doc_summary.get('findings', len(docify.get('findings', []) or [])) or 0)
        if not docify:
            warning_items.append({'id': 'warning:readiness:optional-evidence-missing', 'warning_id': 'warning:readiness:optional-evidence-missing', 'suite': 'docify', 'summary': 'Optional documentation evidence is missing.'})
        elif doc_findings > 0:
            obligations.append({'obligation_id': 'obligation:docify:findings', 'suite': 'docify', 'category': 'documentation_review', 'severity': 'medium', 'summary': f'{doc_findings} documentation findings remain reviewable.', 'source_paths': ['docify/baseline_docstring_coverage.json']})

        if not doc_manifest:
            warning_items.append({'id': 'warning:readiness:optional-evidence-missing', 'warning_id': 'warning:readiness:optional-evidence-missing', 'suite': 'documentify', 'summary': 'Generated documentation manifest is missing.'})

        if not mvpify:
            warning_items.append({'id': 'warning:mvpify:inventory-missing', 'warning_id': 'warning:mvpify:inventory-missing', 'suite': 'mvpify', 'summary': 'MVP import inventory is missing.'})

        candidate_deep_count = 1 if not meta['candidate_e_active'] else 3
        deep_synthesis = {
            'schema_version': 'fy.deep-synthesis.v1',
            'active_profile': profile.active_profile,
            'planning_horizon': meta['planning_horizon'],
            'guarantee_gap_clusters': [
                {'cluster_id': f'gap-cluster-{i}', 'summary': f'Cluster {i} groups remaining proof and review items.'}
                for i in range(1, candidate_deep_count + 1)
            ],
            'next_wave_plan': [
                {'step_id': f'next-step-{i}', 'summary': f'Review and reduce bounded open burden step {i}.'}
                for i in range(1, candidate_deep_count + 1)
            ],
        }

        blocker_ids = [item['id'] for item in blocker_items]
        obligation_ids = [item['obligation_id'] for item in obligations]
        warning_ids = [item['id'] for item in warning_items]
        readiness_status = 'blocked' if blocker_ids else 'implementation_ready'
        if readiness_status == 'implementation_ready' and warning_ids and not obligation_ids:
            summary = 'Readiness is implementation-ready for the current bounded target, with warnings kept visible.'
        elif readiness_status == 'implementation_ready' and obligation_ids:
            summary = 'Readiness is implementation-ready for review-first closure assembly, with explicit obligations.'
        else:
            summary = 'Readiness is blocked by remaining blocker-class findings.'

        blocker_graph = {
            'schema_version': 'fy.blocker-graph.v1',
            'nodes': [{'id': item['id'], 'suite': item['suite'], 'severity': item.get('severity', 'medium'), 'summary': item['summary']} for item in blocker_items],
            'edges': [],
            'summary': 'Dependency view of blocker-class items.' if blocker_items else 'No blocker-class items remain for the current bounded target.',
        }
        blocker_priority_report = {
            'schema_version': 'fy.blocker-priority-report.v1',
            'blocker_count': len(blocker_items),
            'priorities': [{'id': item['id'], 'suite': item['suite'], 'severity': item.get('severity', 'medium'), 'summary': item['summary']} for item in blocker_items],
            'summary': 'Priority order for remaining blocker-class items.' if blocker_items else 'No prioritized blockers remain.',
        }
        obligation_matrix = {
            'schema_version': 'fy.obligation-matrix.v1',
            'rows': obligations,
            'summary': 'Current review obligations assembled from supporting suites.' if obligations else 'No open obligation rows remain.',
        }
        cannot_honestly_claim = {
            'schema_version': 'fy.cannot-honestly-claim.v1',
            'blocked_claims': ['global_closure'] if blocker_items else [],
            'summary': 'Blocked claims remain.' if blocker_items else 'No additional blocked claims beyond the bounded claim boundary.',
        }
        residue_ledger = {
            'schema_version': 'fy.residue-ledger.v1',
            'items': [],
            'summary': 'No residue items remain for the current bounded target.',
        }
        warning_ledger = {
            'schema_version': 'fy.warning-ledger.v1',
            'items': warning_items,
            'summary': 'Warnings remain visible and reviewable.' if warning_items else 'No warning-only items remain.',
        }
        sufficiency_verdict = {
            'schema_version': 'fy.sufficiency-verdict.v1',
            'verdict': 'bounded_sufficient' if not blocker_items else 'not_sufficient',
            'reason': summary,
            'supporting_artifact_paths': ['contractify/reports/audit_latest.json', 'testify/reports/testify_audit.json'],
        }
        handoff_packet = {
            'schema_version': 'fy.handoff-packet.v1',
            'depth': meta['handoff_depth'],
            'profile_execution_lane': meta['profile_execution_lane'],
            'planning_horizon': meta['planning_horizon'],
            'open_blocker_count': len(blocker_items),
            'open_obligation_count': len(obligations),
            'warning_count': len(warning_items),
        }
        readiness_case = {
            'schema_version': 'fy.readiness-case.v1',
            'target_id': f'workspace:{root.name}',
            'readiness_case_id': f'readiness:{root.name}',
            'target_kind': 'repository',
            'active_profile': profile.active_profile,
            'readiness_status': readiness_status,
            'summary': summary,
            'blocker_ids': blocker_ids,
            'obligation_ids': obligation_ids,
            'warning_ids': warning_ids,
            'residue_ids': [],
            'evidence_sources': sorted(set(evidence_sources + ['contractify/reports/audit_latest.json', 'testify/reports/testify_audit.json'])),
        }

        reports = root / 'diagnosta' / 'reports'
        reports.mkdir(parents=True, exist_ok=True)
        write_json(reports / 'latest_readiness_case.json', readiness_case)
        write_json(reports / 'latest_blocker_graph.json', blocker_graph)
        write_json(reports / 'latest_blocker_priority_report.json', blocker_priority_report)
        write_json(reports / 'latest_obligation_matrix.json', obligation_matrix)
        write_json(reports / 'latest_cannot_honestly_claim.json', cannot_honestly_claim)
        write_json(reports / 'latest_residue_ledger.json', residue_ledger)
        write_json(reports / 'latest_warning_ledger.json', warning_ledger)
        write_json(reports / 'latest_sufficiency_verdict.json', sufficiency_verdict)
        write_json(reports / 'latest_deep_synthesis.json', deep_synthesis)
        write_json(reports / 'latest_handoff_packet.json', handoff_packet)
        _write_md_summary(reports / 'latest_readiness_case.md', 'Diagnosta Readiness Case', [f"- readiness_status: `{readiness_status}`", f"- active_profile: `{profile.active_profile}`", f"- blocker_count: `{len(blocker_items)}`", f"- obligation_count: `{len(obligations)}`", f"- warning_count: `{len(warning_items)}`"])

        run = self.registry.start_run(suite='diagnosta', mode='audit', target_repo_root=str(root), target_repo_id=target_repo_id(root), strategy_profile=profile.active_profile, run_metadata={'profile_execution_lane': meta['profile_execution_lane'], 'planning_horizon': meta['planning_horizon'], 'handoff_depth': meta['handoff_depth']})
        for path in [
            'diagnosta/reports/latest_readiness_case.json', 'diagnosta/reports/latest_blocker_graph.json', 'diagnosta/reports/latest_blocker_priority_report.json',
            'diagnosta/reports/latest_obligation_matrix.json', 'diagnosta/reports/latest_cannot_honestly_claim.json', 'diagnosta/reports/latest_residue_ledger.json',
            'diagnosta/reports/latest_warning_ledger.json', 'diagnosta/reports/latest_sufficiency_verdict.json', 'diagnosta/reports/latest_deep_synthesis.json', 'diagnosta/reports/latest_handoff_packet.json'
        ]:
            self.registry.record_artifact(suite='diagnosta', run_id=run.run_id, format='json' if path.endswith('.json') else 'markdown', role='report', path=path)
        self.registry.finish_run(run.run_id, status='ok')
        status_payload = {'ok': True, 'summary': summary, 'next_steps': [step['summary'] for step in deep_synthesis['next_wave_plan']], 'command': 'audit', 'latest_run': {'run_id': run.run_id}}
        write_json(root / 'diagnosta/reports/status/most_recent_next_steps.json', status_payload)
        return {
            'ok': True,
            'run_id': run.run_id,
            'active_strategy_profile': {
                'active_profile': profile.active_profile,
                'profile_execution_lane': meta['profile_execution_lane'],
                'profile_behavior_depth': meta['profile_behavior_depth'],
            },
            'readiness_case': readiness_case,
            'blocker_graph': blocker_graph,
            'blocker_priority_report': blocker_priority_report,
            'obligation_matrix': obligation_matrix,
            'cannot_honestly_claim': cannot_honestly_claim,
            'residue_ledger': residue_ledger,
            'warning_ledger': warning_ledger,
            'sufficiency_verdict': sufficiency_verdict,
            'deep_synthesis': deep_synthesis,
            'handoff_packet': handoff_packet,
        }

    def compare_runs(self, earlier_run_id: str, later_run_id: str) -> dict[str, Any]:
        earlier = self.registry.get_run(earlier_run_id) or {}
        later = self.registry.get_run(later_run_id) or {}
        earlier_meta = earlier.get('run_metadata', {})
        later_meta = later.get('run_metadata', {})
        return {
            'ok': True,
            'earlier_run_id': earlier_run_id,
            'later_run_id': later_run_id,
            'profile_depth_delta': {
                'active_profile_changed': earlier.get('strategy_profile') != later.get('strategy_profile'),
                'planning_horizon_delta': int(later_meta.get('planning_horizon', 0)) - int(earlier_meta.get('planning_horizon', 0)),
            },
            'handoff_depth_delta': {
                'depth_changed': earlier_meta.get('handoff_depth') != later_meta.get('handoff_depth'),
                'from': earlier_meta.get('handoff_depth'),
                'to': later_meta.get('handoff_depth'),
            },
        }
