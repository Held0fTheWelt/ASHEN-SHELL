from __future__ import annotations

import contractify.tools.repo_paths as repo_paths
from contractify.tools.audit_pipeline import run_audit
from contractify.tools.discovery import discover_contracts_and_projections


def test_api_projection_family_is_visible() -> None:
    root = repo_paths.repo_root()
    contracts, projections, _ = discover_contracts_and_projections(root, max_contracts=60)
    ids = {c.id for c in contracts}
    assert 'CTR-API-OPENAPI-001' in ids
    proj_ids = {p.id for p in projections}
    assert {
        'PRJ-API-README',
        'PRJ-API-REFERENCE',
        'PRJ-API-POSTMAN-GUIDE',
        'PRJ-API-EXPLORER-STRATEGY',
        'PRJ-POSTMAN-README',
    }.issubset(proj_ids)


def test_api_projection_manual_unresolved_area_remains_visible() -> None:
    root = repo_paths.repo_root()
    payload = run_audit(root, max_contracts=60)
    summaries = {row['id']: row for row in payload['manual_unresolved_areas']}
    assert 'CNF-RUNTIME-SPINE-API-PROJECTION-GOVERNANCE' in summaries
    assert payload['runtime_mvp_families']['api_projection']
