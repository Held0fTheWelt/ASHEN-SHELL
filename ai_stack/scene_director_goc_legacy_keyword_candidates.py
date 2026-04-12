"""Pre-semantic keyword / pacing heuristic for GoC scene candidates (legacy fallback path)."""

from __future__ import annotations

from typing import Any


def legacy_keyword_scene_candidates(
    *,
    pacing_mode: str,
    player_input: str,
    interpreted_move: dict[str, Any],
    prior_classes: list[str],
) -> tuple[list[str], dict[str, str], list[str]]:
    """Pre-semantic keyword/tie-break heuristic — bounded fallback only when semantic record absent."""
    text = f"{player_input} {interpreted_move.get('player_intent', '')}".lower()
    move_class = str(interpreted_move.get("move_class") or "").lower()
    intent = str(interpreted_move.get("player_intent") or "").lower()
    implied: dict[str, str] = {}
    candidates: list[str] = []
    heuristic_trace: list[str] = []

    if pacing_mode == "containment":
        candidates.append("scene_pivot")
        implied["scene_pivot"] = "refused_cooperation"
        heuristic_trace.append("pacing_mode:containment->scene_pivot")
    elif pacing_mode == "thin_edge":
        if "silent" in text or "say nothing" in text or "nothing" in text:
            candidates.append("withhold_or_evade")
            implied["withhold_or_evade"] = "silent_carry"
            heuristic_trace.append("thin_edge:silence_keyword->withhold_or_evade")
        else:
            candidates.append("establish_pressure")
            implied["establish_pressure"] = "situational_pressure"
            heuristic_trace.append("thin_edge:default->establish_pressure")
    else:
        if (
            "silent" in text
            or "say nothing" in text
            or "awkward pause" in text
            or "long pause" in text
            or "do not answer" in text
            or "won't answer" in text
        ):
            candidates.append("withhold_or_evade")
            implied["withhold_or_evade"] = "silent_carry"
            heuristic_trace.append("keyword:silence_pause->withhold_or_evade")
        if (
            "humiliat" in text
            or "embarrass" in text
            or "ashamed" in text
            or "ridicule" in text
            or "mock" in text
        ):
            candidates.append("redirect_blame")
            implied["redirect_blame"] = "dignity_injury"
            heuristic_trace.append("keyword:humiliation->redirect_blame")
        if (
            "evade" in text
            or "deflect" in text
            or "avoid answering" in text
            or "change subject" in text
        ):
            candidates.append("withhold_or_evade")
            implied["withhold_or_evade"] = "silent_carry"
            heuristic_trace.append("keyword:evasion->withhold_or_evade")
        if "sorry" in text or "apolog" in text or "repair" in text:
            candidates.append("repair_or_stabilize")
            implied["repair_or_stabilize"] = "repair_attempt"
            heuristic_trace.append("keyword:repair->repair_or_stabilize")
        if "reveal" in text or "secret" in text or "truth" in text or "admit" in text:
            candidates.append("reveal_surface")
            implied["reveal_surface"] = "revealed_fact"
            heuristic_trace.append("keyword:reveal->reveal_surface")
        if "blame" in text or "fault" in text:
            candidates.append("redirect_blame")
            implied["redirect_blame"] = "blame_pressure"
            heuristic_trace.append("keyword:blame->redirect_blame")
        if "why" in text or "motive" in text or "reason" in text:
            candidates.append("probe_motive")
            implied["probe_motive"] = "situational_pressure"
            heuristic_trace.append("keyword:probe->probe_motive")
        if "escalat" in text or "fight" in text or "angry" in text or "furious" in text or "attack" in text:
            candidates.append("escalate_conflict")
            implied["escalate_conflict"] = "situational_pressure"
            heuristic_trace.append("keyword:escalation->escalate_conflict")
        if (
            "side with" in text
            or "siding with" in text
            or "ally with" in text
            or "stand with" in text
            or "against your wife" in text
            or "against your husband" in text
        ):
            candidates.append("scene_pivot")
            implied["scene_pivot"] = "alliance_shift"
            heuristic_trace.append("keyword:alliance_reposition->scene_pivot")

        if (
            ("question" in move_class or "question" in intent or player_input.strip().endswith("?"))
            and "probe_motive" not in candidates
            and "containment" not in pacing_mode
        ):
            candidates.append("probe_motive")
            implied["probe_motive"] = "situational_pressure"
            heuristic_trace.append("interpreted_move:question_nudge->probe_motive")

        if "blame_pressure" in prior_classes and not candidates:
            candidates.append("redirect_blame")
            implied["redirect_blame"] = "blame_pressure"
            heuristic_trace.append("continuity:blame_pressure_fallback->redirect_blame")
        if "dignity_injury" in prior_classes and not candidates:
            candidates.append("redirect_blame")
            implied["redirect_blame"] = "dignity_injury"
            heuristic_trace.append("continuity:dignity_injury_fallback->redirect_blame")
        if "alliance_shift" in prior_classes and "probe_motive" not in candidates and "why" in text:
            candidates.append("probe_motive")
            implied["probe_motive"] = "alliance_shift"
            heuristic_trace.append("continuity:alliance_shift_nudge->probe_motive")
        if "blame_pressure" in prior_classes and "redirect_blame" not in candidates and "watch" in text:
            candidates.append("redirect_blame")
            implied["redirect_blame"] = "blame_pressure"
            heuristic_trace.append("continuity:watch_under_blame->redirect_blame")

        if not candidates:
            candidates.append("establish_pressure")
            implied["establish_pressure"] = "situational_pressure"
            heuristic_trace.append("default->establish_pressure")

    return candidates, implied, heuristic_trace
