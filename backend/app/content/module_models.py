"""
Pydantic models for content module structure.

These models define the schema for content modules like "God of Carnage",
providing structure for characters, relationships, triggers, scene phases,
and narrative flow.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ModuleMetadata(BaseModel):
    """Metadata about a content module.

    Attributes:
        module_id: Unique identifier for the module
        title: Human-readable title of the module
        version: Module version (semantic versioning)
        contract_version: Version of the content module contract/schema
        content: Free-form description of module content
        files: Mapping of file identifiers to file paths/references
    """

    module_id: str = Field(..., description="Unique module identifier")
    title: str = Field(..., description="Module title")
    version: str = Field(..., description="Module version (e.g., 1.0.0)")
    contract_version: str = Field(..., description="Content module contract version")
    content: str = Field(default="", description="Module content description")
    files: dict[str, Any] = Field(default_factory=dict, description="Module files mapping")


class CharacterDefinition(BaseModel):
    """Definition of a character in a module.

    Attributes:
        id: Unique identifier for the character
        name: Character name
        role: Character's role in the module (e.g., "protagonist", "antagonist")
        baseline_attitude: Initial attitude/demeanor
        extras: Module-specific character attributes (flexible)
    """

    id: str = Field(..., description="Character identifier")
    name: str = Field(..., description="Character name")
    role: str = Field(..., description="Character role in module")
    baseline_attitude: str = Field(..., description="Initial character attitude")
    extras: dict[str, Any] = Field(default_factory=dict, description="Module-specific attributes")


class RelationshipAxis(BaseModel):
    """Definition of a relationship axis between characters.

    Attributes:
        id: Unique identifier for the axis
        name: Axis name (e.g., "dominance", "affection")
        description: Description of what this axis represents
        relationships: Mapping of character pair to relationship state
        baseline: Initial state of the axis
        escalation: How the axis escalates under tension
    """

    id: str = Field(..., description="Axis identifier")
    name: str = Field(..., description="Axis name")
    description: str = Field(..., description="Axis description")
    relationships: dict[str, Any] = Field(default_factory=dict, description="Character relationship states")
    baseline: str | float = Field(..., description="Baseline axis state")
    escalation: dict[str, Any] = Field(default_factory=dict, description="Escalation rules")


class TriggerDefinition(BaseModel):
    """Definition of a trigger event in a module.

    Attributes:
        id: Unique identifier for the trigger
        name: Trigger name
        description: What activates this trigger
        recognition_markers: Signs that indicate trigger activation
        escalation_impact: How this trigger escalates conflict
        active_in_phases: Which scene phases this trigger is active
        character_vulnerability: Character vulnerabilities to this trigger
    """

    id: str = Field(..., description="Trigger identifier")
    name: str = Field(..., description="Trigger name")
    description: str = Field(..., description="Trigger description")
    recognition_markers: list[str] = Field(default_factory=list, description="Markers for trigger recognition")
    escalation_impact: dict[str, Any] = Field(default_factory=dict, description="How this escalates conflict")
    active_in_phases: list[str] = Field(default_factory=list, description="Phase IDs where trigger is active")
    character_vulnerability: dict[str, Any] = Field(default_factory=dict, description="Character vulnerabilities")


class ScenePhase(BaseModel):
    """Definition of a scene phase in module progression.

    Attributes:
        id: Unique identifier for the phase
        name: Phase name
        sequence: Order in which phase occurs (must be positive)
        description: Phase description
        content_focus: What aspects are focused on in this phase
        engine_tasks: Tasks for the narrative engine
        active_triggers: Trigger IDs active in this phase
        enforced_constraints: Constraints active in this phase
    """

    id: str = Field(..., description="Phase identifier")
    name: str = Field(..., description="Phase name")
    sequence: int = Field(..., description="Phase sequence order", gt=0)
    description: str = Field(..., description="Phase description")
    content_focus: str = Field(default="", description="Content focus for this phase")
    engine_tasks: list[str] = Field(default_factory=list, description="Engine tasks to execute")
    active_triggers: list[str] = Field(default_factory=list, description="Active trigger IDs")
    enforced_constraints: dict[str, Any] = Field(default_factory=dict, description="Phase constraints")

    @field_validator("sequence")
    @classmethod
    def validate_sequence(cls, v: int) -> int:
        """Ensure sequence is a positive integer."""
        if v <= 0:
            raise ValueError("sequence must be a positive integer")
        return v


class PhaseTransition(BaseModel):
    """Definition of transitions between scene phases.

    Attributes:
        from_phase: Source phase ID
        to_phase: Target phase ID
        trigger_conditions: Conditions that allow transition
        engine_checks: Engine validation before transition
        transition_action: Action to perform during transition
    """

    from_phase: str = Field(..., description="Source phase ID")
    to_phase: str = Field(..., description="Target phase ID")
    trigger_conditions: list[str] = Field(default_factory=list, description="Transition trigger conditions")
    engine_checks: list[str] = Field(default_factory=list, description="Engine validation checks")
    transition_action: dict[str, Any] = Field(default_factory=dict, description="Transition action details")


class EndingCondition(BaseModel):
    """Definition of an ending condition for the module.

    Attributes:
        id: Unique identifier for the ending
        name: Ending name
        description: Description of this ending
        trigger_conditions: Conditions that trigger this ending
        outcome: The outcome of reaching this ending
        closure_action: Action to perform for closure
    """

    id: str = Field(..., description="Ending identifier")
    name: str = Field(..., description="Ending name")
    description: str = Field(..., description="Ending description")
    trigger_conditions: list[str] = Field(default_factory=list, description="Conditions for this ending")
    outcome: str = Field(default="", description="Outcome of this ending")
    closure_action: dict[str, Any] = Field(default_factory=dict, description="Closure action details")


class ContentModule(BaseModel):
    """Aggregated content module structure.

    Contains all components of a content module including metadata, characters,
    relationships, triggers, scene phases, phase transitions, and ending conditions.

    Attributes:
        metadata: Module metadata
        characters: List of character definitions
        relationship_axes: List of relationship axes
        trigger_definitions: List of trigger definitions
        scene_phases: List of scene phases
        phase_transitions: List of phase transitions
        ending_conditions: List of ending conditions
    """

    metadata: ModuleMetadata = Field(..., description="Module metadata")
    characters: list[CharacterDefinition] = Field(default_factory=list, description="Character definitions")
    relationship_axes: list[RelationshipAxis] = Field(default_factory=list, description="Relationship axes")
    trigger_definitions: list[TriggerDefinition] = Field(default_factory=list, description="Trigger definitions")
    scene_phases: list[ScenePhase] = Field(default_factory=list, description="Scene phases")
    phase_transitions: list[PhaseTransition] = Field(default_factory=list, description="Phase transitions")
    ending_conditions: list[EndingCondition] = Field(default_factory=list, description="Ending conditions")

    def character_map(self) -> dict[str, CharacterDefinition]:
        """Create a mapping of character IDs to definitions."""
        return {char.id: char for char in self.characters}

    def phase_map(self) -> dict[str, ScenePhase]:
        """Create a mapping of phase IDs to scene phases."""
        return {phase.id: phase for phase in self.scene_phases}

    def trigger_map(self) -> dict[str, TriggerDefinition]:
        """Create a mapping of trigger IDs to definitions."""
        return {trigger.id: trigger for trigger in self.trigger_definitions}

    def ending_map(self) -> dict[str, EndingCondition]:
        """Create a mapping of ending IDs to conditions."""
        return {ending.id: ending for ending in self.ending_conditions}
