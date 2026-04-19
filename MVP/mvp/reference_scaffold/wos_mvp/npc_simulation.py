from __future__ import annotations
from dataclasses import dataclass

from .enums import NPCSimulationMode
from .records import NPCAction, NPCProfile

@dataclass
class NPCSimulationEngine:
    budget_per_turn_ms: int = 500
    max_full_npcs_per_turn: int = 3
    periodic_cadence: int = 5

    def simulate_turn(self, turn_number: int, npcs: list[NPCProfile], world_pressure: float) -> list[NPCAction]:
        actions: list[NPCAction] = []
        full_candidates = sorted([n for n in npcs if n.importance >= 8], key=lambda n: n.importance, reverse=True)[: self.max_full_npcs_per_turn]
        for npc in full_candidates:
            npc.mode = NPCSimulationMode.FULL
            npc.last_simulated_turn = turn_number
            actions.append(NPCAction(npc_id=npc.npc_id, summary=f"{npc.npc_id} advances goal under pressure {world_pressure:.2f}", mode_used=npc.mode, world_pressure_delta=0.05))
        for npc in npcs:
            if npc in full_candidates:
                continue
            if turn_number - npc.last_simulated_turn >= self.periodic_cadence:
                npc.mode = NPCSimulationMode.PERIODIC
                npc.last_simulated_turn = turn_number
                actions.append(NPCAction(npc_id=npc.npc_id, summary=f"{npc.npc_id} updates off-screen state", mode_used=npc.mode, world_pressure_delta=0.01))
            else:
                npc.mode = NPCSimulationMode.EVENT_DRIVEN
        return actions
