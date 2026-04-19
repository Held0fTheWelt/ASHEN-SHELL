from __future__ import annotations
from typing import Any

FORBIDDEN_PLAYER_KEYS = {
    "operator_bundle",
    "backend_interpretation_preview",
    "raw_diagnostics",
    "live_room",
    "privileged_copy_controls",
}

REQUIRED_PLAYER_KEYS = {
    "transcript",
    "gm_narration",
    "turn_number",
}


def validate_player_surface_payload(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    missing = sorted(key for key in REQUIRED_PLAYER_KEYS if key not in payload)
    if missing:
        errors.append(f"missing required keys: {', '.join(missing)}")
    leaked = sorted(key for key in FORBIDDEN_PLAYER_KEYS if key in payload)
    if leaked:
        errors.append(f"forbidden player keys present: {', '.join(leaked)}")
    return (not errors, errors)


def make_clean_player_surface(*, transcript: list[dict[str, Any]], gm_narration: str, turn_number: int, status: str = "committed") -> dict[str, Any]:
    return {
        "transcript": transcript,
        "gm_narration": gm_narration,
        "turn_number": turn_number,
        "status": status,
    }
