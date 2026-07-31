"""Technical failure recovery policies for live story turns (Wave 4 / E7).

Chain on technical failure:
1. One cheap reduced-context retry (shorter prompt than the first attempt).
2. Deterministic continue-turn with no further model call, marked
   ``technically_reduced`` (distinct from narrative ``prevented``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DegradedMode(str, Enum):
    NONE = "none"
    TECHNICALLY_REDUCED = "technically_reduced"
    NARRATIVELY_PREVENTED = "narratively_prevented"


@dataclass(slots=True)
class StateSnapshot:
    """Minimal restore point for a failed generation attempt."""

    scene_id: str
    turn_number: int
    revision: int | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "turn_number": self.turn_number,
            "revision": self.revision,
            "payload": dict(self.payload),
        }


@dataclass
class RetryPolicy:
    """First-attempt retry budget (count only; context size unchanged)."""

    max_retries: int = 0  # E7: primary path uses ReducedContextRetry once instead


@dataclass
class ReducedContextRetryPolicy:
    """Single cheaper retry with truncated context (E7 step 1)."""

    enabled: bool = True
    max_context_chars: int = 2_000
    max_attempts: int = 1

    def shrink_prompt(self, prompt: str) -> str:
        text = str(prompt or "")
        if len(text) <= self.max_context_chars:
            return text
        return text[: self.max_context_chars]


@dataclass
class FallbackResponderPolicy:
    """Optional cheap responder after reduced retry fails."""

    enabled: bool = True
    mode: str = "deterministic_continue"


@dataclass
class SafeTurnPolicy:
    """Deterministic continue-turn without a model call (E7 step 2)."""

    enabled: bool = True
    degraded_mode: DegradedMode = DegradedMode.TECHNICALLY_REDUCED
    player_visible_line: str = (
        "The moment hangs unresolved; the scene continues without a model reply."
    )


@dataclass
class RestorePolicy:
    """Restore from snapshot when abandoning a failed attempt."""

    enabled: bool = True

    def restore(self, snapshot: StateSnapshot) -> dict[str, Any]:
        return {
            "scene_id": snapshot.scene_id,
            "turn_number": snapshot.turn_number,
            "revision": snapshot.revision,
            "payload": dict(snapshot.payload),
            "restored": True,
        }


@dataclass
class FailureRecoveryBundle:
    retry: RetryPolicy = field(default_factory=RetryPolicy)
    reduced_context_retry: ReducedContextRetryPolicy = field(
        default_factory=ReducedContextRetryPolicy
    )
    fallback_responder: FallbackResponderPolicy = field(
        default_factory=FallbackResponderPolicy
    )
    safe_turn: SafeTurnPolicy = field(default_factory=SafeTurnPolicy)
    restore: RestorePolicy = field(default_factory=RestorePolicy)


def build_reduced_context_retry_prompt(*, original_prompt: str, policy: ReducedContextRetryPolicy) -> str:
    """Return a retry prompt that is never longer than the original (E7)."""
    shrunk = policy.shrink_prompt(original_prompt)
    if len(shrunk) > len(original_prompt):
        return original_prompt
    return shrunk


def deterministic_continuation_turn(
    *,
    prior_scene_id: str,
    turn_number: int,
    policy: SafeTurnPolicy | None = None,
) -> dict[str, Any]:
    """Build a continue-turn payload that requires zero model calls."""
    pol = policy or SafeTurnPolicy()
    return {
        "turn_number": turn_number,
        "committed_scene_id": prior_scene_id,
        "situation_status": "continue",
        "allowed": True,
        "commit_reason_code": "technically_reduced_continuation",
        "authoritative_reason": "Technical failure exhausted; deterministic continue-turn.",
        "degraded_mode": pol.degraded_mode.value,
        "trace_completeness": "reduced",
        "player_visible_lines": [pol.player_visible_line],
        "model_calls_additional": 0,
        "committed_consequences": [
            f"scene_continue:{prior_scene_id}",
            "technically_reduced",
        ],
    }


DEFAULT_FAILURE_RECOVERY = FailureRecoveryBundle()
