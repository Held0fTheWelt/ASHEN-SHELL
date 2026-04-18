from __future__ import annotations

from pathlib import Path

from fy_platform.ai.base_adapter import BaseSuiteAdapter
from mvpify.tools.hub_cli import run as run_mvpify


class MVPifyAdapter(BaseSuiteAdapter):
    __test__ = False

    def __init__(self, root: Path | None = None) -> None:
        super().__init__('mvpify', root)

    def audit(self, target_repo_root: str) -> dict:
        target = Path(target_repo_root).resolve()
        run_id, run_dir, tgt_id = self._start_run('audit', target)
        try:
            payload = run_mvpify(target, source_root=str(target))
            import_inventory = payload.get('import_inventory', {})
            plan = payload.get('plan', {})
            summary_md = "\n".join(
                [
                    '# MVPify Audit',
                    '',
                    f"- target: `{target}`",
                    f"- import_source: `{import_inventory.get('source', '')}`",
                    f"- artifact_count: {import_inventory.get('artifact_count', 0)}",
                    f"- step_count: {len(plan.get('steps', []))}",
                    f"- highest_value_next_step: `{(plan.get('highest_value_next_step') or {}).get('suite', 'mvpify')}`",
                    '',
                ]
            ) + "\n"
            paths = self._write_payload_bundle(
                run_id=run_id,
                run_dir=run_dir,
                payload=payload,
                summary_md=summary_md,
                role_prefix='mvpify_audit',
            )
            self._finish_run(
                run_id,
                'ok',
                {
                    'artifact_count': import_inventory.get('artifact_count', 0),
                    'step_count': len(plan.get('steps', [])),
                    'target_repo_id': tgt_id,
                },
            )
            return {
                'ok': True,
                'suite': self.suite,
                'run_id': run_id,
                'artifact_count': import_inventory.get('artifact_count', 0),
                'step_count': len(plan.get('steps', [])),
                **paths,
            }
        except Exception as exc:
            self._finish_run(run_id, 'failed', {'error': str(exc)})
            return {'ok': False, 'suite': self.suite, 'run_id': run_id, 'error': str(exc)}

    def inspect(self, query: str | None = None) -> dict:
        out = super().inspect(query)
        out['suite_role'] = 'Import, normalize, mirror, and orchestrate prepared MVP bundles into the governed fy workspace.'
        out['focus'] = ['prepared MVP intake', 'doc mirroring', 'suite orchestration', 'observifyfy-tracked import cycles']
        return out

    def prepare_fix(self, finding_ids: list[str]) -> dict:
        out = super().prepare_fix(finding_ids)
        out['suggested_actions'] = [
            'normalize imported MVP surfaces into mvpify/imports/<id>/normalized',
            'mirror MVP docs into docs/MVPs/imports/<id> so implementation folders can later be removed',
            'handoff imported contracts to contractify import or legacy-import as needed',
            'refresh observifyfy after each MVP import cycle',
        ]
        return out
