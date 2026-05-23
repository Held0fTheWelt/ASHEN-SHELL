"""Bounded live-turn branching forecast helpers.

The forecast is proposal-only evidence derived from an already committed turn.
It must never create a parallel canonical history or mutate inactive branches.
"""

from __future__ import annotations

import hashlib
from typing import Any

from story_runtime_core.serialization import sequence_list as _as_list


BRANCHING_FORECAST_SCHEMA_VERSION = "branching_forecast.v1"
BRANCHING_FORECAST_SOURCE = "world_engine_committed_turn"
MAX_BRANCH_OPTIONS = 3
MAX_TRIGGER_REASONS = 8
MAX_SOURCE_INPUTS = 8
MAX_TEXT = 96


def _short(value: Any, limit: int = MAX_TEXT) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        dumped = value.model_dump(mode="json")
        return dumped if isinstance(dumped, dict) else {}
    return {}


def _str_list(value: Any, *, limit: int = 8) -> list[str]:
    out: list[str] = []
    for item in _as_list(value):
        token = _short(item, 64)
        if token and token not in out:
            out.append(token)
        if len(out) >= limit:
            break
    return out


def _active_threads(thread_set: Any) -> list[dict[str, Any]]:
    raw = thread_set
    if hasattr(raw, "model_dump"):
        raw = raw.model_dump(mode="json")
    if isinstance(raw, dict):
        raw = raw.get("active")
    rows: list[dict[str, Any]] = []
    for item in _as_list(raw):
        row = _as_dict(item)
        if not row:
            continue
        if str(row.get("status") or "").strip().lower() == "resolved":
            continue
        rows.append(row)
    return rows[:8]


def _thread_entities(threads: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in threads:
        raw = row.get("related_entities")
        if raw is None:
            raw = row.get("related_characters")
        for entity in _as_list(raw):
            token = _short(entity, 48)
            if token and token not in out:
                out.append(token)
            if len(out) >= 6:
                return out
    return out


def _dominant_thread(threads: list[dict[str, Any]], thread_metrics: dict[str, Any]) -> dict[str, Any]:
    if threads:
        return max(
            threads,
            key=lambda row: (
                int(row.get("intensity") or 0),
                int(row.get("persistence_turns") or 0),
                str(row.get("thread_id") or ""),
            ),
        )
    kind = str(thread_metrics.get("dominant_thread_kind") or "").strip()
    if kind:
        return {
            "thread_kind": kind,
            "intensity": int(thread_metrics.get("thread_pressure_level") or 0),
        }
    return {}


def _add_reason(reasons: list[str], reason: str) -> None:
    token = str(reason or "").strip()
    if token and token not in reasons and len(reasons) < MAX_TRIGGER_REASONS:
        reasons.append(token)


def _source_input(source: str, count: int, sample: Any = None) -> dict[str, Any]:
    row: dict[str, Any] = {
        "source": source,
        "count": max(0, int(count or 0)),
    }
    if sample is not None:
        row["sample"] = _short(sample)
    return row


def _option_id(seed: str, family: str) -> str:
    digest = hashlib.sha256(f"{seed}|{family}".encode("utf-8")).hexdigest()[:12]
    return f"branch_{family}_{digest}"


def _branch_option(
    *,
    seed: str,
    family: str,
    label: str,
    forecasted_consequence: str,
    trigger_reasons: list[str],
    consequence_tags: list[str],
    pressure_delta: dict[str, int] | None = None,
) -> dict[str, Any]:
    return {
        "option_id": _option_id(seed, family),
        "family": family,
        "label": label,
        "source": "deterministic_runtime_forecast",
        "authority": "proposal_only",
        "state_mutation_allowed": False,
        "selection_required_to_commit": True,
        "trigger_reasons": trigger_reasons[:MAX_TRIGGER_REASONS],
        "consequence_tags": consequence_tags[:8],
        "pressure_delta": dict(pressure_delta or {}),
        "forecasted_consequence": _short(forecasted_consequence, 140),
    }


def _base_forecast(
    *,
    story_session_id: str | None,
    module_id: str | None,
    runtime_profile_id: str | None,
    canonical_turn_id: str | None,
    turn_number: int,
    turn_kind: str | None,
    committed_scene_id: str | None,
    status: str,
    trigger_reasons: list[str] | None = None,
    source_inputs: list[dict[str, Any]] | None = None,
    options: list[dict[str, Any]] | None = None,
    thread_pressure_level: int = 0,
    dominant_thread_kind: str | None = None,
) -> dict[str, Any]:
    opts = list(options or [])[:MAX_BRANCH_OPTIONS]
    option_seed = "|".join(str(o.get("option_id") or "") for o in opts)
    path_signature = hashlib.sha256(option_seed.encode("utf-8")).hexdigest()[:16] if option_seed else None
    return {
        "schema_version": BRANCHING_FORECAST_SCHEMA_VERSION,
        "status": status,
        "source": BRANCHING_FORECAST_SOURCE,
        "story_session_id": story_session_id,
        "module_id": module_id,
        "runtime_profile_id": runtime_profile_id,
        "canonical_turn_id": canonical_turn_id,
        "turn_number": turn_number,
        "turn_kind": turn_kind or ("opening" if turn_number <= 0 else "player"),
        "committed_scene_id": committed_scene_id,
        "forecast_only": True,
        "authoritative": False,
        "inactive_branches_authoritative": False,
        "mutates_canonical_state": False,
        "selection_required_to_commit": True,
        "source_commit_authoritative": True,
        "trigger_reasons": list(trigger_reasons or [])[:MAX_TRIGGER_REASONS],
        "source_inputs": list(source_inputs or [])[:MAX_SOURCE_INPUTS],
        "thread_pressure_level": max(0, int(thread_pressure_level or 0)),
        "dominant_thread_kind": dominant_thread_kind,
        "options": opts,
        "option_count": len(opts),
        "path_signature": path_signature,
    }


def _forecast_turn_context(
    *,
    turn_number: int | None,
    turn_kind: str | None,
    narrative_commit: Any,
    graph_state: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], int, str, str | None]:
    commit = _as_dict(narrative_commit)
    graph = graph_state if isinstance(graph_state, dict) else {}
    tn = int(turn_number if turn_number is not None else commit.get("turn_number") or 0)
    tk = str(turn_kind or ("opening" if tn <= 0 else "player")).strip() or "player"
    scene_id = _short(commit.get("committed_scene_id") or graph.get("current_scene_id"), 64) or None
    return commit, graph, tn, tk, scene_id


