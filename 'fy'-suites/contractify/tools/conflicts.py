"""Conflict detection — deterministic anchors first, then bounded heuristics.

Every ``ConflictFinding`` records ``classification`` for backlog triage. Human review is
required when ``requires_human_review`` is true unless confidence is explicitly high for a
mechanical clash (duplicate normative table targets).
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from urllib.parse import unquote

from contractify.tools.discovery import NORMATIVE_INDEX, OPENAPI_DEFAULT, POSTMAN_MANIFEST
from contractify.tools.models import ConflictFinding, ProjectionRecord
from contractify.tools.versioning import openapi_sha256_prefix

# Markdown table / inline link targets from normative index (same cell patterns as human editors use).
_MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

# ADR vocabulary buckets (bounded overlap heuristic — not semantic contradiction proof).
_ADR_OVERLAP_TERMS = (
    ("scene identity", ("scene identity", "scene_id", "scene-id")),
    ("session surface", ("session surface", "session_surface", "session")),
    ("runtime authority", ("runtime authority", "runtime_authority", "authority")),
)


def _norm_index_link(repo: Path, index_dir: Path, raw_target: str) -> str:
    """Resolve link target relative to the normative index directory; return repo-posix path."""
    t = unquote(raw_target.strip().split("#", 1)[0].strip())
    if not t or t.startswith(("http://", "https://", "mailto:")):
        return ""
    resolved = (index_dir / t).resolve()
    try:
        return resolved.relative_to(repo.resolve()).as_posix()
    except ValueError:
        return ""


def detect_duplicate_normative_index_targets(repo: Path) -> list[ConflictFinding]:
    """Two or more index rows link to the same resolved path — anchor ambiguity (deterministic)."""
    repo = repo.resolve()
    p = repo / NORMATIVE_INDEX
    if not p.is_file():
        return []
    text = p.read_text(encoding="utf-8", errors="replace")
    index_dir = p.parent
    counts: dict[str, list[str]] = {}
    for _label, target in _MD_LINK.findall(text):
        norm = _norm_index_link(repo, index_dir, target)
        if not norm:
            continue
        counts.setdefault(norm, []).append(target.strip())

    out: list[ConflictFinding] = []
    for norm, raw_list in counts.items():
        if len(raw_list) < 2:
            continue
        out.append(
            ConflictFinding(
                id=f"CNF-NORM-DUP-{hashlib.sha256(norm.encode()).hexdigest()[:10]}",
                conflict_type="duplicate_normative_navigation_target",
                summary=f"Normative index lists the same resolved target more than once: {norm}",
                sources=[NORMATIVE_INDEX, norm],
                confidence=0.95,
                requires_human_review=False,
                notes="Mechanical duplicate-link detection in the index markdown.",
                classification="normative_anchor_ambiguity",
                normative_sources=[NORMATIVE_INDEX],
                observed_or_projection_sources=[],
            )
        )
    return out


def detect_adr_vocabulary_overlap(repo: Path) -> list[ConflictFinding]:
    """Multiple ADRs hit the same bounded vocabulary bucket (heuristic overlap)."""
    adr_dir = repo / "docs" / "governance"
    if not adr_dir.is_dir():
        return []
    out: list[ConflictFinding] = []
    for bucket, keywords in _ADR_OVERLAP_TERMS:
        hits: list[str] = []
        for adr in sorted(adr_dir.glob("adr-*.md")):
            if "template" in adr.stem.lower():
                continue
            text = adr.read_text(encoding="utf-8", errors="replace").lower()
            if any(k.lower() in text for k in keywords):
                hits.append(adr.name)
        if len(hits) >= 2:
            out.append(
                ConflictFinding(
                    id=f"CNF-ADR-VOC-{hashlib.sha256(bucket.encode()).hexdigest()[:8]}",
                    conflict_type="adr_vocabulary_overlap",
                    summary=f"Multiple ADRs reference the same governance vocabulary bucket “{bucket}”; "
                    "check supersession and single-current-truth narrative.",
                    sources=hits,
                    confidence=0.55,
                    requires_human_review=True,
                    notes="Keyword bucket overlap only — not proof of logical contradiction.",
                    classification="normative_vocabulary_overlap",
                    normative_sources=hits,
                    observed_or_projection_sources=[],
                )
            )
    return out


def detect_projection_fingerprint_mismatch(
    repo: Path,
    projections: list[ProjectionRecord],
) -> list[ConflictFinding]:
    """Projection ``contract_version_ref`` is a 16-hex OpenAPI prefix that disagrees with disk (deterministic)."""
    repo = repo.resolve()
    openapi = repo / OPENAPI_DEFAULT
    if not openapi.is_file():
        return []
    full_sha = hashlib.sha256(openapi.read_bytes()).hexdigest()
    prefix = openapi_sha256_prefix(full_sha)
    out: list[ConflictFinding] = []
    for pr in projections:
        ref = (pr.contract_version_ref or "").strip().lower()
        if len(ref) != 16 or any(c not in "0123456789abcdef" for c in ref):
            continue
        if ref == prefix:
            continue
        out.append(
            ConflictFinding(
                id=f"CNF-PRJ-SHA-{hashlib.sha256(pr.path.encode()).hexdigest()[:10]}",
                conflict_type="projection_openapi_fingerprint_mismatch",
                summary=f"Projection {pr.path} declares openapi fingerprint prefix {ref!r} but "
                f"current OpenAPI SHA256 prefix is {prefix!r}.",
                sources=[pr.path, OPENAPI_DEFAULT, POSTMAN_MANIFEST],
                confidence=1.0,
                requires_human_review=False,
                notes="Treat as stale projection or wrong manifest until regenerated.",
                classification="projection_anchor_mismatch",
                normative_sources=[OPENAPI_DEFAULT],
                observed_or_projection_sources=[pr.path],
            )
        )
    return out


def detect_deprecated_adr_without_supersession_link(repo: Path) -> list[ConflictFinding]:
    """Explicit ``Status: Deprecated`` / ``Superseded`` without supersession navigation (bounded header scan)."""
    adr_dir = repo / "docs" / "governance"
    if not adr_dir.is_dir():
        return []
    out: list[ConflictFinding] = []
    linkish = re.compile(r"supersed|superseded\s+by|replaced\s+by", re.IGNORECASE)
    bad_status = re.compile(r"(?im)^\s*\*{0,2}status\*{0,2}\s*:\s*(deprecated|superseded)\b")
    for adr in sorted(adr_dir.glob("adr-*.md")):
        if "template" in adr.stem.lower():
            continue
        head = adr.read_text(encoding="utf-8", errors="replace")[:6000]
        if not bad_status.search(head):
            continue
        if linkish.search(head):
            continue
        rel = adr.relative_to(repo).as_posix()
        out.append(
            ConflictFinding(
                id=f"CNF-ADR-LIFE-{adr.stem[:20]}",
                conflict_type="lifecycle_supersession_gap",
                summary=f"ADR {rel} declares deprecated/superseded status in the header but no explicit supersession "
                "navigation pattern — add a link to the replacement anchor.",
                sources=[rel],
                confidence=0.62,
                requires_human_review=True,
                notes="Header-only scan for Status + supersession cues.",
                classification="supersession_gap",
                normative_sources=[rel],
                observed_or_projection_sources=[],
            )
        )
    return out


def detect_all_conflicts(repo: Path, projections: list[ProjectionRecord]) -> list[ConflictFinding]:
    """Run all conflict passes; de-duplicate by ``id``."""
    all_c: list[ConflictFinding] = []
    all_c.extend(detect_duplicate_normative_index_targets(repo))
    all_c.extend(detect_adr_vocabulary_overlap(repo))
    all_c.extend(detect_projection_fingerprint_mismatch(repo, projections))
    all_c.extend(detect_deprecated_adr_without_supersession_link(repo))
    seen: set[str] = set()
    uniq: list[ConflictFinding] = []
    for c in all_c:
        if c.id in seen:
            continue
        seen.add(c.id)
        uniq.append(c)
    return uniq
