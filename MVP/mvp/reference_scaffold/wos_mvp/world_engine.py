from __future__ import annotations
from dataclasses import dataclass, field
from datetime import UTC, datetime

from .consciousness_layer import ConsciousnessLayer
from .emotional_layer import EmotionalLayer
from .enums import AssertionMode, AuthorityLevel, DomainType, ReviewStatus
from .governance import GovernanceEngine
from .index_lifecycle import IndexLifecycleManager
from .npc_simulation import NPCSimulationEngine
from .records import (
    ConsciousnessState,
    EmotionalSignals,
    EmotionalState,
    MemoryEntry,
    PartitionKey,
    QueryContext,
    StoryHealthVector,
    TemporalValidityWindow,
    TurnResult,
)
from .relevance import RelevanceScorer
from .retrieval import RetrievalPlanner

@dataclass
class WorldEngine:
    partition_key: PartitionKey
    entries: list[MemoryEntry] = field(default_factory=list)
    governance: GovernanceEngine = field(default_factory=GovernanceEngine)

    def __post_init__(self) -> None:
        self.index_manager = IndexLifecycleManager()
        self.scorer = RelevanceScorer()
        self.retrieval = RetrievalPlanner(self.entries, self.scorer, self.index_manager)
        self.emotional_layer = EmotionalLayer()
        self.consciousness_layer = ConsciousnessLayer()
        self.npc_engine = NPCSimulationEngine()
        self.emotional_state = EmotionalState()
        self.health_vector = StoryHealthVector()
        self.turn_number = 0

    def seed(self, entries: list[MemoryEntry]) -> None:
        self.entries[:] = entries
        self.index_manager.rebuild(entries, self.partition_key)
        self.retrieval.entries = self.entries

    def execute_turn(self, player_input: str) -> TurnResult:
        self.turn_number += 1
        signals = EmotionalSignals(input_text=player_input, response_time_seconds=45, repeated_failure_count=0, scene_energy=0.5)
        self.emotional_state = self.emotional_layer.update(self.emotional_state, signals)
        emotional_constraints = self.emotional_layer.constraints(self.emotional_state)
        directive = self.consciousness_layer.choose_strategy(
            ConsciousnessState(vector=self.health_vector, player_support_pressure=self.emotional_state.support_need)
        )
        context = QueryContext(task_tags={"investigation", "money_trail"}, turn_number=self.turn_number, partition_key=self.partition_key)
        retrieved = self.retrieval.retrieve_for_runtime_question(player_input, context)

        npcs = []
        npc_actions = self.npc_engine.simulate_turn(self.turn_number, npcs, self.health_vector.world_pressure)

        output = self._compose_output(player_input, directive.strategy, emotional_constraints.support_action, retrieved)
        self.governance.log("runtime", "turn_executed", turn=self.turn_number, strategy=directive.strategy, support=emotional_constraints.support_action)

        new_entry = MemoryEntry(
            record_id=f"turn::{self.turn_number}",
            partition_key=self.partition_key,
            domain_type=DomainType.EPISODIC,
            assertion_mode=AssertionMode.CANONICAL_ASSERTION,
            authority_level=AuthorityLevel.CONFIRMED,
            review_status=ReviewStatus.CONFIRMED,
            carrier_scope="session",
            entity_id="session",
            field_name="turn_output",
            slot_key=f"session::canonical::turn_output::turn_{self.turn_number}::session",
            content=output,
            normalized_value=output.lower(),
            source_lineage=[f"turn:{self.turn_number}"],
            temporal_validity=TemporalValidityWindow(self.turn_number),
            created_at=datetime.now(UTC),
            last_accessed=datetime.now(UTC),
            task_tags={"investigation"},
            metadata={"fresh": True},
        )
        self.entries.append(new_entry)
        self.index_manager.rebuild(self.entries, self.partition_key)
        return TurnResult(
            turn_number=self.turn_number,
            strategy=directive.strategy,
            support_action=emotional_constraints.support_action,
            text_output=output,
            retrieved_memory_ids=[c.entry.record_id for c in retrieved],
            npc_actions=npc_actions,
        )

    def _compose_output(self, player_input: str, strategy: str, support_action: str, retrieved: list) -> str:
        if support_action == "offer_hint_and_recap":
            return "You have three anchors: money, Vera, and Marcus. The next useful move is to ask how the accounts connect."
        if "money" in player_input.lower():
            return "The money trail narrows around Vera Chen. Too neat to be innocent, too careful to be simple."
        return f"[{strategy}] The scene advances. Relevant memory count: {len(retrieved)}."
