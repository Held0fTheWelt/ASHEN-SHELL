from __future__ import annotations
from .enums import ReviewStatus, TemporalState
from .records import MemoryEntry

class TemporalMemoryManager:
    def classify_temporal_state(self, entry: MemoryEntry, current_turn: int) -> TemporalState:
        if entry.review_status == ReviewStatus.SUPERSEDED:
            return TemporalState.SUPERSEDED
        if entry.review_status == ReviewStatus.DEPRECATED:
            return TemporalState.DEPRECATED
        if current_turn < entry.temporal_validity.valid_from_turn:
            return TemporalState.FUTURE_BOUND
        if entry.temporal_validity.valid_to_turn is not None and current_turn > entry.temporal_validity.valid_to_turn:
            return TemporalState.HISTORICAL
        return TemporalState.ACTIVE

    def apply_temporal_decay(self, entries: list[MemoryEntry], current_turn: int) -> None:
        for entry in entries:
            state = self.classify_temporal_state(entry, current_turn)
            if state == TemporalState.ACTIVE:
                entry.temporal_weight = 1.0
            elif state == TemporalState.HISTORICAL:
                entry.temporal_weight = 0.6
            elif state == TemporalState.FUTURE_BOUND:
                entry.temporal_weight = 0.4
            elif state == TemporalState.SUPERSEDED:
                entry.temporal_weight = 0.1
            else:
                entry.temporal_weight = 0.0

    def mark_as_superseded(self, old_entry: MemoryEntry, new_entry: MemoryEntry, reason: str, at_turn: int) -> None:
        old_entry.review_status = ReviewStatus.SUPERSEDED
        old_entry.superseded_by = new_entry.record_id
        old_entry.temporal_validity.temporal_state = TemporalState.SUPERSEDED
        old_entry.temporal_validity.superseded_at_turn = at_turn
        old_entry.metadata["supersession_reason"] = reason
