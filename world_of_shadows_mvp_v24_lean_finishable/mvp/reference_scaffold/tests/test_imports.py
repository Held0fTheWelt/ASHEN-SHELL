from wos_mvp import (
    AuthorityLevel,
    ReviewStatus,
    AssertionMode,
    DomainType,
    EffectSurface,
    TemporalState,
    PartitionKey,
    MemoryEntry,
    ConflictRecord,
)

def test_package_imports() -> None:
    assert AuthorityLevel.CANONICAL.value == 4
    assert ReviewStatus.CONFIRMED.value == "confirmed"
    assert AssertionMode.CANONICAL_ASSERTION.value == "canonical_assertion"
    assert DomainType.BELIEF.value.endswith("belief_memory")
    assert EffectSurface.BEHAVIOR.value == "behavior"
    assert TemporalState.ACTIVE.value == "active"
    assert PartitionKey(world_id="w", module_id="m", session_id="s")
    assert MemoryEntry
    assert ConflictRecord
