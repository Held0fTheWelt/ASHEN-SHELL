from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.content.models import ExperienceKind, JoinPolicy, ParticipantMode


class RunStatus(str, Enum):
    LOBBY = "lobby"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class ParticipantState(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    display_name: str
    role_id: str
    mode: ParticipantMode
    current_room_id: str
    connected: bool = False
    account_id: str | None = None
    character_id: str | None = None
    seat_owner_account_id: str | None = None
    seat_owner_display_name: str | None = None
    seat_owner: str | None = None
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if self.seat_owner_account_id is None and self.account_id is not None:
            if self.seat_owner == self.account_id or self.seat_owner is None:
                self.seat_owner_account_id = self.account_id
        if self.seat_owner_display_name is None:
            if self.seat_owner and self.seat_owner != self.account_id:
                self.seat_owner_display_name = self.seat_owner
            elif self.mode == ParticipantMode.HUMAN:
                self.seat_owner_display_name = self.display_name
        if self.seat_owner is None:
            self.seat_owner = self.seat_owner_account_id or self.seat_owner_display_name


class LobbySeatState(BaseModel):
    role_id: str
    role_display_name: str
    reserved_for_account_id: str | None = None
    reserved_for_display_name: str | None = None
    participant_id: str | None = None
    occupant_display_name: str | None = None
    connected: bool = False
    ready: bool = False
    joined_at: datetime | None = None


class PropState(BaseModel):
    id: str
    name: str
    room_id: str
    description: str
    state: str = "default"


class TranscriptEntry(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    kind: str
    actor: str | None = None
    text: str
    room_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class RuntimeEvent(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type: str
    run_id: str
    payload: dict[str, Any]


class RuntimeInstance(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    template_id: str
    template_title: str
    kind: ExperienceKind
    join_policy: JoinPolicy
    owner_player_name: str | None = None
    owner_account_id: str | None = None
    owner_character_id: str | None = None
    status: RunStatus = RunStatus.LOBBY
    beat_id: str
    tension: int = 0
    flags: set[str] = Field(default_factory=set)
    participants: dict[str, ParticipantState] = Field(default_factory=dict)
    lobby_seats: dict[str, LobbySeatState] = Field(default_factory=dict)
    props: dict[str, PropState] = Field(default_factory=dict)
    transcript: list[TranscriptEntry] = Field(default_factory=list)
    event_log: list[RuntimeEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    persistent: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class PublicRunSummary(BaseModel):
    id: str
    template_id: str
    template_title: str
    kind: ExperienceKind
    join_policy: JoinPolicy
    persistent: bool
    status: RunStatus
    connected_humans: int
    total_humans: int
    open_human_seats: int = 0
    ready_human_seats: int = 0
    tension: int
    beat_id: str
    owner_player_name: str | None = None


class RuntimeSnapshot(BaseModel):
    run_id: str
    template_id: str
    template_title: str
    kind: ExperienceKind
    join_policy: JoinPolicy
    status: RunStatus
    beat_id: str
    tension: int
    flags: list[str] = Field(default_factory=list)
    viewer_participant_id: str
    viewer_account_id: str | None = None
    viewer_character_id: str | None = None
    viewer_room_id: str
    viewer_role_id: str
    viewer_display_name: str
    current_room: dict[str, Any] | None = None
    visible_occupants: list[dict[str, Any]] = Field(default_factory=list)
    rooms: list[dict[str, Any]] = Field(default_factory=list)
    room_occupants: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    available_actions: list[dict[str, Any]]
    transcript_tail: list[TranscriptEntry]
    lobby: dict[str, Any] | None = None
    metadata: dict[str, Any]


class CommandResult(BaseModel):
    accepted: bool
    reason: str | None = None
    events: list[RuntimeEvent] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# MVP2: Runtime State, Story Session State, Actor Lane Context
# ---------------------------------------------------------------------------

class ActorLaneContext(BaseModel):
    """Actor lane assignment context. Built from MVP1 build_actor_ownership() output.

    human_actor_id is the selected player's canonical actor. AI is forbidden
    from generating lines, actions, emotions, or decisions for this actor.
    ai_allowed_actor_ids contains only NPC actors.
    """

    contract: str = "actor_lane_context.v1"
    content_module_id: str
    runtime_profile_id: str
    selected_player_role: str
    human_actor_id: str
    actor_lanes: dict[str, str]  # actor_id -> "human" | "npc"
    ai_allowed_actor_ids: list[str]
    ai_forbidden_actor_ids: list[str]

    def is_human_actor(self, actor_id: str) -> bool:
        return actor_id == self.human_actor_id

    def is_npc_actor(self, actor_id: str) -> bool:
        return self.actor_lanes.get(actor_id) == "npc"

    def is_ai_forbidden(self, actor_id: str) -> bool:
        return actor_id in self.ai_forbidden_actor_ids


class RuntimeState(BaseModel):
    """Runtime state with source provenance. Consumed by MVP3 LDSS."""

    contract: str = "runtime_state.v1"
    state_version: str = "runtime_state.goc_solo.v1"
    story_session_id: str
    run_id: str
    content_module_id: str
    content_hash: str
    runtime_profile_id: str
    runtime_profile_hash: str
    runtime_module_id: str
    runtime_module_hash: str
    current_scene_id: str
    selected_player_role: str
    human_actor_id: str
    actor_lanes: dict[str, str]
    admitted_objects: list[str] = Field(default_factory=list)


class StorySessionState(BaseModel):
    """Story session state tracking turn number, scene, and ownership. Consumed by MVP3."""

    contract: str = "story_session_state.v1"
    story_session_id: str
    run_id: str
    turn_number: int = 0
    content_module_id: str
    runtime_profile_id: str
    runtime_module_id: str
    current_scene_id: str
    selected_player_role: str
    human_actor_id: str
    npc_actor_ids: list[str]
    visitor_present: bool = False


class ActorLaneValidationResult(BaseModel):
    """Result of actor lane validation at the AI candidate output seam."""

    contract: str = "actor_lane_validation_result.v1"
    status: str  # "approved" | "rejected"
    error_code: str | None = None
    actor_id: str | None = None
    block_kind: str | None = None
    human_actor_id: str | None = None
    message: str | None = None


# ---------------------------------------------------------------------------
# MVP2 Wave 2.3: StateDeltaBoundary
# ---------------------------------------------------------------------------

class StateDeltaBoundary(BaseModel):
    """Protected path enforcement for runtime state deltas.

    Mutations to protected_paths are always rejected. Mutations to unknown
    paths are rejected when reject_unknown_paths=True.
    """

    contract: str = "state_delta_boundary.v1"
    protected_paths: list[str] = Field(default_factory=lambda: [
        "canonical_scene_order",
        "canonical_characters",
        "canonical_relationships",
        "canonical_content_truth",
        "canonical_props",
        "canonical_endings",
        "content_module_id",
        "selected_player_role",
        "human_actor_id",
        "actor_lanes",
    ])
    allowed_runtime_paths: list[str] = Field(default_factory=lambda: [
        "runtime_flags",
        "turn_memory",
        "scene_pressure",
        "admitted_objects",
        "relationship_runtime_pressure",
    ])
    reject_unknown_paths: bool = True


class StateDeltaValidationResult(BaseModel):
    """Result of a state delta boundary validation."""

    contract: str = "state_delta_validation_result.v1"
    status: str  # "approved" | "rejected"
    error_code: str | None = None
    path: str | None = None
    operation: str | None = None
    message: str | None = None


# ---------------------------------------------------------------------------
# MVP2 Wave 2.4: Object Admission
# ---------------------------------------------------------------------------

VALID_SOURCE_KINDS: frozenset[str] = frozenset({
    "canonical_content",
    "typical_minor_implied",
    "similar_allowed",
})


class ObjectAdmissionRecord(BaseModel):
    """Admission record for a runtime environment object.

    source_kind must be one of: canonical_content, typical_minor_implied, similar_allowed.
    similar_allowed requires a non-empty similarity_reason.
    typical_minor_implied objects are staged temporarily and not committed.
    canonical_content objects may be committed when canonical content allows it.
    """

    contract: str = "object_admission_record.v1"
    object_id: str
    source_kind: str | None = None
    source_reference: str | None = None
    admission_reason: str | None = None
    similarity_reason: str | None = None
    temporary_scene_staging: bool = False
    commit_allowed: bool = False
    status: str = "pending"  # "admitted" | "rejected"
    error_code: str | None = None
    message: str | None = None
