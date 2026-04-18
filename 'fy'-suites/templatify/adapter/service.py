from __future__ import annotations

from pathlib import Path

from documentify.tools.document_builder import collect_repository_context
from fy_platform.ai.base_adapter import BaseSuiteAdapter
from templatify.tools.template_drift import scan_generated_drift
from templatify.tools.template_inventory import inspect_areas
from templatify.tools.template_registry import discover_templates
from templatify.tools.template_render import render_with_header
from templatify.tools.template_validator import validate_templates


class TemplatifyAdapter(BaseSuiteAdapter):
    __test__ = False

    def __init__(self, root: Path | None = None) -> None:
        super().__init__('templatify', root)

    def audit(self, target_repo_root: str) -> dict:
        target = Path(target_repo_root).resolve()
        run_id, run_dir, tgt_id = self._start_run('audit', target)
        try:
            validation = validate_templates(self.root)
            templates = [item.__dict__ for item in discover_templates(self.root)]
            inventory = inspect_areas(target)
            preview_dir = self.hub_dir / 'generated' / tgt_id / run_id
            preview_dir.mkdir(parents=True, exist_ok=True)
            context = collect_repository_context(target)
            ctx = {
                'services_csv': ', '.join(context['services']) or 'no detected services',
                'docs_dirs_csv': ', '.join(context['docs_dirs']) or 'none',
                'workflows_csv': ', '.join(context['workflows']) or 'none',
                'service_lines': ''.join(f'- `{svc}/`\n' for svc in context['services']) or '- none\n',
                'workflow_lines': ''.join(f'- `{wf}`\n' for wf in context['workflows']) or '- none\n',
                'key_doc_lines': ''.join(f'- `{doc}`\n' for doc in context['key_docs']) or '- none\n',
                'role_title': 'Developer',
                'role_summary': 'Implement and debug the repository surfaces.',
                'relevant_path_lines': '- `src/`\n- `tests/`\n',
            }
            preview_paths = []
            for family, name, outfile in [
                ('documentify', 'easy_overview', 'documentify_easy_preview.md'),
                ('documentify', 'technical_reference', 'documentify_technical_preview.md'),
                ('documentify', 'ai_read', 'documentify_ai_read_preview.md'),
            ]:
                rendered, record = render_with_header(self.root, family, name, ctx)
                out_path = preview_dir / outfile
                out_path.write_text(rendered, encoding='utf-8')
                preview_paths.append({'path': str(out_path.relative_to(self.root)), 'template_id': record.template_id})
            drift = scan_generated_drift(self.root, preview_dir)
            payload = {
                'validation': validation,
                'template_count': len(templates),
                'templates': templates,
                'inventory': inventory,
                'preview_dir': str(preview_dir.relative_to(self.root)),
                'preview_paths': preview_paths,
                'drift': drift,
                'target_repo_id': tgt_id,
            }
            md_lines = [
                '# Templatify Audit',
                '',
                f"- template_count: {len(templates)}",
                f"- validation_ok: {validation['ok']}",
                f"- preview_dir: `{preview_dir.relative_to(self.root)}`",
                f"- inventory_areas: {len(inventory.get('areas', {}))}",
                f"- drift_count: {drift['drift_count']}",
                '',
                '## Families',
                '',
            ]
            md_lines.extend(f"- `{family}`" for family in validation['families'])
            md_lines.extend(['', '## Preview files', ''])
            md_lines.extend(f"- `{item['path']}` ← `{item['template_id']}`" for item in preview_paths)
            paths = self._write_payload_bundle(run_id=run_id, run_dir=run_dir, payload=payload, summary_md='\n'.join(md_lines)+'\n', role_prefix='templatify_audit')
            self._finish_run(run_id, 'ok', {'template_count': len(templates), 'drift_count': drift['drift_count'], 'target_repo_id': tgt_id})
            return {'ok': True, 'suite': self.suite, 'run_id': run_id, 'template_count': len(templates), 'drift_count': drift['drift_count'], **paths, 'preview_dir': str(preview_dir)}
        except Exception as exc:
            self._finish_run(run_id, 'failed', {'error': str(exc)})
            return {'ok': False, 'suite': self.suite, 'run_id': run_id, 'error': str(exc)}

    def inspect(self, query: str | None = None) -> dict:
        out = super().inspect(query)
        discovered = discover_templates(self.root)
        out['families'] = sorted({item.family for item in discovered})
        out['template_count'] = len(discovered)
        return out

    def prepare_fix(self, finding_ids: list[str]) -> dict:
        out = super().prepare_fix(finding_ids)
        out['suggested_actions'] = [
            'add or normalize missing template families',
            'align placeholders across related templates',
            'refresh generated documents to clear template drift',
            'promote repeated ad-hoc markdown into tracked templates',
        ]
        return out
