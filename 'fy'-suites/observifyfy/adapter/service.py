from __future__ import annotations

from pathlib import Path

from fy_platform.ai.base_adapter import BaseSuiteAdapter
from observifyfy.tools.ai_support import build_ai_context
from observifyfy.tools.hub_cli import run_audit
from observifyfy.tools.repo_paths import fy_observifyfy_root
from observifyfy.tools.scanner import scan_workspace


class ObservifyfyAdapter(BaseSuiteAdapter):
    __test__ = False

    def __init__(self, root: Path | None = None) -> None:
        super().__init__('observifyfy', root)
        self.hub_dir = fy_observifyfy_root(self.root)
        self.hub_dir.mkdir(parents=True, exist_ok=True)
        (self.hub_dir / 'reports').mkdir(parents=True, exist_ok=True)
        (self.hub_dir / 'state').mkdir(parents=True, exist_ok=True)
        (self.hub_dir / 'generated').mkdir(parents=True, exist_ok=True)

    def audit(self, target_repo_root: str) -> dict:
        target = Path(target_repo_root).resolve()
        run_id, run_dir, _ = self._start_run('audit', target)
        try:
            result = run_audit(target)
            inventory = result['inventory']
            next_steps = result['next_steps']
            payload = {
                'inventory': inventory,
                'next_steps': next_steps,
                'ai_context': build_ai_context(inventory, next_steps),
            }
            md = ['# Observifyfy Audit', '', f"- tracked suites: {inventory['existing_suite_count']}", f"- highest next step: {next_steps.get('highest_value_next_step', {}).get('recommended_action', 'none')}", '']
            paths = self._write_payload_bundle(run_id=run_id, run_dir=run_dir, payload=payload, summary_md='\n'.join(md)+'\n', role_prefix='observifyfy_audit')
            self._finish_run(run_id, 'ok', {'tracked_suites': inventory['existing_suite_count']})
            return {'ok': True, 'suite': self.suite, 'run_id': run_id, **paths}
        except Exception as exc:
            self._finish_run(run_id, 'failed', {'error': str(exc)})
            return {'ok': False, 'suite': self.suite, 'run_id': run_id, 'error': str(exc)}

    def inspect(self, query: str | None = None) -> dict:
        out = super().inspect(query)
        inv = scan_workspace(self.root)
        out['tracked_suite_count'] = inv['existing_suite_count']
        out['internal_roots'] = inv['internal_roots']
        return out

    def prepare_fix(self, finding_ids: list[str]) -> dict:
        out = super().prepare_fix(finding_ids)
        out['suggested_actions'] = [
            "refresh internal docs routing under docs",
            "refresh internal ADR routing under docs/ADR",
            'run stale suites again and consolidate next steps',
        ]
        return out
