"""Relation extension — bounded edges on top of discovery."""
from __future__ import annotations

import contractify.tools.repo_paths as repo_paths
from contractify.tools.discovery import discover_contracts_and_projections
from contractify.tools.relations import extend_relations


def test_extend_relations_adds_normative_to_openapi_reference() -> None:
    root = repo_paths.repo_root()
    contracts, projections, base = discover_contracts_and_projections(root, max_contracts=40)
    extended = extend_relations(root, contracts, projections, base)
    kinds = {(r.relation, r.source_id, r.target_id) for r in extended}
    assert ("references", "CTR-NORM-INDEX-001", "CTR-API-OPENAPI-001") in kinds