def _not_applicable_forecast(
    *,
    story_session_id: str | None,
    module_id: str | None,
    runtime_profile_id: str | None,
    canonical_turn_id: str | None,
    turn_number: int,
    turn_kind: str,
    committed_scene_id: str | None,
    reason: str,
    source_inputs: list[dict[str, Any]] | None = None,
    thread_pressure_level: int = 0,
    dominant_thread_kind: str | None = None,
) -> dict[str, Any]:
    return _base_forecast(
        story_session_id=story_session_id,
        module_id=module_id,
        runtime_profile_id=runtime_profile_id,
        canonical_turn_id=canonical_turn_id,
        turn_number=turn_number,
        turn_kind=turn_kind,
        committed_scene_id=committed_scene_id,
        status="not_applicable",
        trigger_reasons=[reason],
        source_inputs=source_inputs or [],
        thread_pressure_level=thread_pressure_level,
        dominant_thread_kind=dominant_thread_kind,
    )


def _forecast_responders(
    *,
    selected_responder_set: list[Any] | None,
    actor_turn_summary: dict[str, Any] | None,
) -> list[Any]:
    responders = selected_responder_set if isinstance(selected_responder_set, list) else []
    actor_summary = actor_turn_summary if isinstance(actor_turn_summary, dict) else {}
    if responders:
        return responders
    primary = actor_summary.get("primary_responder_id")
    secondary = _str_list(actor_summary.get("secondary_responder_ids"), limit=4)
    return [primary, *secondary] if primary or secondary else []


