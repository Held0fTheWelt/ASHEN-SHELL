"""Player input scene-block helpers.

Extracts scene-block context around player input for runtime prompts, diagnostics, and visible projections.
"""
from __future__ import annotations

from ._deps import *

def _player_input_language(session_output_language: str) -> str:
    lang = str(session_output_language or DEFAULT_SESSION_LANGUAGE).strip().lower()
    return lang[:2] or DEFAULT_SESSION_LANGUAGE


def _player_input_kind(interpreted_input: dict[str, Any]) -> str:
    pik_fine = str(interpreted_input.get("player_input_kind") or "").strip().lower()
    kind = pik_fine or str(
        interpreted_input.get("input_kind") or interpreted_input.get("kind") or "speech"
    ).strip().lower()
    return "speech" if kind in ("intent_only", "reaction") else kind


def _player_capability_for_kind(player_input_kind: str) -> str:
    return {
        "action": PLAYER_ACTION_REQUEST,
        "movement_action": PLAYER_MOVEMENT_REQUEST,
        "object_interaction": PLAYER_OBJECT_INTERACTION_REQUEST,
        "perception": PLAYER_PERCEPTION_REQUEST,
        "perception_action": PLAYER_PERCEPTION_REQUEST,
        "mixed": PLAYER_ACTION_REQUEST,
        "question": PLAYER_SPEECH_REQUEST,
        "speech": PLAYER_SPEECH_REQUEST,
    }.get(player_input_kind, "player.input")


def _player_input_delivery() -> dict[str, Any]:
    return {
        "mode": "typewriter",
        "characters_per_second": 44,
        "pause_before_ms": 0,
        "pause_after_ms": 120,
        "skippable": True,
    }


def _player_input_visible_lines(
    *,
    text: str,
    canon: str,
    name: str,
    exp_lang: str,
    interpreted_input: dict[str, Any],
) -> tuple[str, str]:
    pair = _goc_greeting_imperative_visible_pair(
        raw=text,
        player_shell_name=name,
        lang=exp_lang,
    )
    if pair and _player_input_kind(interpreted_input) in {
        "speech",
        "action",
        "social_nonverbal_action",
    }:
        return pair[0], pair[1]
    return (
        text,
        _goc_player_attributed_visible_text(
            raw_input=text,
            human_actor_id=canon,
            session_output_language=exp_lang,
            interpreted_input=interpreted_input,
        )[1],
    )


def _player_input_actor_blocks(
    *,
    session_id: str,
    turn_token: str,
    canon: str,
    name: str,
    verbatim_line: str,
    outcome_line: str,
    exp_lang: str,
    interpreted_input: dict[str, Any],
) -> list[dict[str, Any]]:
    player_input_kind = str(
        interpreted_input.get("player_input_kind")
        or interpreted_input.get("kind")
        or "speech"
    ).strip().lower()
    render_hints = {"player_input_kind": player_input_kind}
    player_capability = _player_capability_for_kind(player_input_kind)
    out_blocks: list[dict[str, Any]] = []
    for suffix, line, block_type in (
        ("", verbatim_line, "player_input"),
        ("-outcome", outcome_line, "player_input_outcome"),
    ):
        cleaned, _partial = sanitize_visible_block_text(
            line,
            block_type=block_type,
            speaker_label=name,
            actor_id=canon,
            expected_language=exp_lang,
        )
        if cleaned:
            out_blocks.append(
                {
                    "id": f"{session_id}-turn-{turn_token}-player-input{suffix}",
                    "block_type": block_type,
                    "speaker_label": name,
                    "actor_id": canon,
                    "target_actor_id": None,
                    "text": cleaned,
                    "delivery": _player_input_delivery(),
                    "source": "player_input",
                    "render_hints": render_hints,
                    "origin_aspect": ASPECT_INPUT,
                    "origin_beat_id": None,
                    "origin_capability": player_capability,
                    "authority_owner": "player",
                    "expected_owner": "player",
                    "actual_owner": "player",
                    "canonical_turn_id": f"{session_id}:turn:{turn_token}",
                    "evidence_role": EVIDENCE_SUPPORTING,
                }
            )
    return out_blocks


def _legacy_player_input_block(
    *,
    session_id: str,
    turn_token: str,
    text: str,
    speaker_label: str,
) -> dict[str, Any]:
    return {
        "id": f"{session_id}-turn-{turn_token}-player-input",
        "block_type": "player_input",
        "speaker_label": speaker_label,
        "actor_id": None,
        "target_actor_id": None,
        "text": text,
        "delivery": _player_input_delivery(),
        "source": "player_commit",
        "origin_aspect": ASPECT_INPUT,
        "origin_beat_id": None,
        "origin_capability": "player.input",
        "authority_owner": "player",
        "expected_owner": "player",
        "actual_owner": "player",
        "canonical_turn_id": f"{session_id}:turn:{turn_token}",
        "evidence_role": EVIDENCE_SUPPORTING,
    }


def _player_input_scene_blocks_for_story_window(
    *,
    session_id: str,
    turn_number: Any,
    raw_input: str,
    session_output_language: str,
    human_actor_id: str | None = None,
    interpreted_input: dict[str, Any] | None = None,
    module_id: str | None = None,
) -> list[dict[str, Any]]:
    """MVP5 cumulative transcript: visible player line for the story shell.

    When ``human_actor_id`` is bound (canonical solo path), **always** emit **two**
    cards: ``player_input`` (verbatim typing, italic shell lane) then
    ``player_input_outcome`` (diegetic attributed line for the selected human actor).

    Imperative greetings to a named actor still use the scripted polite
    outcome line for the second card; all other inputs use ``_goc_player_attributed_visible_text``.

    Without a human actor id (legacy / non-solo), a single ``player_input`` block
    with speaker *Du* / *You* is emitted.

    Player text is not part of runtime ``spoken_lines`` (human lane is filtered from
    scene envelope). Story-window entries must still carry ``scene_blocks`` so backend
    ``_cumulative_scene_blocks_from_story_window`` can replay the full transcript.
    """
    text = str(raw_input or "").strip()
    if not text:
        return []
    exp_lang = _player_input_language(session_output_language)
    mid = (module_id or GOD_OF_CARNAGE_MODULE_ID).strip()
    root = _goc_content_modules_root()
    turn_token = str(turn_number).strip() if turn_number is not None else "0"
    hid = str(human_actor_id or "").strip()
    if hid:
        canon = str(canonicalize_goc_actor_id(hid) or hid).strip()
        name = _goc_shell_actor_firstname(canon)
        interp = interpreted_input if isinstance(interpreted_input, dict) else {}
        verbatim_line, outcome_line = _player_input_visible_lines(
            text=text,
            canon=canon,
            name=name,
            exp_lang=exp_lang,
            interpreted_input=interp,
        )
        out_blocks = _player_input_actor_blocks(
            session_id=session_id,
            turn_token=turn_token,
            canon=canon,
            name=name,
            verbatim_line=verbatim_line,
            outcome_line=outcome_line,
            exp_lang=exp_lang,
            interpreted_input=interp,
        )
        if out_blocks:
            return out_blocks
    speaker_label = resolve_string(mid, "player_shell.second_person", exp_lang, content_modules_root=root)
    return [
        _legacy_player_input_block(
            session_id=session_id,
            turn_token=turn_token,
            text=text,
            speaker_label=speaker_label,
        )
    ]

__all__ = [
    name
    for name in globals()
    if not name.startswith("__") and name != "annotations"
]
