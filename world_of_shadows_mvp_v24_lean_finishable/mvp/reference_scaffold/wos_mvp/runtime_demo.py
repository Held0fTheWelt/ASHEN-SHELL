from __future__ import annotations
from datetime import UTC, datetime

from .enums import AssertionMode, AuthorityLevel, DomainType, ReviewStatus
from .records import MemoryEntry, PartitionKey, TemporalValidityWindow
from .world_engine import WorldEngine

def build_demo_engine(*, session_id: str = "demo", module_id: str = "vera_investigation") -> WorldEngine:
    pk = PartitionKey(world_id="wos", module_id=module_id, session_id=session_id)
    now = datetime.now(UTC)
    seed_entries = [
        MemoryEntry(
            record_id="opening_money",
            partition_key=pk,
            domain_type=DomainType.EPISODIC,
            assertion_mode=AssertionMode.CANONICAL_ASSERTION,
            authority_level=AuthorityLevel.CONFIRMED,
            review_status=ReviewStatus.CONFIRMED,
            carrier_scope="session",
            entity_id="vera_chen",
            field_name="money_trail",
            slot_key="vera_chen::canonical::money_trail::opening::session",
            content="Missing money trail points to Vera Chen.",
            normalized_value="missing money trail points to vera chen",
            source_lineage=["commit:opening"],
            temporal_validity=TemporalValidityWindow(0),
            created_at=now,
            last_accessed=now,
            access_count=3,
            task_tags={"investigation", "money_trail"},
            metadata={"fresh": True},
        )
    ]
    engine = WorldEngine(partition_key=pk)
    engine.seed(seed_entries)
    return engine

def main() -> None:
    engine = build_demo_engine()
    for text in [
        "I want to find out about the money.",
        "I'm confused about the timeline.",
        "I search the desk.",
    ]:
        result = engine.execute_turn(text)
        print(f"TURN {result.turn_number} | strategy={result.strategy} | support={result.support_action}")
        print(result.text_output)
        print(f"retrieved={result.retrieved_memory_ids}")
        print("---")

if __name__ == "__main__":
    main()
