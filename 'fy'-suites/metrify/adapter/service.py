from __future__ import annotations

from pathlib import Path

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
