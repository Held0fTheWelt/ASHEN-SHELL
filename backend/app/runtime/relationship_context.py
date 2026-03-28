"""W2.3.4 — Canonical relationship-axis context for longer-session coherence.

Derives and maintains the most relevant interpersonal dynamics from session
history and progression signals. Surfaces salient relationship axes without
replaying full history or complete relationship state.

RelationshipAxisContext is distinct from:
- raw session history (aggregated and bounded)
- full canonical state (only salient axes extracted)
- progression summary (interpersonal focus vs structural)
- future AI request assembly (runtime context not prompt prose)
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.runtime.session_history import SessionHistory


class SalientRelationshipAxis(BaseModel):
    """A single relationship axis that matters in the current context.

    Captures the most relevant interpersonal dynamics between two characters
    based on recent activity, detected changes, and escalation signals.

    Attributes:
        character_a: First character ID in the relationship.
        character_b: Second character ID in the relationship.
        salience_score: Relevance score (0.0-1.0) based on recent activity.
        recent_change_direction: Trend (escalating, stable, de-escalating).
        signal_type: Classification (tension, alliance, instability, stable).
        involved_in_recent_triggers: Triggers mentioning these characters.
        last_involved_turn: Most recent turn this axis mattered.
    """

    character_a: str
    character_b: str
    salience_score: float  # 0.0 to 1.0
    recent_change_direction: str  # escalating, stable, de-escalating
    signal_type: str  # tension, alliance, instability, stable
    involved_in_recent_triggers: list[str] = Field(default_factory=list)
    last_involved_turn: int = 0


class RelationshipAxisContext(BaseModel):
    """Bounded, deterministic relationship-axis context for a session.

    Surfaces the most relevant interpersonal dynamics derived from session
    history and progression signals. Enables later context assembly to
    understand character relationships without full state dump.

    Attributes:
        salient_axes: Most relevant relationship axes (bounded to 10).
        total_character_pairs_known: Count of all character pairs in history.
        overall_stability_signal: General relationship health signal.
        has_escalation_markers: Whether any axes show escalation.
        has_de_escalation_markers: Whether any axes show de-escalation.
        highest_salience_axis: The relationship axis that matters most.
        highest_tension_axis: The relationship axis most in conflict.
        derived_from_turn: Last turn processed for this context.
    """

    salient_axes: list[SalientRelationshipAxis] = Field(default_factory=list)
    total_character_pairs_known: int = 0
    overall_stability_signal: str = "unknown"  # stable, mixed, escalating, de-escalating
    has_escalation_markers: bool = False
    has_de_escalation_markers: bool = False
    highest_salience_axis: Optional[tuple[str, str]] = None
    highest_tension_axis: Optional[tuple[str, str]] = None
    derived_from_turn: int = 0


def _extract_characters_from_trigger(trigger_name: str) -> set[str]:
    """Extract likely character identifiers from a trigger name.

    Simple heuristic: split by known separators and identify character-like tokens.
    For example: "accusation_veronique_giuseppe" → {"veronique", "giuseppe"}

    Args:
        trigger_name: The trigger name to analyze.

    Returns:
        Set of character identifiers mentioned in the trigger.
    """
    # Split by separators
    parts = trigger_name.lower().replace("-", "_").split("_")

    # Filter out common non-character words
    excluded = {
        "conflict",
        "tension",
        "accusation",
        "betrayal",
        "reconciliation",
        "alliance",
        "hostility",
        "support",
        "doubt",
        "escalation",
        "de",
        "resolution",
        "event",
        "trigger",
    }

    chars = {p for p in parts if p and len(p) > 2 and p not in excluded}
    return chars


def derive_relationship_axis_context(history: SessionHistory) -> RelationshipAxisContext:
    """Derive relationship-axis context from bounded session history.

    Analyzes triggers and session progression to surface the most salient
    relationship dynamics: which axes matter, what trends are visible, and
    where escalation or resolution is concentrating.

    Args:
        history: A SessionHistory to analyze.

    Returns:
        A bounded RelationshipAxisContext suitable for later context assembly.
    """
    if not history.entries:
        return RelationshipAxisContext()

    # Scan for all character pairs mentioned in triggers
    axis_involvement: dict[tuple[str, str], list[int]] = {}  # (a, b) → [turn1, turn2, ...]
    axis_triggers: dict[tuple[str, str], set[str]] = {}  # (a, b) → {trigger1, trigger2, ...}

    for entry in history.entries:
        for trigger in entry.detected_triggers:
            chars = _extract_characters_from_trigger(trigger)

            # Create all pairs from extracted characters
            char_list = sorted(chars)
            for i, a in enumerate(char_list):
                for b in char_list[i + 1 :]:
                    axis = (a, b)
                    if axis not in axis_involvement:
                        axis_involvement[axis] = []
                        axis_triggers[axis] = set()

                    axis_involvement[axis].append(entry.turn_number)
                    axis_triggers[axis].add(trigger)

    total_axes = len(axis_involvement)

    # Score salience: recency + frequency
    axis_salience: dict[tuple[str, str], float] = {}

    for axis, turns in axis_involvement.items():
        # Recency: how close to current turn
        most_recent_turn = max(turns)
        age = (history.entries[-1].turn_number - most_recent_turn) + 1
        recency_score = max(0, 1.0 - (age / max(10, len(history.entries))))

        # Frequency: how many times involved
        frequency_score = min(1.0, len(turns) / 5.0)

        # Combined salience
        salience = (recency_score * 0.6) + (frequency_score * 0.4)
        axis_salience[axis] = salience

    # Sort by salience and keep top 10
    sorted_axes = sorted(axis_salience.items(), key=lambda x: -x[1])[:10]

    salient_axes = []
    highest_salience = None
    highest_tension = None
    escalation_count = 0
    de_escalation_count = 0

    for (a, b), salience in sorted_axes:
        turns = axis_involvement[(a, b)]
        triggers = list(axis_triggers[(a, b)])

        # Detect trend: escalation vs de-escalation
        # Simple heuristic: look for escalation/tension keywords vs resolution keywords
        escalation_keywords = {"escalation", "tension", "conflict", "hostility", "accusation", "betrayal"}
        resolution_keywords = {"reconciliation", "resolution", "peace", "alliance", "support"}

        escalation_mentions = sum(1 for t in triggers if any(k in t.lower() for k in escalation_keywords))
        resolution_mentions = sum(1 for t in triggers if any(k in t.lower() for k in resolution_keywords))

        if escalation_mentions > resolution_mentions:
            trend = "escalating"
            escalation_count += 1
        elif resolution_mentions > escalation_mentions:
            trend = "de-escalating"
            de_escalation_count += 1
        else:
            trend = "stable"

        # Determine signal type based on keywords
        if any("alliance" in t or "support" in t for t in triggers):
            signal = "alliance"
        elif any("hostility" in t or "conflict" in t or "tension" in t for t in triggers):
            signal = "tension"
        elif any("doubt" in t or "unstable" in t for t in triggers):
            signal = "instability"
        else:
            signal = "stable"

        axis = SalientRelationshipAxis(
            character_a=a,
            character_b=b,
            salience_score=salience,
            recent_change_direction=trend,
            signal_type=signal,
            involved_in_recent_triggers=triggers[:5],  # Keep top 5 triggers
            last_involved_turn=max(turns),
        )

        salient_axes.append(axis)

        if highest_salience is None:
            highest_salience = (a, b)
        if highest_tension is None and signal == "tension":
            highest_tension = (a, b)

    # Determine overall stability
    if escalation_count > de_escalation_count:
        stability = "escalating"
    elif de_escalation_count > escalation_count:
        stability = "de-escalating"
    elif escalation_count > 0 or de_escalation_count > 0:
        stability = "mixed"
    else:
        stability = "stable" if salient_axes else "unknown"

    return RelationshipAxisContext(
        salient_axes=salient_axes,
        total_character_pairs_known=total_axes,
        overall_stability_signal=stability,
        has_escalation_markers=(escalation_count > 0),
        has_de_escalation_markers=(de_escalation_count > 0),
        highest_salience_axis=highest_salience,
        highest_tension_axis=highest_tension,
        derived_from_turn=history.entries[-1].turn_number if history.entries else 0,
    )
