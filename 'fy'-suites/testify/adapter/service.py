from __future__ import annotations

from pathlib import Path
from typing import Any

from fy_platform.ai.adr_reflection import compute_reflection_status, discover_consolidated_adrs
from fy_platform.ai.base_adapter import BaseSuiteAdapter
from testify.tools.test_governance import audit_test_governance, render_markdown


class TestifyAdapter(BaseSuiteAdapter):
    __test__ = False

    def __init__(self, root: Path | None = None) -> None:
        super().__init__('testify', root)

    def _latest_contractify_consolidation(self, target_repo_id: str) -> dict[str, Any] | None:
        for run in self.registry.list_runs('contractify'):
            if run.get('mode') != 'consolidate':
                continue
            if run.get('target_repo_id') != target_repo_id:
                continue
            artifacts = self.registry.artifacts_for_run(run['run_id'])
            for artifact in artifacts:
                if artifact.get('role') == 'contractify_consolidate_json':
                    payload = self.registry.artifact_payload(artifact['artifact_id'])
                    if isinstance(payload, dict):
                        return payload
        return None

    def audit(self, target_repo_root: str) -> dict:
        target = Path(target_repo_root).resolve()
        run_id, run_dir, tgt_id = self._start_run('audit', target)
        try:
            try:
                payload = audit_test_governance(target)
            except Exception as exc:
                checks = []
                checks.append({'name': 'tests_run_script', 'ok': (target / 'tests' / 'run_tests.py').is_file()})
                checks.append({'name': 'github_workflow', 'ok': any((target / '.github' / 'workflows').glob('*.y*ml')) if (target / '.github' / 'workflows').is_dir() else False})
                payload = {'fallback_note': f'testify fallback used: {exc}', 'checks': checks, 'findings': [c for c in checks if not c['ok']]}
            latest_contractify = self._latest_contractify_consolidation(tgt_id)
            consolidated_adrs = latest_contractify.get('consolidated_adrs', []) if latest_contractify else discover_consolidated_adrs(target)
            reflection = compute_reflection_status(target, consolidated_adrs)
            payload['adr_reflection'] = reflection
            payload['contractify_consolidation_available'] = bool(latest_contractify)
            payload.setdefault('findings', [])
            payload.setdefault('warnings', [])
            if reflection['consolidated_adr_count'] and not reflection['alignment_test_present']:
                payload['findings'].append({
                    'id': 'TESTIFY-ADR-CONSOLIDATION-ALIGNMENT-TEST-MISSING',
                    'severity': 'high',
                    'summary': 'Consolidated ADRs exist, but tests/test_adr_consolidation_alignment.py is missing.',
                })
            if reflection['unmapped_adr_ids']:
                payload['findings'].append({
                    'id': 'TESTIFY-ADR-TEST-REFLECTION-GAP',
                    'severity': 'high',
                    'summary': 'Consolidated ADRs are not mirrored in explicit test mappings: ' + ', '.join(reflection['unmapped_adr_ids']),
                })
            if reflection['weakly_mapped_adr_ids']:
                payload['warnings'].append('Weak ADR reflection detected for: ' + ', '.join(reflection['weakly_mapped_adr_ids']))
            md = render_markdown(payload)
            if reflection['consolidated_adr_count']:
                md += '\n## ADR reflection\n\n'
                md += f"- consolidated ADR count: `{reflection['consolidated_adr_count']}`\n"
                md += f"- alignment test present: `{reflection['alignment_test_present']}`\n"
                md += f"- mirrored ADR ids: `{reflection['mirrored_adr_ids']}`\n"
                md += f"- weakly mapped ADR ids: `{reflection['weakly_mapped_adr_ids']}`\n"
                md += f"- unmapped ADR ids: `{reflection['unmapped_adr_ids']}`\n"
            paths = self._write_payload_bundle(run_id=run_id, run_dir=run_dir, payload=payload, summary_md=md, role_prefix='testify_audit')
            failures = len(payload.get('findings', [])) if isinstance(payload, dict) else 0
            self._finish_run(run_id, 'ok', {'finding_count': failures, 'target_repo_id': tgt_id, 'consolidated_adr_count': reflection['consolidated_adr_count']})
            return {
                'ok': True,
                'suite': self.suite,
                'run_id': run_id,
                'finding_count': failures,
                'adr_reflection': reflection,
                **paths,
            }
        except Exception as exc:
            self._finish_run(run_id, 'failed', {'error': str(exc)})
            return {'ok': False, 'suite': self.suite, 'run_id': run_id, 'error': str(exc)}

    def prepare_fix(self, finding_ids: list[str]) -> dict:
        out = super().prepare_fix(finding_ids)
        out['suggested_actions'] = [
            'align tests/run_tests.py with workflow entries',
            'ensure CI workflow covers required suite targets',
            'mirror consolidated ADRs in explicit ADR alignment tests and mappings',
            'refresh testify audit after changes',
        ]
        return out
