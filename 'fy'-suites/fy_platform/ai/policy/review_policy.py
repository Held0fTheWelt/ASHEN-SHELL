from __future__ import annotations

from fy_platform.ai.schemas.common import ReviewTransitionResult

ALLOWED_REVIEW_STATES = {"raw", "accepted", "superseded", "rejected"}
ALLOWED_REVIEW_TRANSITIONS = {
    "raw": {"accepted", "rejected"},
    "accepted": {"superseded"},
    "superseded": set(),
    "rejected": set(),
}


def is_valid_transition(current: str, new: str) -> bool:
    if current not in ALLOWED_REVIEW_TRANSITIONS:
        return False
    return new in ALLOWED_REVIEW_TRANSITIONS[current]


def validate_transition(current: str, new: str) -> ReviewTransitionResult:
    if current not in ALLOWED_REVIEW_STATES:
        return ReviewTransitionResult(False, current, new, f'unknown_current_state:{current}')
    if new not in ALLOWED_REVIEW_STATES:
        return ReviewTransitionResult(False, current, new, f'unknown_new_state:{new}')
    if current == new:
        return ReviewTransitionResult(True, current, new, 'noop_transition')
    if is_valid_transition(current, new):
        return ReviewTransitionResult(True, current, new, 'valid_transition')
    return ReviewTransitionResult(False, current, new, f'invalid_transition:{current}->{new}')