def _forecast_pressure_inputs(
    *,
    commit: dict[str, Any],
    narrative_threads: Any,
    thread_metrics: dict[str, Any],
    selected_responder_set: list[Any] | None,
    actor_turn_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    source_inputs: list[dict[str, Any]] = []
    trigger_reasons: list[str] = []
    open_pressures = _str_list(commit.get("open_pressures"), limit=6)
    committed_consequences = _str_list(commit.get("committed_consequences"), limit=6)
    threads = _active_threads(narrative_threads)
    dominant = _dominant_thread(threads, thread_metrics)
    dominant_kind = _short(dominant.get("thread_kind"), 48) or None
    thread_pressure = int(thread_metrics.get("thread_pressure_level") or dominant.get("intensity") or 0)
    responders = _forecast_responders(
        selected_responder_set=selected_responder_set,
        actor_turn_summary=actor_turn_summary,
    )
    responder_count = len([item for item in responders if item])
    if open_pressures:
        _add_reason(trigger_reasons, "open_pressure_present")
        source_inputs.append(_source_input("narrative_commit.open_pressures", len(open_pressures), open_pressures[0]))
    if committed_consequences:
        source_inputs.append(
            _source_input(
                "narrative_commit.committed_consequences",
                len(committed_consequences),
                committed_consequences[0],
            )
        )
    _add_thread_forecast_reasons(
        trigger_reasons=trigger_reasons,
        source_inputs=source_inputs,
        threads=threads,
        dominant_kind=dominant_kind,
        thread_pressure=thread_pressure,
        commit=commit,
    )
    _add_planner_forecast_reasons(trigger_reasons, source_inputs, _as_dict(commit.get("planner_truth")))
    if responder_count > 1:
        _add_reason(trigger_reasons, "multi_responder_pressure")
        source_inputs.append(_source_input("selected_responder_set", responder_count))
    return {
        "source_inputs": source_inputs,
        "trigger_reasons": trigger_reasons,
        "threads": threads,
        "dominant_kind": dominant_kind,
        "thread_pressure": thread_pressure,
        "responder_count": responder_count,
    }


def _add_thread_forecast_reasons(
    *,
    trigger_reasons: list[str],
    source_inputs: list[dict[str, Any]],
    threads: list[dict[str, Any]],
    dominant_kind: str | None,
    thread_pressure: int,
    commit: dict[str, Any],
) -> None:
    if threads:
        _add_reason(trigger_reasons, "active_narrative_threads")
        source_inputs.append(_source_input("session.narrative_threads.active", len(threads), dominant_kind))
    if thread_pressure >= 4:
        _add_reason(trigger_reasons, "high_thread_pressure")
    if str(commit.get("situation_status") or "") == "blocked":
        _add_reason(trigger_reasons, "blocked_progression")


def _add_planner_forecast_reasons(
    trigger_reasons: list[str],
    source_inputs: list[dict[str, Any]],
    planner_truth: dict[str, Any],
) -> None:
    pressure_shift = _short(planner_truth.get("social_pressure_shift"), 48)
    social_outcome = _short(planner_truth.get("social_outcome"), 48)
    dramatic_direction = _short(planner_truth.get("dramatic_direction"), 48)
    if pressure_shift or social_outcome or dramatic_direction:
        _add_reason(trigger_reasons, "planner_pressure_signal")
        source_inputs.append(
            _source_input(
                "narrative_commit.planner_truth",
                1,
                pressure_shift or social_outcome or dramatic_direction,
            )
        )


def _branch_forecast_options(
    *,
    canonical_turn_id: str | None,
    story_session_id: str | None,
    turn_number: int,
    scene_id: str | None,
    trigger_reasons: list[str],
    dominant_kind: str | None,
    threads: list[dict[str, Any]],
    responder_count: int,
) -> list[dict[str, Any]]:
    seed = "|".join(
        [
            str(canonical_turn_id or story_session_id or ""),
            str(turn_number),
            str(scene_id or ""),
            "|".join(trigger_reasons),
        ]
    )
    tag_kind = f"thread:{dominant_kind}" if dominant_kind else "thread:unspecified"
    base_tags = ["branching_forecast", tag_kind]
    options = [
        _branch_option(
            seed=seed,
            family="press_pressure",
            label="press_unresolved_pressure",
            forecasted_consequence="The next turn can confront the unresolved pressure directly.",
            trigger_reasons=trigger_reasons,
            consequence_tags=[*base_tags, "pressure:increase"],
            pressure_delta={"dramatic_pressure": 1},
        ),
        _branch_option(
            seed=seed,
            family="repair_pressure",
            label="repair_or_deescalate",
            forecasted_consequence="The next turn can reduce pressure by repair, clarification, or restraint.",
            trigger_reasons=trigger_reasons,
            consequence_tags=[*base_tags, "pressure:decrease"],
            pressure_delta={"dramatic_pressure": -1},
        ),
    ]
    related_entities = _thread_entities(threads)
    if responder_count > 1 or related_entities:
        options.append(
            _branch_option(
                seed=seed,
                family="shift_focus",
                label="shift_actor_or_thread_focus",
                forecasted_consequence="The next turn can move attention to another implicated actor or thread.",
                trigger_reasons=trigger_reasons,
                consequence_tags=[*base_tags, "focus:shift"],
                pressure_delta={"focus_shift": 1},
            )
        )
    return options


def build_branching_forecast(
    *,
    story_session_id: str | None,
    module_id: str | None,
    runtime_profile_id: str | None = None,
    canonical_turn_id: str | None = None,
    turn_number: int | None = None,
    turn_kind: str | None = None,
    narrative_commit: Any = None,
    narrative_threads: Any = None,
    thread_metrics: dict[str, Any] | None = None,
    selected_responder_set: list[Any] | None = None,
    actor_turn_summary: dict[str, Any] | None = None,
    graph_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a bounded branch forecast from committed runtime truth.

    The returned object is JSON-safe and intentionally marked as non-authoritative.
    It describes possible next pressures; inactive options cannot change history.
    """

    commit, _graph, tn, tk, scene_id = _forecast_turn_context(
        turn_number=turn_number,
        turn_kind=turn_kind,
        narrative_commit=narrative_commit,
        graph_state=graph_state,
    )
    if tn <= 0 or tk in {"opening", "engine_opening"}:
        return _not_applicable_forecast(
            story_session_id=story_session_id,
            module_id=module_id,
            runtime_profile_id=runtime_profile_id,
            canonical_turn_id=canonical_turn_id,
            turn_number=tn,
            turn_kind=tk,
            committed_scene_id=scene_id,
            reason="opening_turn",
        )
    if bool(commit.get("is_terminal")) or str(commit.get("situation_status") or "") == "terminal":
        return _not_applicable_forecast(
            story_session_id=story_session_id,
            module_id=module_id,
            runtime_profile_id=runtime_profile_id,
            canonical_turn_id=canonical_turn_id,
            turn_number=tn,
            turn_kind=tk,
            committed_scene_id=scene_id,
            reason="terminal_turn",
        )

    metrics = thread_metrics if isinstance(thread_metrics, dict) else {}
    pressure = _forecast_pressure_inputs(
        commit=commit,
        narrative_threads=narrative_threads,
        thread_metrics=metrics,
        selected_responder_set=selected_responder_set,
        actor_turn_summary=actor_turn_summary,
    )

    if not pressure["trigger_reasons"]:
        return _not_applicable_forecast(
            story_session_id=story_session_id,
            module_id=module_id,
            runtime_profile_id=runtime_profile_id,
            canonical_turn_id=canonical_turn_id,
            turn_number=tn,
            turn_kind=tk,
            committed_scene_id=scene_id,
            reason="no_branching_pressure_signal",
            source_inputs=pressure["source_inputs"],
            thread_pressure_level=pressure["thread_pressure"],
            dominant_thread_kind=pressure["dominant_kind"],
        )

    options = _branch_forecast_options(
        canonical_turn_id=canonical_turn_id,
        story_session_id=story_session_id,
        turn_number=tn,
        scene_id=scene_id,
        trigger_reasons=pressure["trigger_reasons"],
        dominant_kind=pressure["dominant_kind"],
        threads=pressure["threads"],
        responder_count=pressure["responder_count"],
    )

    return _base_forecast(
        story_session_id=story_session_id,
        module_id=module_id,
        runtime_profile_id=runtime_profile_id,
        canonical_turn_id=canonical_turn_id,
        turn_number=tn,
        turn_kind=tk,
        committed_scene_id=scene_id,
        status="forecasted",
        trigger_reasons=pressure["trigger_reasons"],
        source_inputs=pressure["source_inputs"],
        options=options,
        thread_pressure_level=pressure["thread_pressure"],
        dominant_thread_kind=pressure["dominant_kind"],
    )
