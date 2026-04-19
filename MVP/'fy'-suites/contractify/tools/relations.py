"""Add bounded, high-signal relation edges beyond discovery’s core Postman / audience edges."""
from __future__ import annotations

import re
from pathlib import Path

from contractify.tools.discovery import NORMATIVE_INDEX, OPENAPI_DEFAULT
from contractify.tools.models import ConflictFinding, ContractRecord, ProjectionRecord, RelationEdge
from contractify.tools.versioning import adr_supersedes_line, resolve_supersedes_markdown_target

# Cap index-derived edges to avoid graph explosion (anti-bureaucracy).
_MAX_INDEX_REFERENCE_EDGES = 14
_MAX_FIELD_EDGES_PER_BUCKET = 3


def _field_edges(repo: Path, contracts: list[ContractRecord]) -> list[RelationEdge]:
    """Project explicit contract fields into bounded relation edges when paths still exist."""
    out: list[RelationEdge] = []
    seen: set[tuple[str, str, str]] = set()
    repo = repo.resolve()
    def add_edge(source_id: str, relation: str, raw: str, prefix: str, evidence: str, confidence: float) -> None:
        """Append one bounded field-derived relation edge when the referenced path exists."""
        candidate = (repo / raw).resolve()
        try:
            candidate.relative_to(repo)
        except ValueError:
            return
        if not candidate.exists():
            return
        key = (source_id, relation, raw)
        if key in seen:
            return
        seen.add(key)
        out.append(RelationEdge(relation=relation, source_id=source_id, target_id=f"{prefix}:{raw}", evidence=evidence, confidence=confidence))

    for c in contracts:
        for raw in list(c.implemented_by)[:_MAX_FIELD_EDGES_PER_BUCKET]:
            add_edge(c.id, "implemented_by", raw, "OBS", f"{c.id} explicitly names existing implementation surface {raw}", 0.9)
        for raw in list(c.validated_by)[:_MAX_FIELD_EDGES_PER_BUCKET]:
            add_edge(c.id, "validated_by", raw, "VER", f"{c.id} explicitly names existing validation surface {raw}", 0.9)
        for raw in list(c.documented_in)[:_MAX_FIELD_EDGES_PER_BUCKET]:
            add_edge(c.id, "documented_in", raw, "DOC", f"{c.id} explicitly names existing documentation surface {raw}", 0.86)
    return out


def _adr_contract_id(stem: str) -> str:
    slug = stem.upper().replace("-", "_")
    return f"CTR-ADR-{slug[:24]}"


def extend_relations(
    repo: Path,
    contracts: list[ContractRecord],
    projections: list[ProjectionRecord],
    base: list[RelationEdge],
    *,
    conflicts: list[ConflictFinding] | None = None,
) -> list[RelationEdge]:
    """Return ``base`` plus a small set of deterministic cross-links."""
    repo = repo.resolve()
    out: list[RelationEdge] = list(base)
    out.extend(_field_edges(repo, contracts))
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

    if "CTR-POSTMANIFY-TASK-001" in ids and "CTR-API-OPENAPI-001" in ids:
        out.append(
            RelationEdge(
                relation="references",
                source_id="CTR-POSTMANIFY-TASK-001",
                target_id="CTR-API-OPENAPI-001",
                evidence="Postmanify procedure consumes the canonical OpenAPI anchor for collection generation.",
                confidence=0.9,
            )
        )

    if "CTR-DOCIFY-TASK-001" in ids and "CTR-CONTRACTIFY-SELF-001" in ids:
        out.append(
            RelationEdge(
                relation="documents",
                source_id="CTR-DOCIFY-TASK-001",
                target_id="CTR-CONTRACTIFY-SELF-001",
                evidence="Docify default roots include contractify; check task documents cross-suite audit obligations.",
                confidence=0.62,
            )
        )

    adr_dir = repo / "docs" / "governance"
    if adr_dir.is_dir():
        for adr in sorted(adr_dir.glob("adr-*.md")):
            if "template" in adr.stem.lower():
                continue
            head = adr.read_text(encoding="utf-8", errors="replace")[:12_000]
            body = adr_supersedes_line(head)
            if not body:
                continue
            sup = resolve_supersedes_markdown_target(body, adr_file=adr, repo=repo)
            if not sup:
                continue
            tgt_path = repo / sup
            if not tgt_path.is_file():
                continue
            src_id = _adr_contract_id(adr.stem)
            tgt_id = _adr_contract_id(tgt_path.stem)
            if src_id in ids and tgt_id in ids:
                out.append(
                    RelationEdge(
                        relation="supersedes",
                        source_id=src_id,
                        target_id=tgt_id,
                        evidence=f"{adr.name} declares explicit Supersedes navigation to {sup}",
                        confidence=0.9,
                    )
                )

    wf_dir = repo / ".github" / "workflows"
    if "CTR-API-OPENAPI-001" in ids and wf_dir.is_dir():
        for wf in sorted(wf_dir.glob("*.yml"))[:6]:
            txt = wf.read_text(encoding="utf-8", errors="replace")[:20_000]
            low = txt.lower()
            if "openapi" not in low and "postman" not in low:
                continue
            rel = wf.relative_to(repo).as_posix()
            out.append(
                RelationEdge(
                    relation="validates",
                    source_id=f"OBS:{rel}",
                    target_id="CTR-API-OPENAPI-001",
                    evidence=f"Workflow {rel} references OpenAPI/Postman artefacts (regeneration or contract checks).",
                    confidence=0.66,
                )
            )
            break

    if conflicts:
        for c in conflicts:
            if c.classification != "normative_anchor_ambiguity":
                continue
            dup = next((x for x in c.normative_candidates if x != NORMATIVE_INDEX), None)
            if not dup:
                continue
            if "CTR-NORM-INDEX-001" not in ids:
                continue
            tid = f"DOC:{dup}"
            out.append(
                RelationEdge(
                    relation="conflicts_with",
                    source_id="CTR-NORM-INDEX-001",
                    target_id=tid,
                    evidence="Normative index lists the same resolved markdown target more than once (navigation ambiguity).",
                    confidence=0.88,
                )
            )

    return out
