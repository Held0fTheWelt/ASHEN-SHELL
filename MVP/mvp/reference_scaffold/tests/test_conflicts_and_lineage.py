from datetime import datetime

from wos_mvp.conflicts import ConflictDetector
from wos_mvp.enums import AssertionMode, AuthorityLevel, ConflictClass, DomainType, ReviewStatus
from wos_mvp.lineage import LineageGraph
from wos_mvp.records import MemoryEntry, TemporalValidityWindow
from wos_mvp.slotting import AssertionSlotResolver

def test_conflict_detects_same_slot_contradiction(base_entry: MemoryEntry) -> None:
    other = MemoryEntry(
        **{
            **base_entry.__dict__,
            "record_id": "r2",
            "normalized_value": "money trail points away from vera chen",
            "content": "Money trail points away from Vera Chen.",
        }
    )
    detector = ConflictDetector(AssertionSlotResolver())
    conflicts = detector.detect(other, [base_entry])
    assert len(conflicts) == 1
    assert conflicts[0].conflict_class == ConflictClass.SLOT_VALUE_CONTRADICTION

def test_sacred_conflict_requires_human_review(base_entry: MemoryEntry) -> None:
    sacred = MemoryEntry(
        **{
            **base_entry.__dict__,
            "record_id": "s1",
            "domain_type": DomainType.SACRED,
            "assertion_mode": AssertionMode.SACRED_CLAIM,
            "authority_level": AuthorityLevel.CANONICAL,
            "normalized_value": "sacred truth differs",
        }
    )
    detector = ConflictDetector(AssertionSlotResolver())
    conflict = detector.detect(sacred, [base_entry])[0]
    assert conflict.conflict_class == ConflictClass.SACRED_COLLISION
    assert conflict.human_review_required is True

def test_lineage_graph_traces() -> None:
    graph = LineageGraph()
    graph.add_edge("a", "derived_from", "b")
    graph.add_edge("b", "supported_by", "c")
    assert graph.successors("a") == [("derived_from", "b")]
    assert "a" in graph.trace_upstream("c")
