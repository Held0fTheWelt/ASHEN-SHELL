"""Map AI affordance / resolution statuses onto authority SituationStatus (Wave 3 / E9).

Richer AI vocabulary must never collapse onto a poorer commit status than the
resolution itself implies. Mapping to a poorer value is a contract error.
"""

from __future__ import annotations

from typing import Final

from app.story_runtime.commit_models import SituationStatus

# AI-side affordance statuses (ai_stack AffordanceResolutionContract.status).
AI_AFFORDANCE_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "allowed",
        "allowed_offscreen",
        "partial",
        "prevented",
        "blocked",
        "denied",
        "needs_clarification",
    }
)

# Explicit table: AI status → SituationStatus. Never map to a strictly poorer
# outcome than the AI already resolved (e.g. partial must not become blocked).
AI_TO_SITUATION_STATUS: Final[dict[str, SituationStatus]] = {
    "allowed": "continue",
    "allowed_offscreen": "allowed_offscreen",
    "partial": "partial",
    "prevented": "prevented",
    "blocked": "blocked",
    "denied": "blocked",
    "needs_clarification": "continue",
}

# Poorer-than ordering for contract tests (higher index = poorer / more rejecting).
_SITUATION_POORNESS: Final[dict[str, int]] = {
    "transitioned": 0,
    "continue": 1,
    "allowed_offscreen": 2,
    "partial": 3,
    "prevented": 4,
    "terminal": 5,
    "blocked": 6,
}


def map_ai_affordance_to_situation_status(ai_status: str) -> SituationStatus:
    """Return the authority SituationStatus for an AI affordance status."""
    key = str(ai_status or "").strip().lower()
    if key not in AI_TO_SITUATION_STATUS:
        raise KeyError(f"unmapped AI affordance status: {ai_status!r}")
    return AI_TO_SITUATION_STATUS[key]


def mapping_is_not_poorer(ai_status: str, situation: SituationStatus) -> bool:
    """True when ``situation`` is not poorer than the AI status's mapped value."""
    expected = map_ai_affordance_to_situation_status(ai_status)
    return _SITUATION_POORNESS.get(situation, 99) <= _SITUATION_POORNESS.get(expected, 99)
