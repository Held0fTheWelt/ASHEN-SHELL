from __future__ import annotations

from pathlib import Path

from templatify.tools.template_registry import discover_templates

REQUIRED_FAMILIES = {'documentify', 'reports', 'context_packs'}


def validate_templates(workspace_root: Path) -> dict:
    records = discover_templates(workspace_root)
    template_ids = [item.template_id for item in records]
    duplicates = sorted({tid for tid in template_ids if template_ids.count(tid) > 1})
    families = sorted({item.family for item in records})
    missing_families = sorted(REQUIRED_FAMILIES - set(families))
    empty_templates = []
    for item in records:
        path = workspace_root / 'templatify' / 'templates' / item.path
        if not path.read_text(encoding='utf-8', errors='replace').strip():
            empty_templates.append(item.template_id)
    warnings = []
    if any('role' in item.name for item in records) and not any('role_summary' in item.placeholders for item in records if 'role' in item.name):
        warnings.append('role_templates_without_role_summary_placeholder')
    return {
        'ok': not duplicates and not missing_families and not empty_templates and bool(records),
        'template_count': len(records),
        'families': families,
        'duplicates': duplicates,
        'missing_families': missing_families,
        'empty_templates': empty_templates,
        'warnings': warnings,
    }
