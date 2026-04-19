from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .enums import (
    AssertionMode,
    AuthorityLevel,
    ConflictClass,
    DomainType,
    EffectSurface,
    NPCSimulationMode,
    RetrievalTaskProfile,
    ReviewStatus,
    TemporalState,
)

@dataclass(frozen=True)
class PartitionKey:
    world_id: str
    module_id: str
    session_id: str
    player_id: str = "default_player"
    actor_scope: str = "global"
    agent_role: str = "runtime"
    visibility_class: str = "default"

    def world_module(self) -> tuple[str, str]:
        return (self.world_id, self.module_id)

@dataclass
class TemporalValidityWindow:
    valid_from_turn: int
    valid_to_turn: Optional[int] = None
    temporal_state: TemporalState = TemporalState.ACTIVE
    superseded_at_turn: Optional[int] = None

    def overlaps(self, other: "TemporalValidityWindow") -> bool:
        left_end = self.valid_to_turn if self.valid_to_turn is not None else float("inf")
        right_end = other.valid_to_turn if other.valid_to_turn is not None else float("inf")
        return self.valid_from_turn <= right_end and other.valid_from_turn <= left_end

    def covers(self, turn: int) -> bool:
        if turn < self.valid_from_turn:
            return False
        if self.valid_to_turn is not None and turn > self.valid_to_turn:
            return False
        return self.temporal_state not in {TemporalState.DEPRECATED}

@dataclass
class MemoryProvenance:
    source_type: str
    source_id: str
    created_at: datetime
    confirmed_by: list[str] = field(default_factory=list)
    confirmation_turns: list[int] = field(default_factory=list)
    confidence_history: list[tuple[datetime, float]] = field(default_factory=list)
    replaced_entries: list[str] = field(default_factory=list)
    replaced_at: Optional[datetime] = None
    replacement_reason: Optional[str] = None
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    derived_from: Optional[str] = None
    children: list[str] = field(default_factory=list)

@dataclass
class MemoryEntry:
    record_id: str
    partition_key: PartitionKey
    domain_type: DomainType
    assertion_mode: AssertionMode
    authority_level: AuthorityLevel
    review_status: ReviewStatus
    carrier_scope: str
    entity_id: str
    field_name: str
    slot_key: str
    content: Any
    normalized_value: str
    source_lineage: list[str]
    temporal_validity: TemporalValidityWindow
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    task_tags: set[str] = field(default_factory=set)
    conflict_risk: float = 0.0
    superseded_by: Optional[str] = None
    confidence: float = 1.0
    effect_surfaces: list[EffectSurface] = field(default_factory=list)
    primary_surface: Optional[EffectSurface] = None
    temporal_weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    provenance: Optional[MemoryProvenance] = None

@dataclass
class ConflictRecord:
    conflict_id: str
    conflict_class: ConflictClass
    involved_record_ids: list[str]
    same_slot_decision: bool
    severity: float
    suggested_resolution: str
    human_review_required: bool
    closure_state: str = "open"
    notes: list[str] = field(default_factory=list)

@dataclass
class RetrievalCandidate:
    entry: MemoryEntry
    lexical_score: float = 0.0
    semantic_score: float = 0.0
    relevance_score: float = 0.0
    final_score: float = 0.0

@dataclass
class QueryContext:
    task_tags: set[str]
    turn_number: int
    partition_key: PartitionKey
    task_profile: RetrievalTaskProfile = RetrievalTaskProfile.RUNTIME_QUESTION

@dataclass
class ThresholdInput:
    repetition_count: int = 0
    emotional_charge: float = 0.0
    carrier_count: int = 0
    ritualization_count: int = 0
    symbolic_density: float = 0.0
    collective_binding: float = 0.0
    debunking_pressure: float = 0.0
    fragmentation_pressure: float = 0.0

@dataclass
class EffectActivationResult:
    primary_surface: EffectSurface
    secondary_surfaces: list[EffectSurface]
    latent_surfaces: list[EffectSurface]
    intensity_by_surface: dict[EffectSurface, float]
    blockers_triggered: list[str] = field(default_factory=list)
    escalators_triggered: list[str] = field(default_factory=list)

@dataclass
class TransformationRule:
    from_domain: DomainType
    to_domain: DomainType
    required_carriers: list[str]
    trigger_conditions: list[str]
    amplifiers: list[str]
    blockers: list[str]
    min_score: float
    effect_surfaces: list[EffectSurface]
    reversibility: str = "medium"

@dataclass
class TransformationResult:
    status: str
    score: float
    rule_name: str
    notes: list[str] = field(default_factory=list)

@dataclass
class EmotionalState:
    engagement: float = 0.6
    frustration: float = 0.0
    confusion: float = 0.0
    overload: float = 0.0
    boredom: float = 0.0
    agency: float = 0.8
    support_need: float = 0.0
    pacing_tolerance: float = 0.7
    trust_in_system: float = 0.7

@dataclass
class EmotionalSignals:
    input_text: str
    response_time_seconds: float
    repeated_failure_count: int = 0
    scene_energy: float = 0.5
    choice_count: int = 1

@dataclass
class EmotionalConstraints:
    support_action: str
    target_engagement: float
    max_cognitive_load: float
    pacing_mode: str

@dataclass
class StoryHealthVector:
    story_health: float = 0.7
    mystery_integrity: float = 0.7
    pacing_health: float = 0.7
    callback_debt: float = 0.0
    tonal_integrity: float = 0.8
    world_pressure: float = 0.4

@dataclass
class ConsciousnessState:
    vector: StoryHealthVector
    player_support_pressure: float = 0.0
    degraded_mode_active: bool = False
    branch_risk: float = 0.2

@dataclass
class ConsciousnessDirective:
    strategy: str
    support_bias: float
    tension_bias: float
    explanation: str

@dataclass
class NPCProfile:
    npc_id: str
    importance: int
    goals: list[str]
    last_simulated_turn: int = 0
    mode: NPCSimulationMode = NPCSimulationMode.EVENT_DRIVEN

@dataclass
class NPCAction:
    npc_id: str
    summary: str
    mode_used: NPCSimulationMode
    world_pressure_delta: float = 0.0

@dataclass
class TurnResult:
    turn_number: int
    strategy: str
    support_action: str
    text_output: str
    retrieved_memory_ids: list[str]
    npc_actions: list[NPCAction]
