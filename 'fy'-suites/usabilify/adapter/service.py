from __future__ import annotations

from pathlib import Path

from fy_platform.ai.base_adapter import BaseSuiteAdapter
from usabilify.tools.contract_bridge import scan_contracts
from usabilify.tools.evaluator import evaluate, evaluation_markdown, inventory_markdown, view_map
from usabilify.tools.template_inventory import inspect_areas


class UsabilifyAdapter(BaseSuiteAdapter):
    __test__ = False

    def __init__(self, root: Path | None = None) -> None:
        super().__init__('usabilify', root)

    def audit(self, target_repo_root: str) -> dict:
        target = Path(target_repo_root).resolve()
        run_id, run_dir, tgt_id = self._start_run('audit', target)
        try:
            inventory = inspect_areas(target)
            evaluation = evaluate(target)
            contracts = scan_contracts(target)
            mermaid = view_map(evaluation)
            mermaid_path = run_dir / 'usabilify_view_map.mmd'
            mermaid_path.write_text(mermaid, encoding='utf-8')
            payload = {
                'inventory': inventory,
                'evaluation': evaluation,
                'contracts': contracts,
                'target_repo_id': tgt_id,
                'area_count': len(inventory.get('areas', {})),
                'view_count': len(inventory.get('views', [])),
                'contract_count': len(contracts.get('contracts', [])),
                'mermaid_path': str(mermaid_path.relative_to(self.root)),
            }
            summary_md = evaluation_markdown(evaluation) + '\n\n---\n\n' + inventory_markdown(inventory)
            paths = self._write_payload_bundle(
                run_id=run_id,
                run_dir=run_dir,
                payload=payload,
                summary_md=summary_md,
                role_prefix='usabilify_audit',
            )
            self.registry.record_artifact(
                suite=self.suite,
                run_id=run_id,
                format='mmd',
                role='usabilify_view_map',
                path=str(mermaid_path.relative_to(self.root)),
                payload={'preview': mermaid[:500]},
            )
            avg_scores = [item.get('average_score', 0) for item in evaluation.get('areas', {}).values()]
            avg_score = round(sum(avg_scores) / max(len(avg_scores), 1), 1)
            self._finish_run(run_id, 'ok', {
                'target_repo_id': tgt_id,
                'area_count': len(inventory.get('areas', {})),
                'view_count': len(inventory.get('views', [])),
                'contract_count': len(contracts.get('contracts', [])),
                'average_score': avg_score,
            })
            return self._attach_status_page('audit', {
                'ok': True,
                'suite': self.suite,
                'run_id': run_id,
                'area_count': len(inventory.get('areas', {})),
                'view_count': len(inventory.get('views', [])),
                'contract_count': len(contracts.get('contracts', [])),
                'average_score': avg_score,
                'summary': 'Usabilify evaluated UI and UX surfaces, connected available UI contracts, and highlighted the next usability steps in plain language.',
                **paths,
                'mermaid_path': str(mermaid_path),
            })
        except Exception as exc:
            self._finish_run(run_id, 'failed', {'error': str(exc)})
            return self._attach_status_page('audit', {'ok': False, 'suite': self.suite, 'run_id': run_id, 'error': str(exc), 'reason': 'audit_failed'})

    def inspect(self, query: str | None = None) -> dict:
        out = super().inspect(query)
        out['focus'] = ['ui-inventory', 'usability-rules', 'contract-bridges', 'templatify-alignment', 'next-steps']
        out['suite_role'] = 'Evaluate usability and UX quality of outward-facing repository surfaces.'
        return out

    def explain(self, audience: str = 'developer') -> dict:
        out = super().explain(audience)
        if out.get('ok'):
            out['suite_context'] = {
                'position_in_mvp': 'Usabilify is the usability and UX governance suite. It complements templatify and documentify by checking whether UI surfaces are understandable, consistent, and easier to use.',
                'works_with': ['templatify', 'documentify', 'docify', 'contractify'],
            }
        return out

    def prepare_fix(self, finding_ids: list[str]) -> dict:
        out = super().prepare_fix(finding_ids)
        out['suggested_actions'] = [
            'add visible headings, landmarks, and consistent navigation shells',
            'improve form labels, aria naming, and status feedback surfaces',
            'link UI surfaces to discoverable contracts and design guidance',
            'use templatify to normalize shared base shells before editing many child views',
        ]
        return out

    def triage(self, query: str | None = None) -> dict:
        out = super().triage(query)
        out['triage_axes'] = ['feedback visibility', 'clear structure', 'form clarity', 'consistency', 'error recovery', 'accessibility']
        return out
