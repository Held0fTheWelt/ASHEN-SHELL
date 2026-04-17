from __future__ import annotations

from pathlib import Path
from typing import Any

from contractify.tools.audit_pipeline import build_discover_payload, run_audit
from fy_platform.ai.adr_reflection import (
    discover_consolidated_adrs,
    find_candidate_test_matches,
    parse_instruction_mapping,
    render_alignment_test_module,
    render_contract_matrix_module,
)
from fy_platform.ai.base_adapter import BaseSuiteAdapter
from fy_platform.ai.workspace import write_text


class ContractifyAdapter(BaseSuiteAdapter):
    __test__ = False

    def __init__(self, root: Path | None = None) -> None:
        super().__init__('contractify', root)

    def audit(self, target_repo_root: str) -> dict:
        target = Path(target_repo_root).resolve()
        run_id, run_dir, tgt_id = self._start_run('audit', target)
        try:
            try:
                payload = run_audit(target, max_contracts=30)
            except Exception as exc:
                payload = {
                    'stats': {'contracts': 0, 'drift_findings': 0, 'conflicts': 0},
                    'drift_findings': [],
                    'conflicts': [],
                    'fallback_note': f'contractify fallback summary used: {exc}',
                    'discovery_preview': build_discover_payload(target, max_contracts=30) if target.exists() else {},
                }
            findings = len(payload.get('drift_findings', [])) + len(payload.get('conflicts', []))
            md = '# Contractify Audit\n\n' + f'- target: `{target}`\n- findings: {findings}\n'
            paths = self._write_payload_bundle(run_id=run_id, run_dir=run_dir, payload=payload, summary_md=md, role_prefix='contractify_audit')
            self._finish_run(run_id, 'ok', {'finding_count': findings, 'target_repo_id': tgt_id})
            return {'ok': True, 'suite': self.suite, 'run_id': run_id, 'finding_count': findings, **paths}
        except Exception as exc:
            self._finish_run(run_id, 'failed', {'error': str(exc)})
            return {'ok': False, 'suite': self.suite, 'run_id': run_id, 'error': str(exc)}

    def _build_consolidation_plan(self, target: Path, audit_payload: dict[str, Any], instruction: str | None) -> dict[str, Any]:
        instruction_map = parse_instruction_mapping(instruction)
        consolidated_adrs = discover_consolidated_adrs(target)
        entries: list[dict[str, Any]] = []
        user_questions: list[str] = []
        auto_actions: list[str] = []
        unresolved: list[str] = []
        for adr in consolidated_adrs:
            candidates = find_candidate_test_matches(target, adr)
            required_paths = [item['path'] for item in candidates[:2]]
            if adr['adr_id'] in instruction_map:
                required_paths = instruction_map[adr['adr_id']]
            if not required_paths:
                unresolved.append(adr['adr_id'])
                user_questions.append(
                    f"Provide explicit test path mappings for {adr['adr_id']} using --instruction 'ADR-xxxx=tests/test_file.py[,tests/test_other.py]'"
                )
            entries.append({
                'adr_id': adr['adr_id'],
                'title': adr['title'],
                'source_path': adr['path'],
                'keywords': adr['keywords'],
                'candidate_test_matches': candidates,
                'required_test_paths': required_paths,
            })
        if entries:
            auto_actions.extend([
                'write tests/adr_contract_matrix.py',
                'write tests/test_adr_consolidation_alignment.py',
            ])
        plan = {
            'consolidated_adrs': entries,
            'stats': {
                'consolidated_adr_count': len(entries),
                'drift_count': len(audit_payload.get('drift_findings', [])),
                'conflict_count': len(audit_payload.get('conflicts', [])),
                'unresolved_adr_count': len(unresolved),
            },
            'unresolved_adr_ids': unresolved,
            'requires_user_input': bool(unresolved),
            'user_questions': user_questions,
            'auto_actions': auto_actions,
            'instruction_used': instruction or '',
            'can_apply_safe': bool(entries) and not unresolved,
            'advisory_note': 'Contractify may safely apply generated ADR/test reflection scaffolding only when every consolidated ADR resolves to at least one explicit test path.',
        }
        return plan

    def consolidate(self, target_repo_root: str, *, apply_safe: bool = False, instruction: str | None = None) -> dict[str, Any]:
        target = Path(target_repo_root).resolve()
        run_id, run_dir, tgt_id = self._start_run('consolidate', target)
        generated_dir = self.hub_dir / 'generated' / 'consolidations' / tgt_id / run_id
        generated_dir.mkdir(parents=True, exist_ok=True)
        try:
            try:
                audit_payload = run_audit(target, max_contracts=30)
            except Exception as exc:
                audit_payload = {
                    'drift_findings': [],
                    'conflicts': [],
                    'fallback_note': f'contractify consolidate fallback audit used: {exc}',
                }
            plan = self._build_consolidation_plan(target, audit_payload, instruction)
            applied_actions: list[str] = []
            matrix_rel = 'tests/adr_contract_matrix.py'
            alignment_rel = 'tests/test_adr_consolidation_alignment.py'
            if apply_safe and plan['can_apply_safe']:
                write_text(target / matrix_rel, render_contract_matrix_module(plan['consolidated_adrs']))
                write_text(target / alignment_rel, render_alignment_test_module())
                applied_actions.extend([matrix_rel, alignment_rel])
            elif apply_safe and not plan['can_apply_safe']:
                plan['apply_safe_blocked'] = True
            plan['applied_actions'] = applied_actions
            plan['target_repo_root'] = str(target)
            plan['target_repo_id'] = tgt_id
            plan['generated_preview_dir'] = str(generated_dir.relative_to(self.root))

            md_lines = [
                '# Contractify Consolidate',
                '',
                f'- target: `{target}`',
                f"- consolidated ADRs: {plan['stats']['consolidated_adr_count']}",
                f"- unresolved ADRs: {plan['stats']['unresolved_adr_count']}",
                f"- can_apply_safe: {plan['can_apply_safe']}",
                f"- applied_actions: {len(applied_actions)}",
                '',
            ]
            for entry in plan['consolidated_adrs']:
                md_lines.append(f"- {entry['adr_id']}: {entry['title']} -> {entry['required_test_paths'] or 'USER INPUT REQUIRED'}")
            if plan['user_questions']:
                md_lines.extend(['', '## User input required', ''])
                md_lines.extend(f'- {q}' for q in plan['user_questions'])
            md_text = '\n'.join(md_lines) + '\n'
            write_text(generated_dir / 'contractify_consolidation_plan.md', md_text)
            write_text(
                generated_dir / 'contractify_consolidation_matrix_preview.py',
                render_contract_matrix_module(plan['consolidated_adrs']) if plan['consolidated_adrs'] else 'ADR_TEST_MATRIX = {}\n',
            )
            paths = self._write_payload_bundle(run_id=run_id, run_dir=run_dir, payload=plan, summary_md=md_text, role_prefix='contractify_consolidate')
            self._finish_run(
                run_id,
                'ok',
                {
                    'consolidated_adr_count': plan['stats']['consolidated_adr_count'],
                    'unresolved_adr_count': plan['stats']['unresolved_adr_count'],
                    'applied_action_count': len(applied_actions),
                    'target_repo_id': tgt_id,
                },
            )
            return {
                'ok': True,
                'suite': self.suite,
                'run_id': run_id,
                'consolidated_adr_count': plan['stats']['consolidated_adr_count'],
                'requires_user_input': plan['requires_user_input'],
                'can_apply_safe': plan['can_apply_safe'],
                'applied_actions': applied_actions,
                'user_questions': plan['user_questions'],
                **paths,
            }
        except Exception as exc:
            self._finish_run(run_id, 'failed', {'error': str(exc)})
            return {'ok': False, 'suite': self.suite, 'run_id': run_id, 'error': str(exc)}

    def triage(self, query: str | None = None) -> dict:
        base = super().triage(query)
        latest = self.registry.latest_run(self.suite)
        if latest:
            artifacts = self.registry.artifacts_for_run(latest['run_id'])
            base['latest_artifact_count'] = len(artifacts)
        return base

    def prepare_fix(self, finding_ids: list[str]) -> dict:
        out = super().prepare_fix(finding_ids)
        out['suggested_actions'] = [
            're-anchor affected contracts to a single owner vocabulary',
            'refresh projection/back-reference links',
            'run contractify consolidate to generate ADR/test reflection scaffolding',
            'regenerate audit and compare against accepted run',
        ]
        return out
