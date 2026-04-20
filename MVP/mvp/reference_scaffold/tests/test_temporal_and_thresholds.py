from wos_mvp.enums import ReviewStatus, TemporalState
from wos_mvp.records import ThresholdInput
from wos_mvp.temporal import TemporalMemoryManager
from wos_mvp.thresholds import ThresholdEngine

def test_superseded_checked_before_freshness(base_entry) -> None:
    manager = TemporalMemoryManager()
    base_entry.review_status = ReviewStatus.SUPERSEDED
    assert manager.classify_temporal_state(base_entry, current_turn=2) == TemporalState.SUPERSEDED

def test_threshold_paths() -> None:
    engine = ThresholdEngine()
    status, score = engine.rumor_to_legend(ThresholdInput(repetition_count=5, emotional_charge=0.8, carrier_count=5, symbolic_density=0.8, collective_binding=0.8))
    assert status in {"candidate", "active_threshold_met"}
    assert 0.0 <= score <= 1.0
