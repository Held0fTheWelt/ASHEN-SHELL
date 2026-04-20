from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
# UTC compatibility for Python 3.10
UTC = timezone.utc

from .enums import IndexState
from .records import MemoryEntry, PartitionKey

def _tokenize(text: str) -> list[str]:
    return [tok for tok in text.lower().replace("_", " ").split() if tok]

@dataclass
class LexicalIndexSnapshot:
    partition: tuple[str, str]
    generation: int
    created_at: datetime
    state: IndexState
    inverted_index: dict[str, set[str]] = field(default_factory=dict)

class IndexLifecycleManager:
    def __init__(self) -> None:
        self.snapshots: dict[tuple[str, str], LexicalIndexSnapshot] = {}
        self.entries_by_id: dict[str, MemoryEntry] = {}

    def rebuild(self, entries: list[MemoryEntry], partition_key: PartitionKey, state: IndexState = IndexState.READY) -> LexicalIndexSnapshot:
        partition = partition_key.world_module()
        generation = self.snapshots[partition].generation + 1 if partition in self.snapshots else 1
        inverted: dict[str, set[str]] = {}
        for entry in entries:
            if entry.partition_key.world_module() != partition:
                continue
            self.entries_by_id[entry.record_id] = entry
            for token in _tokenize(entry.normalized_value):
                inverted.setdefault(token, set()).add(entry.record_id)
        snapshot = LexicalIndexSnapshot(partition=partition, generation=generation, created_at=datetime.now(UTC), state=state, inverted_index=inverted)
        self.snapshots[partition] = snapshot
        return snapshot

    def set_state(self, partition_key: PartitionKey, state: IndexState) -> None:
        partition = partition_key.world_module()
        if partition in self.snapshots:
            self.snapshots[partition].state = state

    def search(self, query: str, partition_key: PartitionKey) -> list[tuple[MemoryEntry, float]]:
        partition = partition_key.world_module()
        snapshot = self.snapshots.get(partition)
        if snapshot is None:
            return []
        scores: dict[str, float] = {}
        for token in _tokenize(query):
            for record_id in snapshot.inverted_index.get(token, set()):
                scores[record_id] = scores.get(record_id, 0.0) + 1.0
        ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return [(self.entries_by_id[rid], score / max(len(_tokenize(query)), 1)) for rid, score in ordered]

    def state_for(self, partition_key: PartitionKey) -> IndexState:
        snapshot = self.snapshots.get(partition_key.world_module())
        return snapshot.state if snapshot else IndexState.FAILED
