"""Add bounded, high-signal relation edges beyond discovery’s core Postman / audience edges."""
from __future__ import annotations

import re
from pathlib import Path

from contractify.tools.discovery import NORMATIVE_INDEX, OPENAPI_DEFAULT
from contractify.tools.models import ContractRecord, ProjectionRecord, RelationEdge

# Cap index-derived edges to avoid graph explosion (anti-bureaucracy).
_MAX_INDEX_REFERENCE_EDGES = 14


def extend_relations(
    repo: Path,
    contracts: list[ContractRecord],
    projections: list[ProjectionRecord],
    base: list[RelationEdge],
) -> list[RelationEdge]:
    """Return ``base`` plus a small set of deterministic cross-links."""
    repo = repo.resolve()
    out: list[RelationEdge] = list(base)
    ids = {c.id for c in contracts}

    idx_path = repo / NORMATIVE_INDEX
    if idx_path.is_file() and "CTR-NORM-INDEX-001" in ids:
        text = idx_path.read_text(encoding="utf-8", errors="replace")
        if "openapi" in text.lower() and "CTR-API-OPENAPI-001" in ids:
            out.append(
                RelationEdge(
                    relation="references",
                    source_id="CTR-NORM-INDEX-001",
                    target_id="CTR-API-OPENAPI-001",
                    evidence="Normative index prose references the HTTP/OpenAPI contract surface.",
                    confidence=0.82,
                )
            )
        # Table targets that look like slice / runtime docs (bounded).
        seen_idx: set[str] = set()
        for m in re.finditer(r"\]\((\.\./[^)]+?\.md)\)", text):
            if len(out) >= len(base) + _MAX_INDEX_REFERENCE_EDGES:
                break
            raw = m.group(1).strip()
            resolved = (idx_path.parent / raw).resolve()
            try:
                rel = resolved.relative_to(repo).as_posix()
            except ValueError:
                continue
            if not resolved.is_file():
                continue
            tid = f"DOC:{rel}"
            if tid in seen_idx:
                continue
            seen_idx.add(tid)
            out.append(
                RelationEdge(
                    relation="indexes",
                    source_id="CTR-NORM-INDEX-001",
                    target_id=tid,
                    evidence=f"Normative index table links to {rel}",
                    confidence=0.88,
                )
            )

    if "CTR-API-OPENAPI-001" in ids and (repo / "backend").is_dir():
        out.append(
            RelationEdge(
                relation="implements",
                source_id="CTR-API-OPENAPI-001",
                target_id="OBS:backend/",
                evidence="OpenAPI describes Flask `/api/v1` routes implemented under backend/.",
                confidence=0.72,
            )
        )

    if "CTR-OPS-RUNTIME-001" in ids and "CTR-NORM-INDEX-001" in ids:
        out.append(
            RelationEdge(
                relation="operationalizes",
                source_id="CTR-OPS-RUNTIME-001",
                target_id="CTR-NORM-INDEX-001",
                evidence="Operational runbook translates normative governance into operator-facing procedures.",
                confidence=0.68,
            )
        )

    return out
