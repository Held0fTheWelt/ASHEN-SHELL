"""Runtime turn output proposal models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProposedEffect(BaseModel):
    """One proposed state effect from generation output."""

    effect_type: str
    target_ref: str | None = None
    description: str
    magnitude: int | None = None
    evidence: str | None = None


class RuntimeTurnStructuredOutputV2(BaseModel):
    """Structured proposal from turn generation before commit validation."""

    narrative_response: str
    intent_summary: str = ""
    responder_actor_ids: list[str] = Field(default_factory=list)
    detected_triggers: list[str] = Field(default_factory=list)
    conflict_vector: str = ""
    proposed_state_effects: list[ProposedEffect] = Field(default_factory=list)
    confidence: float | None = None
    blocked_turn_reason: str | None = None
