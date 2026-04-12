"""W2-R2.2: Shared context DTO definitions — cycle-breaking leaf module.

Defines Pydantic BaseModel classes for narrative, relationship, lore, and scene
context types. Importable by all runtime modules without creating cycles.

This module has no orchestration imports (only stdlib, third-party, runtime_models).
"""

from __future__ import annotations

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


# ===== Narrative Thread Types =====


class NarrativeThreadState(BaseModel):
    """Single bounded narrative consequence thread (derived, not authoritative)."""

    thread_id: str
    thread_kind: str
    status: Literal["active", "holding", "escalating", "de_escalating", "resolved"]
    scene_anchor: Optional[str] = None
    related_paths: list[str] = Field(default_factory=list)
    related_characters: list[str] = Field(default_factory=list)
    evidence_consequences: list[str] = Field(default_factory=list)
    intensity: int = Field(default=0, ge=0, le=5)
    persistence_turns: int = Field(default=0, ge=0)
    last_updated_turn: int = 0
    resolution_hint: Optional[str] = None


class NarrativeThreadSet(BaseModel):
    """Bounded set of active threads plus a small resolved-recent window."""

    active: list[NarrativeThreadState] = Field(default_factory=list)
    resolved_recent: list[NarrativeThreadState] = Field(default_factory=list)


# ===== Relationship Context Types =====


class SalientRelationshipAxis(BaseModel):
    """Single salient relationship or connection axis for a character."""

    axis_id: str
    axis_name: str
    participants: list[str] = Field(default_factory=list)
    current_value: float = Field(default=0.5, ge=0.0, le=1.0)
    semantic_notes: str = Field(default="")


class RelationshipAxisContext(BaseModel):
    """Derived relationship context for a character or scene."""

    character_id: str
    salient_axes: list[SalientRelationshipAxis] = Field(default_factory=list)
    conflict_potential: float = Field(default=0.0, ge=0.0, le=1.0)
    harmony_potential: float = Field(default=0.5, ge=0.0, le=1.0)


# ===== Lore Direction Types =====


class ModuleGuidanceUnit(BaseModel):
    """Single piece of narrative guidance from a lore module."""

    unit_id: str
    lore_module_id: str
    guidance_text: str
    priority: int = Field(default=50, ge=0, le=100)
    applicable_domains: list[str] = Field(default_factory=list)


class LoreDirectionContext(BaseModel):
    """Direction and constraints derived from lore modules."""

    scene_id: str
    lore_guidance_units: list[ModuleGuidanceUnit] = Field(default_factory=list)
    thematic_anchors: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


# ===== Scene Presenter Types =====


class RelationshipMovement(BaseModel):
    """Change in a relationship axis during a scene/turn."""

    axis_id: str
    delta: float = Field(..., ge=-1.0, le=1.0)
    driver: str


class CharacterPanelOutput(BaseModel):
    """One character's state snapshot and panel information for a scene."""

    character_id: str
    panel_text: str
    emotional_state: str = Field(default="neutral")
    relationship_movements: list[RelationshipMovement] = Field(default_factory=list)


class ConflictTrendSignal(BaseModel):
    """Signal indicating a trend in conflict escalation or de-escalation."""

    signal_type: Literal["escalation", "de_escalation", "stasis"]
    magnitude: float = Field(ge=0.0, le=1.0)
    driver: str


class ConflictPanelOutput(BaseModel):
    """Conflict state and trend information for a scene panel."""

    panel_id: str
    conflict_active: bool
    active_conflicts: list[str] = Field(default_factory=list)
    trend_signals: list[ConflictTrendSignal] = Field(default_factory=list)
    panel_narrative: str = Field(default="")
