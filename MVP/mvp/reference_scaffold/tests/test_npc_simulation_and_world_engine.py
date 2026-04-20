from wos_mvp.npc_simulation import NPCSimulationEngine
from wos_mvp.records import NPCProfile
from wos_mvp.runtime_demo import build_demo_engine

def test_npc_simulation_budget_modes() -> None:
    engine = NPCSimulationEngine()
    npcs = [
        NPCProfile("vera", importance=10, goals=["protect secret"]),
        NPCProfile("marcus", importance=9, goals=["avoid capture"]),
        NPCProfile("porter", importance=4, goals=["keep watch"]),
    ]
    actions = engine.simulate_turn(1, npcs, world_pressure=0.4)
    assert any(a.npc_id == "vera" for a in actions)

def test_world_engine_executes_turn() -> None:
    engine = build_demo_engine()
    result = engine.execute_turn("I want to find out about the money.")
    assert result.turn_number == 1
    assert result.text_output
