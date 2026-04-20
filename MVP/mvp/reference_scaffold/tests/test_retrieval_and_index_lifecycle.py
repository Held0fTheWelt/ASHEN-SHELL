from wos_mvp.enums import IndexState, RetrievalTaskProfile
from wos_mvp.index_lifecycle import IndexLifecycleManager
from wos_mvp.records import QueryContext
from wos_mvp.relevance import RelevanceScorer
from wos_mvp.retrieval import RetrievalPlanner

def test_retrieval_respects_partition_and_index(base_entry, partition_key) -> None:
    manager = IndexLifecycleManager()
    manager.rebuild([base_entry], partition_key)
    planner = RetrievalPlanner([base_entry], RelevanceScorer(now_provider=lambda: base_entry.last_accessed), manager)
    ctx = QueryContext(task_tags={"money_trail"}, turn_number=2, partition_key=partition_key)
    results = planner.retrieve_for_runtime_question("money trail", ctx)
    assert results
    assert results[0].entry.record_id == "r1"

def test_audit_profile_blocks_on_failed_index(base_entry, partition_key) -> None:
    manager = IndexLifecycleManager()
    manager.rebuild([base_entry], partition_key)
    manager.set_state(partition_key, IndexState.FAILED)
    planner = RetrievalPlanner([base_entry], RelevanceScorer(now_provider=lambda: base_entry.last_accessed), manager)
    ctx = QueryContext(task_tags={"money_trail"}, turn_number=2, partition_key=partition_key, task_profile=RetrievalTaskProfile.AUDIT)
    import pytest
    with pytest.raises(RuntimeError):
        planner.retrieve_for_audit("money trail", ctx)
