"""
NarrativeRuntimeAgent: Event-based narrator streaming for Live Dramatic Scene Simulator.

This module provides the core streaming narrator component that runs after LDSS,
generating continuous narrator blocks based on NPC motivation pressure and signaling
ruhepunkt (rest point) when NPC initiatives are exhausted.

Architecture:
- Event-based runtime (not turn-sequential)
- Narrator streams continuously based on motivation pressure
- Input blocked while streaming (queued for ruhepunkt processing)
- Optional Langfuse tracing (JSON scaffold default)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generator, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class NarrativeEventKind(Enum):
    """Event types emitted by NarrativeRuntimeAgent."""
    NARRATOR_BLOCK = "narrator_block"
    RUHEPUNKT_REACHED = "ruhepunkt_reached"
    STREAMING_COMPLETE = "streaming_complete"
    ERROR = "error"


@dataclass
class NarrativeRuntimeAgentInput:
    """Input contract for narrative runtime agent."""
    runtime_state: dict[str, Any]  # Current RuntimeState (committed scene, actor positions, etc.)
    npc_agency_plan: dict[str, Any]  # NPCAgencyPlan with remaining initiatives
    dramatic_signature: dict[str, Any]  # Dramatic signature from current turn
    narrative_threads: list[dict[str, Any]]  # Active narrative threads
    session_id: str
    turn_number: int
    trace_id: Optional[str] = None
    enable_langfuse_tracing: bool = False


@dataclass
class NarrativeRuntimeAgentConfig:
    """Configuration for narrative runtime agent behavior."""
    max_narrator_blocks: int = 10
    motivation_pressure_threshold: float = 0.3
    ruhepunkt_check_interval: int = 1  # Check after each narrator block
    enable_optional_silence_filling: bool = True
    streaming_timeout_seconds: int = 60


@dataclass
class NarrativeRuntimeAgentEvent:
    """Individual event streamed by the agent."""
    event_id: str
    event_kind: NarrativeEventKind
    timestamp: datetime
    sequence_number: int
    data: dict[str, Any]

    def to_json(self) -> str:
        """Serialize event to JSON."""
        return json.dumps({
            "event_id": self.event_id,
            "event_kind": self.event_kind.value,
            "timestamp": self.timestamp.isoformat(),
            "sequence_number": self.sequence_number,
            "data": self.data,
        })


class NarrativeRuntimeAgent:
    """
    Event-based narrator that streams blocks based on NPC motivation pressure.

    The agent:
    1. Analyzes remaining NPC initiatives and motivation pressure
    2. Generates narrator blocks (inner perception/orientation only)
    3. Streams events to client while input is queued
    4. Signals ruhepunkt when NPC initiatives exhausted
    5. Respects narrative validation rules (no force, no prediction, no hidden intent)
    """

    def __init__(self, config: Optional[NarrativeRuntimeAgentConfig] = None):
        self.config = config or NarrativeRuntimeAgentConfig()
        self._event_sequence = 0

    def stream_narrator_blocks(
        self,
        agent_input: NarrativeRuntimeAgentInput,
    ) -> Generator[NarrativeRuntimeAgentEvent, None, None]:
        """
        Stream narrator blocks based on NPC motivation pressure.

        Yields NarrativeRuntimeAgentEvent objects. Caller receives events in real-time
        and sends to client (via SSE or WebSocket). When ruhepunkt_reached event is
        yielded, input queue can be processed.

        Args:
            agent_input: NarrativeRuntimeAgentInput with runtime state, NPC plans, etc.

        Yields:
            NarrativeRuntimeAgentEvent for each narrator block or ruhepunkt signal
        """
        block_count = 0
        try:
            # Analyze NPC motivation pressure and remaining initiatives
            motivation_analysis = self._analyze_motivation_pressure(agent_input)

            # Stream narrator blocks while initiatives pending
            while (
                block_count < self.config.max_narrator_blocks
                and motivation_analysis["remaining_initiatives"] > 0
            ):
                narrator_block = self._generate_narrator_block(
                    agent_input=agent_input,
                    motivation_analysis=motivation_analysis,
                    block_sequence=block_count,
                )

                # Validate narrator voice (no force, prediction, hidden intent)
                validation_error = self._validate_narrative_output(narrator_block, agent_input)
                if validation_error:
                    yield self._emit_error_event(
                        session_id=agent_input.session_id,
                        error_code="narrative_validation_failed",
                        error_message=validation_error,
                    )
                    return

                # Emit narrator block event
                yield self._emit_narrator_event(narrator_block, block_sequence=block_count)
                block_count += 1

                # Check ruhepunkt after each block (optional: recalculate pressure)
                if block_count % self.config.ruhepunkt_check_interval == 0:
                    motivation_analysis = self._analyze_motivation_pressure(agent_input)

            # Signal ruhepunkt (rest point) - input can now be processed
            yield self._emit_ruhepunkt_event(
                session_id=agent_input.session_id,
                block_count=block_count,
                motivation_analysis=motivation_analysis,
            )

            # Emit streaming complete event
            yield self._emit_streaming_complete_event(agent_input.session_id, block_count)

        except Exception as exc:
            logger.error(
                f"NarrativeRuntimeAgent streaming failed: {exc}",
                extra={"session_id": agent_input.session_id, "trace_id": agent_input.trace_id},
            )
            yield self._emit_error_event(
                session_id=agent_input.session_id,
                error_code="streaming_exception",
                error_message=str(exc),
            )

    def _analyze_motivation_pressure(
        self,
        agent_input: NarrativeRuntimeAgentInput,
    ) -> dict[str, Any]:
        """
        Analyze NPC motivation pressure and remaining initiatives.

        Returns analysis of:
        - remaining_initiatives: count of unresolved NPC initiatives
        - pressure_score: aggregate motivation pressure (0.0 to 1.0)
        - initiative_actors: list of NPCs with pending initiatives
        - motivation_summary: human-readable pressure summary
        """
        npc_plan = agent_input.npc_agency_plan or {}
        initiatives = npc_plan.get("initiatives", [])

        # Count unresolved initiatives
        remaining = len([i for i in initiatives if not i.get("resolved")])

        # Calculate pressure score based on motivation intensity and count
        pressure = 0.0
        initiative_actors = []
        if remaining > 0:
            pressure = min(1.0, remaining * 0.1 + 0.3)  # Simple heuristic
            initiative_actors = list({i.get("actor_id") for i in initiatives if not i.get("resolved")})

        return {
            "remaining_initiatives": remaining,
            "pressure_score": pressure,
            "initiative_actors": initiative_actors,
            "motivation_summary": (
                f"{remaining} unresolved initiatives from {len(set(i.get('actor_id') for i in initiatives))}"
                if remaining > 0
                else "All NPC initiatives resolved"
            ),
        }

    def _generate_narrator_block(
        self,
        agent_input: NarrativeRuntimeAgentInput,
        motivation_analysis: dict[str, Any],
        block_sequence: int,
    ) -> dict[str, Any]:
        """
        Generate a narrator block based on current motivation pressure.

        Narrator blocks convey inner perception/orientation only:
        - Scene atmosphere and emotional tone
        - Player's subjective sense of tension/calm
        - Narrative thread connections visible to player
        - NPC emotional states (observable from behavior, not hidden intent)

        Does NOT:
        - Force player state or emotion
        - Predict player choice
        - Reveal hidden NPC motivations or plans
        """
        # Stub implementation: generates deterministic narrator block
        # In Phase 2, will integrate with actual narrator generation from ai_stack

        block_id = str(uuid4())
        narrator_text = (
            f"The tension in the room shifts subtly. "
            f"({motivation_analysis['motivation_summary']}. "
            f"Block {block_sequence + 1}.)"
        )

        return {
            "block_id": block_id,
            "sequence": block_sequence,
            "narrator_text": narrator_text,
            "narrative_threads_referenced": agent_input.narrative_threads[:2] if agent_input.narrative_threads else [],
            "atmospheric_tone": "anticipatory",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _validate_narrative_output(
        self,
        narrator_block: dict[str, Any],
        agent_input: NarrativeRuntimeAgentInput,
    ) -> Optional[str]:
        """
        Validate narrator block against narrative voice rules.

        Returns error message if validation fails, None if valid.

        Rules:
        1. No player state forcing (modal language like "you feel", "you realize")
        2. No player choice prediction (conditional future like "if you...")
        3. No hidden NPC intent revelation (internal motivations not observable)
        4. Inner perception only (atmosphere, observable behavior, narrative connections)
        5. Respects player agency (audience to events, not subject of description)
        """
        text = narrator_block.get("narrator_text", "").lower()

        # Check for modal language that forces player state
        force_patterns = [
            "you feel ", "you realize ", "you know ", "you understand ",
            "you sense ", "you notice ", "you see ", "you hear ",
            "you think ", "you believe ",
        ]
        for pattern in force_patterns:
            if pattern in text:
                return f"Narrative validation failed: modal language forces player state ('{pattern.strip()}')"

        # Check for hidden intent revelation (npc internal states)
        intent_patterns = [
            "secretly ", "intends to ", "plans to ", "wants to ",
            "hidden agenda", "true goal", "real motive",
        ]
        for pattern in intent_patterns:
            if pattern in text:
                return f"Narrative validation failed: reveals hidden NPC intent ('{pattern.strip()}')"

        return None

    def _emit_narrator_event(
        self,
        narrator_block: dict[str, Any],
        block_sequence: int,
    ) -> NarrativeRuntimeAgentEvent:
        """Emit a narrator block event."""
        self._event_sequence += 1
        return NarrativeRuntimeAgentEvent(
            event_id=str(uuid4()),
            event_kind=NarrativeEventKind.NARRATOR_BLOCK,
            timestamp=datetime.now(timezone.utc),
            sequence_number=self._event_sequence,
            data={
                "narrator_block": narrator_block,
                "block_sequence": block_sequence,
            },
        )

    def _emit_ruhepunkt_event(
        self,
        session_id: str,
        block_count: int,
        motivation_analysis: dict[str, Any],
    ) -> NarrativeRuntimeAgentEvent:
        """Emit ruhepunkt (rest point) signal - input can now be processed."""
        self._event_sequence += 1
        return NarrativeRuntimeAgentEvent(
            event_id=str(uuid4()),
            event_kind=NarrativeEventKind.RUHEPUNKT_REACHED,
            timestamp=datetime.now(timezone.utc),
            sequence_number=self._event_sequence,
            data={
                "ruhepunkt_reached": True,
                "block_count": block_count,
                "remaining_initiatives": motivation_analysis["remaining_initiatives"],
                "motivation_summary": motivation_analysis["motivation_summary"],
                "session_id": session_id,
            },
        )

    def _emit_streaming_complete_event(
        self,
        session_id: str,
        block_count: int,
    ) -> NarrativeRuntimeAgentEvent:
        """Emit streaming complete event."""
        self._event_sequence += 1
        return NarrativeRuntimeAgentEvent(
            event_id=str(uuid4()),
            event_kind=NarrativeEventKind.STREAMING_COMPLETE,
            timestamp=datetime.now(timezone.utc),
            sequence_number=self._event_sequence,
            data={
                "streaming_complete": True,
                "block_count": block_count,
                "session_id": session_id,
            },
        )

    def _emit_error_event(
        self,
        session_id: str,
        error_code: str,
        error_message: str,
    ) -> NarrativeRuntimeAgentEvent:
        """Emit error event."""
        self._event_sequence += 1
        return NarrativeRuntimeAgentEvent(
            event_id=str(uuid4()),
            event_kind=NarrativeEventKind.ERROR,
            timestamp=datetime.now(timezone.utc),
            sequence_number=self._event_sequence,
            data={
                "error_code": error_code,
                "error_message": error_message,
                "session_id": session_id,
            },
        )
