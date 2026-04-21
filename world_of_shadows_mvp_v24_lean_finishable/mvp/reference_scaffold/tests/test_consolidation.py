from wos_mvp.consolidation import MemoryConsolidator

def test_consolidation_creates_semantic_candidate(base_entry) -> None:
    other = base_entry
    other2 = MemoryEntry(**{**base_entry.__dict__, "record_id": "r2"})
    consolidator = MemoryConsolidator()
    result = consolidator.consolidate([other, other2])
    assert result.semantic_candidates
    assert result.semantic_candidates[0].record_id.startswith("semantic::")

from wos_mvp.records import MemoryEntry
