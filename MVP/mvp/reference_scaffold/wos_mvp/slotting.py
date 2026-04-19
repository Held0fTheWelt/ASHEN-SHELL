from __future__ import annotations
from dataclasses import dataclass

from .identity import EntityIdentityResolver
from .records import MemoryEntry

@dataclass(frozen=True)
class FactSlotKey:
    entity_id: str
    assertion_scope: str
    field_name: str
    temporal_bucket: str
    carrier_scope: str

    def as_string(self) -> str:
        return "::".join([
            self.entity_id,
            self.assertion_scope,
            self.field_name,
            self.temporal_bucket,
            self.carrier_scope,
        ])

class AssertionSlotResolver:
    def __init__(self, identity_resolver: EntityIdentityResolver | None = None) -> None:
        self.identity_resolver = identity_resolver or EntityIdentityResolver()

    def make_slot_key(
        self,
        entity_id: str,
        assertion_scope: str,
        field_name: str,
        temporal_bucket: str,
        carrier_scope: str,
    ) -> str:
        canonical_entity = self.identity_resolver.canonicalize(entity_id)
        return FactSlotKey(canonical_entity, assertion_scope, field_name, temporal_bucket, carrier_scope).as_string()

    def same_slot(self, left: MemoryEntry, right: MemoryEntry) -> bool:
        same_partition = left.partition_key.world_module() == right.partition_key.world_module()
        return same_partition and left.slot_key == right.slot_key
