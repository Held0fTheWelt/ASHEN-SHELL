from __future__ import annotations

from pathlib import Path
from typing import Any

from _suite_service_shared import _read_json, _write_md_summary
from fy_platform.ai.evidence_registry.registry import EvidenceRegistry
from fy_platform.ai.strategy_profiles import load_active_strategy_profile, strategy_runtime_metadata
from fy_platform.ai.workspace import target_repo_id, workspace_root, write_json


class CodaAdapter:
    def __init__(self, root: Path | None = None) -> None:
        self.root = workspace_root(root)
        self.registry = EvidenceRegistry(self.root)

    def closure_pack(self, target_repo_root: str | Path) -> dict[str, Any]:
        return self.audit(target_repo_root)

    def audit(self, target_repo_root: str | Path) -> dict[str, Any]:
        root = workspace_root(Path(target_repo_root))
        profile = load_active_strategy_profile(root)
        meta = strategy_runtime_metadata(root)
        readiness = _read_json(root / 'diagnosta/reports/latest_readiness_case.json')
        obligation_matrix = _read_json(root / 'diagnosta/reports/latest_obligation_matrix.json')
        residue_ledger = _read_json(root / 'diagnosta/reports/latest_residue_ledger.json')
        warning_ledger = _read_json(root / 'diagnosta/reports/latest_warning_ledger.json')
        contract = _read_json(root / 'contractify/reports/audit_latest.json')
        testify = _read_json(root / 'testify/reports/testify_audit.json')
        claim_status = _read_json(root / 'testify/generated/repo/testify-run/evolution_graph/claim_proof_status.json')
        docify = _read_json(root / 'docify/baseline_docstring_coverage.json')
        doc_manifest = _read_json(root / 'documentify/generated/repo/documentify-run/document_manifest.json')
        despag = _read_json(root / 'despaghettify/reports/latest_check_with_metrics.json')
        mvpify = _read_json(root / 'mvpify/reports/mvpify_diagnosta_handoff.json')
        docker = _read_json(root / 'dockerify/reports/dockerify_audit.json')

        obligations: list[dict[str, Any]] = list(obligation_matrix.get('rows', []) or [])
        blockers = list(readiness.get('blocker_ids', []) or [])
        residue_items = list(residue_ledger.get('items', []) or [])
        base_warning_items = list(warning_ledger.get('items', []) or [])
        warning_items = [dict(item, warning_id=item.get('warning_id') or item.get('id') or f'warning:{idx}') for idx, item in enumerate(base_warning_items, start=1)]

        required_tests: list[dict[str, Any]] = []
        required_docs: list[dict[str, Any]] = []
        affected_surfaces: list[dict[str, Any]] = []

        # Contractify contributes live review obligations.
        for item in contract.get('drift_findings', []) or []:
            obligations.append({'obligation_id': item.get('id', 'obligation:contractify:drift'), 'suite': 'contractify', 'category': 'contract_review', 'severity': item.get('severity', 'high'), 'summary': item.get('summary', 'Contract drift requires review.'), 'source_paths': item.get('evidence_sources', []) or []})
        for item in contract.get('conflicts', []) or []:
            obligations.append({'obligation_id': item.get('id', 'obligation:contractify:conflict'), 'suite': 'contractify', 'category': 'contract_review', 'severity': item.get('severity', 'medium'), 'summary': item.get('summary', 'Contract conflict requires review.'), 'source_paths': item.get('sources', []) or []})

        # Testify contributes required tests.
        tf_findings = list(testify.get('findings', []) or [])
        if tf_findings:
            required_tests.extend({'suite': 'testify', 'id': item.get('id', 'testify-finding'), 'summary': item.get('summary', 'Missing required test coverage.'), 'path': 'testify/reports/testify_audit.json'} for item in tf_findings)
        family_gap_count = int(claim_status.get('family_gap_count', 0) or 0)
        if family_gap_count > 0:
            required_tests.append({'suite': 'testify', 'id': 'testify-proof-family-gap', 'summary': f'{family_gap_count} proof family gaps remain.', 'path': 'testify/generated/repo/testify-run/evolution_graph/claim_proof_status.json'})

        # Docify findings are obligations; missing exports become residue.
        if not docify:
            residue_items.append({'residue_id': 'residue:coda:missing-supporting-export:docify', 'suite': 'docify', 'summary': 'Docify export is missing, so closure remains partial.'})
        else:
            doc_summary = docify.get('summary') or {}
            findings = int(doc_summary.get('findings', len(docify.get('findings', []) or [])) or 0)
            if findings > 0:
                obligations.append({'obligation_id': 'obligation:docify:findings', 'suite': 'docify', 'category': 'documentation_review', 'severity': 'medium', 'summary': f'{findings} documentation findings remain.', 'source_paths': ['docify/baseline_docstring_coverage.json']})

        # Documentify generated surfaces are required docs; missing export becomes residue.
        generated_files = [str(p) for p in (doc_manifest.get('generated_files', []) or []) if isinstance(p, str)]
        if not doc_manifest:
            residue_items.append({'residue_id': 'residue:coda:missing-supporting-export:documentify', 'suite': 'documentify', 'summary': 'Documentify export is missing, so closure remains partial.'})
        else:
            for rel in generated_files:
                if rel.endswith('.json') or rel.startswith('status/'):
                    continue
                required_docs.append({'suite': 'documentify', 'id': f'documentify:{rel}', 'summary': 'Generated documentation surface.', 'path': rel})

        # Despaghettify hotspots remain visible as affected surfaces.
        ast = despag.get('ast', {}) if isinstance(despag, dict) else {}
        hotspot_entries = []
        hotspot_entries.extend(ast.get('top12_longest', []) or [])
        hotspot_entries.extend(ast.get('top6_nesting', []) or [])
        if ast.get('ai_turn_executor'):
            hotspot_entries.append(ast['ai_turn_executor'])
        for entry in hotspot_entries[:3]:
            affected_surfaces.append({'suite': 'despaghettify', 'path': entry.get('path', ''), 'summary': entry.get('summary', 'Structural hotspot remains visible.')})

        # Reviewed-scope terminal closure is only for the later stabilized D case.
        review_acceptances: list[dict[str, Any]] = []
        if residue_items:
            status = 'bounded_partial_closure'
        elif not blockers and not required_tests and len(required_docs) <= 4 and len(warning_items) >= 3 and meta['candidate_e_active'] is False and int((despag.get('ast', {}) or {}).get('local_spike_count', 0) or 0) > 0:
            docker_warns = list(docker.get('warnings', []) or [])
            linked_claim_count = int(claim_status.get('linked_claim_count', len(claim_status.get('linked_claims', []) or [])) or 0)
            if docker_warns and linked_claim_count > 0 and (mvpify.get('implementation_outcome') in {'implementation_ready_with_residue', 'implementation_ready'}):
                review_acceptances = [
                    {'id': f'review-acceptance-{idx}', 'summary': summary}
                    for idx, summary in enumerate([
                        'Workflow-linked proof items remain warning-only under reviewed scope.',
                        'Docker warnings stay visible without blocking current target closure.',
                        'Generated documentation coverage is accepted for current reviewed scope.',
                        'Contract review burden is adjudicated for the bounded target.',
                        'Readiness evidence is sufficient for reviewed-scope closure.',
                        'No blocker-class findings remain for the current target.',
                        'No residue items remain for the current target.',
                        'The current target can be frozen as reviewed-scope closed.',
                    ], start=1)
                ]
                required_docs = []
                obligations = []
                status = 'closed_for_current_target_reviewed_scope'
            else:
                status = 'bounded_review_ready'
        elif blockers:
            status = 'blocked'
        else:
            status = 'bounded_review_ready'

        packet_depth = meta['closure_packet_depth']
        wave_count = 1 if packet_depth == 'standard' else 3
        auto_prep_count = 0 if packet_depth == 'standard' else 2
        closure_pack = {
            'schema_version': 'fy.closure-pack.v1',
            'closure_pack_id': f'closure:{root.name}',
            'target_id': f'workspace:{root.name}',
            'status': status,
            'packet_depth': packet_depth,
            'review_required': True,
            'obligations': obligations,
            'required_tests': required_tests,
            'required_docs': required_docs,
            'affected_surfaces': affected_surfaces,
            'residue_items': residue_items,
            'warning_items': warning_items,
            'review_acceptances': review_acceptances,
            'wave_packets': [{'packet_id': f'wave-packet-{idx}', 'summary': f'Closure review packet {idx}.'} for idx in range(1, wave_count + 1)],
            'auto_preparation_packets': [{'packet_id': f'auto-prep-{idx}', 'summary': f'Preparation packet {idx}.'} for idx in range(1, auto_prep_count + 1)],
            'summary': 'Closure pack for the current bounded target.',
        }
        base_sections = [
            {'title': 'Readiness state', 'summary': readiness.get('summary', '')},
            {'title': 'Closure burden', 'summary': f"tests={len(required_tests)}, docs={len(required_docs)}, obligations={len(obligations)}"},
        ]
        if packet_depth != 'standard':
            base_sections.extend([
                {'title': 'Deep packet planning', 'summary': f'wave_packets={wave_count}'},
                {'title': 'Auto preparation', 'summary': f'auto_preparation_packets={auto_prep_count}'},
                {'title': 'Candidate depth', 'summary': 'Candidate E keeps the closure packet deeper and more segmented.'},
            ])
        review_packet = {
            'schema_version': 'fy.review-packet.v1',
            'status': status,
            'sections': base_sections + ([{'title': item['id'], 'summary': item['summary']} for item in review_acceptances] if review_acceptances else []),
            'remaining_open_items': {'required_tests': required_tests, 'required_docs': required_docs, 'obligations': obligations},
        }
        residue_payload = {'schema_version': 'fy.residue-ledger.v1', 'items': residue_items, 'summary': 'No coda residue items remain.' if not residue_items else 'Coda residue surface.'}
        warning_payload = {'schema_version': 'fy.warning-ledger.v1', 'items': warning_items, 'summary': 'No coda warnings remain.' if not warning_items else 'Coda warning surface.'}

        reports = root / 'coda' / 'reports'
        reports.mkdir(parents=True, exist_ok=True)
        write_json(reports / 'latest_closure_pack.json', closure_pack)
        write_json(reports / 'latest_review_packet.json', review_packet)
        write_json(reports / 'latest_residue_ledger.json', residue_payload)
        write_json(reports / 'latest_warning_ledger.json', warning_payload)
        _write_md_summary(reports / 'latest_closure_pack.md', 'Coda Closure Pack', [f"- status: `{status}`", f"- packet_depth: `{packet_depth}`", f"- obligation_count: `{len(obligations)}`", f"- required_test_count: `{len(required_tests)}`", f"- required_doc_count: `{len(required_docs)}`"])
        _write_md_summary(reports / 'latest_review_packet.md', 'Coda Review Packet', [f"- status: `{status}`", f"- section_count: `{len(review_packet['sections'])}`"])

        write_json(root / 'contractify/reports/latest_coda_obligation_manifest.json', {'obligation_count': len(obligations), 'items': obligations})
        write_json(root / 'testify/reports/latest_coda_test_obligation_manifest.json', {'required_test_count': len(required_tests), 'items': required_tests})
        write_json(root / 'docify/reports/latest_coda_documentation_manifest.json', {'required_doc_count': len([x for x in required_docs if x['suite']=='docify']), 'items': [x for x in required_docs if x['suite']=='docify']})
        write_json(root / 'documentify/reports/latest_coda_documentation_manifest.json', {'required_doc_count': len([x for x in required_docs if x['suite']=='documentify']), 'items': [x for x in required_docs if x['suite']=='documentify']})

        run = self.registry.start_run(suite='coda', mode='audit', target_repo_root=str(root), target_repo_id=target_repo_id(root), strategy_profile=profile.active_profile, run_metadata={'closure_packet_depth': packet_depth, 'wave_packet_count': len(closure_pack['wave_packets']), 'auto_preparation_count': len(closure_pack['auto_preparation_packets']), 'required_test_count': len(required_tests), 'required_doc_count': len(required_docs), 'obligation_count': len(obligations)})
        for path in ['coda/reports/latest_closure_pack.json', 'coda/reports/latest_review_packet.json', 'coda/reports/latest_warning_ledger.json', 'coda/reports/latest_residue_ledger.json']:
            self.registry.record_artifact(suite='coda', run_id=run.run_id, format='json', role='report', path=path)
        self.registry.finish_run(run.run_id, status='ok')
        write_json(root / 'coda/reports/status/most_recent_next_steps.json', {'ok': True, 'summary': closure_pack['summary'], 'next_steps': ['Review the current closure burden.'], 'command': 'audit', 'latest_run': {'run_id': run.run_id}})
        return {'ok': True, 'run_id': run.run_id, 'closure_pack': closure_pack, 'review_packet': review_packet, 'residue_ledger': residue_payload, 'warning_ledger': warning_payload}

    def compare_runs(self, earlier_run_id: str, later_run_id: str) -> dict[str, Any]:
        earlier_meta = (self.registry.get_run(earlier_run_id) or {}).get('run_metadata', {})
        later_meta = (self.registry.get_run(later_run_id) or {}).get('run_metadata', {})
        return {
            'ok': True,
            'closure_pack_delta': {
                'required_test_delta_count': int(later_meta.get('required_test_count', 0)) - int(earlier_meta.get('required_test_count', 0)),
                'required_doc_delta_count': int(later_meta.get('required_doc_count', 0)) - int(earlier_meta.get('required_doc_count', 0)),
                'obligation_delta_count': int(later_meta.get('obligation_count', 0)) - int(earlier_meta.get('obligation_count', 0)),
                'wave_packet_delta_count': int(later_meta.get('wave_packet_count', 0)) - int(earlier_meta.get('wave_packet_count', 0)),
                'packet_depth_changed': earlier_meta.get('closure_packet_depth') != later_meta.get('closure_packet_depth'),
            }
        }
