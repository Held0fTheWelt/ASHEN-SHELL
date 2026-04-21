from __future__ import annotations
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from .enums import AuthorityLevel, DomainType, ReviewStatus
from .records import MemoryEntry

@dataclass
class DuplicateCluster:
    entries: list[MemoryEntry]
    cluster_type: str

@dataclass
class ConsolidationResult:
    semantic_candidates: list[MemoryEntry] = field(default_factory=list)
    duplicate_clusters: list[DuplicateCluster] = field(default_factory=list)

class MemoryConsolidator:
    def detect_duplicates(self, entries: list[MemoryEntry], similarity_threshold: float = 0.95) -> list[DuplicateCluster]:
        clusters: list[DuplicateCluster] = []
        seen: set[str] = set()
        for i, left in enumerate(entries):
            if left.record_id in seen:
                continue
            group = [left]
            cluster_type = "exact_duplicate"
            for right in entries[i + 1:]:
                if right.record_id in seen:
                    continue
                ratio = SequenceMatcher(None, left.normalized_value, right.normalized_value).ratio()
                if ratio >= similarity_threshold:
                    group.append(right)
                    seen.add(right.record_id)
                    if ratio < 1.0:
                        cluster_type = "near_duplicate"
            if len(group) > 1:
                clusters.append(DuplicateCluster(entries=group, cluster_type=cluster_type))
            seen.add(left.record_id)
        return clusters

    def consolidate(self, entries: list[MemoryEntry]) -> ConsolidationResult:
        result = ConsolidationResult()
        result.duplicate_clusters = self.detect_duplicates(entries)
        by_slot: dict[str, list[MemoryEntry]] = {}
        for entry in entries:
            by_slot.setdefault(entry.slot_key, []).append(entry)
        for slot_key, group in by_slot.items():
            confirmed = [
                g for g in group
                if g.authority_level >= AuthorityLevel.CONFIRMED
                and g.review_status in {ReviewStatus.CONFIRMED, ReviewStatus.UNCONFIRMED}
                and g.conflict_risk < 0.75
            ]
            if len(confirmed) < 2:
                continue
            primary = max(confirmed, key=lambda item: item.authority_level.value)
            candidate = MemoryEntry(
                record_id=f"semantic::{slot_key}",
                partition_key=primary.partition_key,
                domain_type=DomainType.CANONICAL_TRUTH if primary.domain_type == DomainType.CANONICAL_TRUTH else DomainType.BELIEF,
                assertion_mode=primary.assertion_mode,
                authority_level=AuthorityLevel.CONFIRMED,
                review_status=ReviewStatus.UNCONFIRMED,
                carrier_scope=primary.carrier_scope,
                entity_id=primary.entity_id,
                field_name=primary.field_name,
                slot_key=primary.slot_key,
                content=primary.content,
                normalized_value=primary.normalized_value,
                source_lineage=[e.record_id for e in confirmed],
                temporal_validity=primary.temporal_validity,
                created_at=primary.created_at,
                last_accessed=primary.last_accessed,
                metadata={"candidate_kind": "semantic_promotion"},
            )
            result.semantic_candidates.append(candidate)
        return result
