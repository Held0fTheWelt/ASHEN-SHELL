from __future__ import annotations
from enum import Enum, IntEnum

class AuthorityLevel(IntEnum):
    ADVISORY = 1
    INFERRED = 2
    CONFIRMED = 3
    CANONICAL = 4

class ReviewStatus(str, Enum):
    UNCONFIRMED = "unconfirmed"
    CONFIRMED = "confirmed"
    NEEDS_REVIEW = "needs_review"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"
    BLOCKED = "blocked"

class AssertionMode(str, Enum):
    CANONICAL_ASSERTION = "canonical_assertion"
    BELIEF_ASSERTION = "belief_assertion"
    RUMOR_ASSERTION = "rumor_assertion"
    INSTITUTIONAL_CLAIM = "institutional_claim"
    RECONSTRUCTED_CLAIM = "reconstructed_claim"
    SACRED_CLAIM = "sacred_claim"

class DomainType(str, Enum):
    CANONICAL_TRUTH = "canonical_truth_memory"
    EPISODIC = "episodic_experience_memory"
    BELIEF = "belief_memory"
    SOCIAL = "social_memory"
    INSTITUTIONAL = "institutional_memory"
    CULTURAL = "cultural_memory"
    RUMOR = "rumor_memetic_memory"
    LEGEND = "legend_mythic_memory"
    SACRED = "sacred_ritual_memory"
    TRAUMA = "trauma_suppression_memory"
    COUNTER_MEMORY = "counter_memory_research_memory"
    ONTOLOGICAL = "ontological_reality_bearing_memory"
    PROCEDURAL = "procedural_memory"

class EffectSurface(str, Enum):
    BEHAVIOR = "behavior"
    RELATIONAL = "relational"
    SOCIAL_REPUTATION = "social_reputation"
    INSTITUTIONAL_POLICY = "institutional_policy"
    CULTURAL_NORMATIVE = "cultural_normative"
    NARRATIVE_DRAMATIC = "narrative_dramatic"
    OPERATIONAL_TACTICAL = "operational_tactical"
    SPATIAL_ENVIRONMENTAL = "spatial_environmental"
    ARCHIVE_TRUTH_CONTEST = "archive_truth_contest"
    RITUAL_SACRED = "ritual_sacred"
    ONTOLOGICAL = "ontological"

class TemporalState(str, Enum):
    ACTIVE = "active"
    FUTURE_BOUND = "future_bound"
    HISTORICAL = "historical"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"

class ConflictClass(str, Enum):
    SLOT_VALUE_CONTRADICTION = "slot_value_contradiction"
    AUTHORITY_COLLISION = "authority_collision"
    TEMPORAL_OVERLAP_CONTRADICTION = "temporal_overlap_contradiction"
    DOMAIN_TENSION = "domain_tension"
    SACRED_COLLISION = "sacred_collision"
    PARTITION_VIOLATION = "partition_violation"

class RetrievalTaskProfile(str, Enum):
    RUNTIME_QUESTION = "runtime_question"
    DIAGNOSIS = "diagnosis"
    AUDIT = "audit"
    RESEARCH = "research"
    AUTHORING = "authoring"
    WORLD_CONTINUITY = "world_continuity"

class IndexState(str, Enum):
    READY = "ready"
    STALE = "stale"
    BUILDING = "building"
    FAILED = "failed"

class NPCSimulationMode(str, Enum):
    FULL = "full_simulation"
    PERIODIC = "periodic_simulation"
    EVENT_DRIVEN = "event_driven"
