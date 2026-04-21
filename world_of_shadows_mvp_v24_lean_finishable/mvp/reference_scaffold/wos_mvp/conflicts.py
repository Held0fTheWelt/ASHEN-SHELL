from __future__ import annotations
from dataclasses import dataclass

from .enums import AuthorityLevel, ConflictClass, DomainType, ReviewStatus
from .records import ConflictRecord, MemoryEntry
from .slotting import AssertionSlotResolver

@dataclass
class ConflictDetector:
    slot_resolver: AssertionSlotResolver

    def detect(self, new_entry: MemoryEntry, existing_entries: list[MemoryEntry]) -> list[ConflictRecord]:
        conflicts: list[ConflictRecord] = []
        for existing in existing_entries:
            if new_entry.partition_key.world_module() != existing.partition_key.world_module():
                continue

            if not self.slot_resolver.same_slot(new_entry, existing):
                continue

            if not new_entry.temporal_validity.overlaps(existing.temporal_validity):
                continue

            if new_entry.normalized_value == existing.normalized_value:
                continue

            conflict_class = self._classify(new_entry, existing)
            severity = self._severity(new_entry, existing, conflict_class)
            conflicts.append(
                ConflictRecord(
                    conflict_id=f"conflict::{new_entry.record_id}::{existing.record_id}",
                    conflict_class=conflict_class,
                    involved_record_ids=[new_entry.record_id, existing.record_id],
                    same_slot_decision=True,
                    severity=severity,
                    suggested_resolution=self.suggest_resolution(new_entry, existing),
                    human_review_required=self._requires_human_review(new_entry, existing, conflict_class, severity),
                )
            )
        return conflicts

    def _classify(self, left: MemoryEntry, right: MemoryEntry) -> ConflictClass:
        if DomainType.SACRED in {left.domain_type, right.domain_type}:
            return ConflictClass.SACRED_COLLISION
        if left.assertion_mode != right.assertion_mode:
            return ConflictClass.DOMAIN_TENSION
        return ConflictClass.SLOT_VALUE_CONTRADICTION

    def _severity(self, left: MemoryEntry, right: MemoryEntry, conflict_class: ConflictClass) -> float:
        authority_weight = max(left.authority_level.value, right.authority_level.value) / float(AuthorityLevel.CANONICAL.value)
        base = 0.55
        if conflict_class == ConflictClass.DOMAIN_TENSION:
            base = 0.65
        if conflict_class == ConflictClass.SACRED_COLLISION:
            base = 0.9
        return round(min(1.0, base + 0.25 * authority_weight), 4)

    def _requires_human_review(
        self,
        left: MemoryEntry,
        right: MemoryEntry,
        conflict_class: ConflictClass,
        severity: float,
    ) -> bool:
        if conflict_class == ConflictClass.SACRED_COLLISION:
            return True
        if AuthorityLevel.CANONICAL in {left.authority_level, right.authority_level}:
            return True
        return severity >= 0.8

    def suggest_resolution(self, new_entry: MemoryEntry, existing: MemoryEntry) -> str:
        if new_entry.authority_level > existing.authority_level:
            return "ALLOW_NEW_TO_SUPERSEDE_ONLY_IF_SAME_SLOT_AND_GOVERNANCE_PASSES"
        if existing.authority_level > new_entry.authority_level:
            return "KEEP_EXISTING_PRIMARY_REVIEW_NEW"
        if new_entry.review_status == ReviewStatus.CONFIRMED and existing.review_status != ReviewStatus.CONFIRMED:
            return "PREFER_CONFIRMED_REVIEW_EXISTING"
        return "MANUAL_REVIEW_REQUIRED"
