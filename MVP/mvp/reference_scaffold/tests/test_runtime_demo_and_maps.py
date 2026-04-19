from wos_mvp import DomainType
from wos_mvp.maps import (
    MEMORY_DOMAIN_FRAMEWORK,
    MEMORY_INTERACTION_LAWS,
    MEMORY_TRANSFORMATION_MAP,
    MEMORY_CARRIER_MAP,
    MEMORY_EFFECT_SURFACE_MAP,
    MEMORY_CONFLICT_MAP,
    MEMORY_THRESHOLD_MAP,
    MEMORY_GOVERNANCE_MAP,
)
from wos_mvp.runtime_demo import build_demo_engine

def test_maps_operationalized() -> None:
    assert DomainType.CANONICAL_TRUTH.value in MEMORY_DOMAIN_FRAMEWORK
    assert "truth_stays_truth" in MEMORY_INTERACTION_LAWS
    assert MEMORY_TRANSFORMATION_MAP
    assert MEMORY_CARRIER_MAP
    assert MEMORY_EFFECT_SURFACE_MAP
    assert MEMORY_CONFLICT_MAP
    assert MEMORY_THRESHOLD_MAP
    assert MEMORY_GOVERNANCE_MAP

def test_runtime_demo_runs_multiple_turns() -> None:
    engine = build_demo_engine()
    r1 = engine.execute_turn("I want to find out about the money.")
    r2 = engine.execute_turn("I'm confused about the timeline.")
    assert r1.turn_number == 1
    assert r2.turn_number == 2
    assert len(engine.entries) >= 3
