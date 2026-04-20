from __future__ import annotations

from pathlib import Path

from _suite_service_shared import _read_json, _write_md_summary
from fy_platform.ai.strategy_profiles import load_active_strategy_profile, strategy_runtime_metadata
from fy_platform.ai.workspace import workspace_root, write_json


class ObservifyfyAdapter:
    def __init__(self, root: Path | None = None) -> None:
        self.root = workspace_root(root)

    def audit(self, target_repo_root: str | Path) -> dict:
        root = workspace_root(Path(target_repo_root))
        profile = load_active_strategy_profile(root)
        meta = strategy_runtime_metadata(root)
        readiness = _read_json(root / 'diagnosta/reports/latest_readiness_case.json')
        deep = _read_json(root / 'diagnosta/reports/latest_deep_synthesis.json')
        handoff = _read_json(root / 'diagnosta/reports/latest_handoff_packet.json')
        d_warning = _read_json(root / 'diagnosta/reports/latest_warning_ledger.json')
        closure = _read_json(root / 'coda/reports/latest_closure_pack.json')
        review = _read_json(root / 'coda/reports/latest_review_packet.json')
        c_warning = _read_json(root / 'coda/reports/latest_warning_ledger.json')
        c_residue = _read_json(root / 'coda/reports/latest_residue_ledger.json')
        diagnosta_signal = {
            'readiness_case': readiness,
            'profile_depth_signal': {'profile_behavior_depth': meta['profile_behavior_depth'], 'planning_horizon': meta['planning_horizon'], 'handoff_depth': meta['handoff_depth']},
            'deep_synthesis': deep,
            'handoff_packet': handoff,
            'warning_count': len(d_warning.get('items', []) or []),
        }
        closure_movement = {
            'packet_depth': closure.get('packet_depth', meta['closure_packet_depth']),
            'wave_packet_count': len(closure.get('wave_packets', []) or []),
            'auto_preparation_count': len(closure.get('auto_preparation_packets', []) or []),
            'obligation_count': len(closure.get('obligations', []) or []),
            'required_test_count': len(closure.get('required_tests', []) or []),
            'required_doc_count': len(closure.get('required_docs', []) or []),
            'accepted_review_item_count': len(closure.get('review_acceptances', []) or []),
            'warning_count': len(c_warning.get('items', []) or []),
            'residue_count': len(c_residue.get('items', []) or []),
        }
        coda_signal = {'present': bool(closure), 'closure_pack': closure, 'review_packet': review, 'closure_movement': closure_movement}
        ai_context = {'schema_version': 'fy.observifyfy-ai-context.v1', 'active_profile': profile.active_profile, 'profile_execution_lane': meta['profile_execution_lane'], 'readiness_status': readiness.get('readiness_status', 'unknown'), 'closure_status': closure.get('status', 'unknown'), 'warning_count': closure_movement['warning_count'], 'residue_count': closure_movement['residue_count']}
        reports = root / 'observifyfy' / 'reports'
        reports.mkdir(parents=True, exist_ok=True)
        write_json(reports / 'observifyfy_diagnosta_signal.json', diagnosta_signal)
        write_json(reports / 'observifyfy_coda_signal.json', coda_signal)
        write_json(reports / 'observifyfy_ai_context.json', ai_context)
        _write_md_summary(reports / 'observifyfy_ai_context.md', 'Observifyfy AI Context', [f"- active_profile: `{profile.active_profile}`", f"- readiness_status: `{ai_context['readiness_status']}`", f"- closure_status: `{ai_context['closure_status']}`"])
        next_steps = {'recommended_next_steps': ['Review the latest readiness and closure signals.']}
        write_json(reports / 'status/most_recent_next_steps.json', {'ok': True, 'summary': 'Observability surfaces are current.', 'next_steps': next_steps['recommended_next_steps'], 'command': 'audit', 'latest_run': {'run_id': 'observifyfy-latest'}})
        return {'ok': True, 'run_id': 'observifyfy-latest', 'active_strategy_profile': {'active_profile': profile.active_profile, 'profile_execution_lane': meta['profile_execution_lane'], 'profile_behavior_depth': meta['profile_behavior_depth']}, 'diagnosta_signal': diagnosta_signal, 'coda_signal': coda_signal, 'ai_context': ai_context, 'next_steps': next_steps}
