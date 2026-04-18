from __future__ import annotations

import ast
import statistics
from pathlib import Path

from fy_platform.ai.base_adapter import BaseSuiteAdapter
from fy_platform.ai.workspace import write_json, write_text


class DespaghettifyAdapter(BaseSuiteAdapter):
    __test__ = False
    FILE_SPIKE_LINES = 350
    FUNC_SPIKE_LINES = 80

    def __init__(self, root: Path | None = None) -> None:
        super().__init__('despaghettify', root)

    def _severity(self, value: int, *, base: int) -> str:
        if value >= base * 2:
            return 'high'
        if value >= int(base * 1.3):
            return 'medium'
        return 'low'

    def _scan(self, target: Path) -> dict:
        file_spikes = []
        function_spikes = []
        line_counts = []
        total_files = 0
        for path in target.rglob('*.py'):
            parts = set(path.parts)
            if 'tests' in parts or '__pycache__' in parts or '.venv' in parts:
                continue
            total_files += 1
            rel = path.relative_to(target).as_posix()
            text = path.read_text(encoding='utf-8', errors='replace')
            lines = text.splitlines()
            line_counts.append(len(lines))
            if len(lines) >= self.FILE_SPIKE_LINES:
                file_spikes.append({'path': rel, 'line_count': len(lines), 'category': 'local_spike_file_length', 'severity': self._severity(len(lines), base=self.FILE_SPIKE_LINES)})
            try:
                module = ast.parse(text)
            except SyntaxError:
                continue
            for node in ast.walk(module):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and hasattr(node, 'end_lineno'):
                    span = int(node.end_lineno or node.lineno) - int(node.lineno) + 1
                    if span >= self.FUNC_SPIKE_LINES:
                        function_spikes.append({'path': rel, 'name': node.name, 'line_span': span, 'category': 'local_spike_function_length', 'severity': self._severity(span, base=self.FUNC_SPIKE_LINES)})
        median_lines = int(statistics.median(line_counts)) if line_counts else 0
        avg_lines = round(sum(line_counts) / len(line_counts), 2) if line_counts else 0.0
        sorted_counts = sorted(line_counts)
        trim = max(1, int(len(sorted_counts) * 0.1)) if len(sorted_counts) >= 5 else 0
        trimmed = sorted_counts[:-trim] if trim else sorted_counts
        trimmed_average = round(sum(trimmed) / len(trimmed), 2) if trimmed else avg_lines
        robust_baseline = median_lines if (file_spikes or function_spikes) else int(trimmed_average)
        global_category = 'low' if robust_baseline <= 120 else 'medium' if robust_baseline <= 220 else 'high'
        return {
            'total_python_files': total_files,
            'median_file_lines': median_lines,
            'average_file_lines': avg_lines,
            'trimmed_average_file_lines': trimmed_average,
            'file_spikes': file_spikes,
            'function_spikes': function_spikes,
            'global_category': global_category,
            'local_spike_count': len(file_spikes) + len(function_spikes),
        }

    def _wave_plan(self, payload: dict) -> dict:
        actions = []
        for spike in payload['file_spikes']:
            actions.append({'kind': 'split_file', 'path': spike['path'], 'severity': spike['severity']})
        for spike in payload['function_spikes']:
            actions.append({'kind': 'extract_function', 'path': spike['path'], 'name': spike['name'], 'severity': spike['severity']})
        actions.sort(key=lambda item: {'high': 0, 'medium': 1, 'low': 2}[item['severity']])
        return {'global_category': payload['global_category'], 'action_count': len(actions), 'actions': actions}

    def audit(self, target_repo_root: str) -> dict:
        target = Path(target_repo_root).resolve()
        run_id, run_dir, tgt_id = self._start_run('audit', target)
        try:
            payload = self._scan(target)
            wave_plan = self._wave_plan(payload)
            wave_json = run_dir / 'despaghettify_wave_plan.json'
            wave_md = run_dir / 'despaghettify_wave_plan.md'
            write_json(wave_json, wave_plan)
            lines = ['# Despaghettify Wave Plan', '', f"- global_category: {wave_plan['global_category']}", f"- action_count: {wave_plan['action_count']}", '']
            for action in wave_plan['actions'][:20]:
                if action['kind'] == 'split_file':
                    lines.append(f"- split file `{action['path']}` ({action['severity']})")
                else:
                    lines.append(f"- extract `{action['path']}::{action['name']}` ({action['severity']})")
            write_text(wave_md, '\n'.join(lines) + '\n')
            md_lines = ['# Despaghettify Audit', '', f"- global_category: {payload['global_category']}", f"- average_file_lines: {payload['average_file_lines']}", f"- local_spike_count: {payload['local_spike_count']}", f"- wave_plan: `{wave_json.relative_to(self.root)}`", '']
            for spike in payload['file_spikes'][:10]:
                md_lines.append(f"- file spike: `{spike['path']}` ({spike['line_count']} lines, {spike['severity']})")
            for spike in payload['function_spikes'][:10]:
                md_lines.append(f"- function spike: `{spike['path']}::{spike['name']}` ({spike['line_span']} lines, {spike['severity']})")
            payload['wave_plan'] = {'json_path': str(wave_json.relative_to(self.root)), 'md_path': str(wave_md.relative_to(self.root)), 'action_count': wave_plan['action_count']}
            paths = self._write_payload_bundle(run_id=run_id, run_dir=run_dir, payload=payload, summary_md='\n'.join(md_lines) + '\n', role_prefix='despaghettify_audit')
            self._finish_run(run_id, 'ok', {'local_spike_count': payload['local_spike_count'], 'target_repo_id': tgt_id, 'wave_action_count': wave_plan['action_count']})
            return {'ok': True, 'suite': self.suite, 'run_id': run_id, 'local_spike_count': payload['local_spike_count'], 'wave_action_count': wave_plan['action_count'], **paths}
        except Exception as exc:
            self._finish_run(run_id, 'failed', {'error': str(exc)})
            return {'ok': False, 'suite': self.suite, 'run_id': run_id, 'error': str(exc)}

    def prepare_fix(self, finding_ids: list[str]) -> dict:
        out = super().prepare_fix(finding_ids)
        out['suggested_actions'] = [
            'split highest-severity files along domain seams',
            'extract oversized functions into helpers or services',
            'close the local spike wave before re-evaluating global category',
            'rerun despaghettify to confirm local spike closure',
        ]
        return out
