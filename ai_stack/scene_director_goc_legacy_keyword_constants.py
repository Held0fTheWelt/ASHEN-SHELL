"""
Named pacing / keyword fragments for GoC legacy keyword heuristic
(readability batch for DS-003).
"""

from __future__ import annotations

from typing import Final

PACING_CONTAINMENT: Final[str] = "containment"
PACING_THIN_EDGE: Final[str] = "thin_edge"
MOVE_CLASS_QUESTION: Final[str] = "question"

THIN_EDGE_SILENCE_PHRASES: Final[tuple[str, ...]] = ("silent", "say nothing", "nothing")

SILENCE_PAUSE_PHRASES: Final[tuple[str, ...]] = (
    "silent",
    "say nothing",
    "awkward pause",
    "long pause",
    "do not answer",
    "won't answer",
)

HUMILIATION_PHRASES: Final[tuple[str, ...]] = ("humiliat", "embarrass", "ashamed", "ridicule", "mock")

EVASION_PHRASES: Final[tuple[str, ...]] = ("evade", "deflect", "avoid answering", "change subject")

REPAIR_PHRASES: Final[tuple[str, ...]] = ("sorry", "apolog", "repair")

REVEAL_PHRASES: Final[tuple[str, ...]] = ("reveal", "secret", "truth", "admit")

BLAME_PHRASES: Final[tuple[str, ...]] = ("blame", "fault")

PROBE_PHRASES: Final[tuple[str, ...]] = ("why", "motive", "reason")

ESCALATION_PHRASES: Final[tuple[str, ...]] = ("escalat", "fight", "angry", "furious", "attack")

ALLIANCE_REPOSITION_PHRASES: Final[tuple[str, ...]] = (
    "side with",
    "siding with",
    "ally with",
    "stand with",
    "against your wife",
    "against your husband",
)


def combined_player_text(player_input: str, intent: str) -> str:
    """``combined_player_text`` — see implementation for behaviour and contracts.
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        player_input: ``player_input`` (str); meaning follows the type and call sites.
        intent: ``intent`` (str); meaning follows the type and call sites.
    
    Returns:
        str:
            Returns a value of type ``str``; see the function body for structure, error paths, and sentinels.
    """
    return f"{player_input} {intent}".lower()


def contains_any(haystack: str, phrases: tuple[str, ...]) -> bool:
    """``contains_any`` — see implementation for behaviour and contracts.
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        haystack: ``haystack`` (str); meaning follows the type and call sites.
        phrases: ``phrases`` (tuple[str, ...]); meaning follows the type and call sites.
    
    Returns:
        bool:
            Returns a value of type ``bool``; see the function body for structure, error paths, and sentinels.
    """
    return any(p in haystack for p in phrases)
