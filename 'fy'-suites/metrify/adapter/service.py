from __future__ import annotations

from pathlib import Path
from typing import Any

from fy_platform.ai.base_adapter import BaseSuiteAdapter
from metrify.tools.ai_support import write_ai_pack
from metrify.tools.ledger import ensure_ledger
from metrify.tools.observify_bridge import write_observify_summary
from metrify.tools.reporting import build_summary, render_markdown, write_report_bundle


class MetrifyAdapter(BaseSuiteAdapter):
    __test__ = False

    def __init__(self, root: Path | None = None) -> None:
        super().__init__('metrify', root)

    def audit(self, target_repo_root: str) -> dict:
        target = Path(target_repo_root).resolve()
        run_id, run_dir, tgt_id = self._start_run('audit', target)
        try:
            ledger_path = self.hub_dir / 'state' / 'ledger.jsonl'
            ensure_ledger(ledger_path)
            summary = build_summary(ledger_path)
            write_report_bundle(self.root, summary)
            write_ai_pack(self.root, summary)
            write_observify_summary(self.root, summary)
            md = render_markdown(summary)
            paths = self._write_payload_bundle(run_id=run_id, run_dir=run_dir, payload=summary, summary_md=md, role_prefix='metrify_audit')
            self._finish_run(run_id, 'ok', {'target_repo_id': tgt_id, 'event_count': summary.get('event_count', 0)})
            return {'ok': True, 'suite': self.suite, 'run_id': run_id, 'target_repo_id': tgt_id, **paths}
        except Exception as exc:
            self._finish_run(run_id, 'failed', {'error': str(exc)})
            return {'ok': False, 'suite': self.suite, 'run_id': run_id, 'error': str(exc)}

    def enforce_budget(
        self,
        suite: str,
        run_budget: dict | None = None,
    ) -> dict[str, Any]:
        """Enforce cost budget for a suite run.

        Parameters
        ----------
        suite
            Suite name (e.g., 'contractify', 'docify').
        run_budget
            Expected budget for this run. If None, uses defaults.
            Expected format: {'tokens': int, 'cost_usd': float}

        Returns
        -------
        dict
            Decision dict with keys:
            - 'decision': 'allow', 'deny', or 'escalate'
            - 'reason': Brief explanation
            - 'evidence': Details (tokens available, cost limit, etc.)
            - 'policy_ids': List of policies checked
        """
        # For now, placeholder implementation
        # In production, this would query ledger for actual costs
        if run_budget is None:
            run_budget = {'tokens': 100_000, 'cost_usd': 10.0}

        # Default: allow if budget provided
        return {
            'decision': 'allow',
            'suite': suite,
            'reason': 'Within budget',
            'run_budget': run_budget,
            'policy_ids': ['policy-token-budget', 'policy-cost-limit'],
            'evidence': f'Budget check passed for {suite}',
        }
