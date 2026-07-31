"""Unsharded manager helper `_emit_langfuse_runtime_aspect_observability` (Wave 1)."""
from __future__ import annotations

from .._deps import *

def _emit_langfuse_runtime_aspect_observability(path_summary: dict[str, Any]) -> None:
    try:
        adapter = LangfuseAdapter.get_instance()
    except Exception:
        logger.debug("Langfuse adapter unavailable for runtime aspect observability", exc_info=True)
        return
    try:
        if not adapter or not adapter.is_enabled():
            return
    except Exception:
        return

    ledger_src = path_summary.get("turn_aspect_ledger")
    ledger_present = bool(
        isinstance(ledger_src, dict)
        and isinstance(ledger_src.get("turn_aspect_ledger"), dict)
    )
    ledger = normalize_runtime_aspect_ledger(ledger_src if isinstance(ledger_src, dict) else {
        "session_id": path_summary.get("session_id"),
        "module_id": path_summary.get("module_id"),
        "turn_number": path_summary.get("turn_number"),
        "turn_kind": path_summary.get("turn_kind"),
        "turn_aspect_ledger": {},
    })
    aspects = ledger.get("turn_aspect_ledger") if isinstance(ledger.get("turn_aspect_ledger"), dict) else {}

    def _rec(aspect: str) -> dict[str, Any]:
        row = aspects.get(aspect)
        return row if isinstance(row, dict) else {}

    def _expected(aspect: str) -> dict[str, Any]:
        row = _rec(aspect).get("expected")
        return row if isinstance(row, dict) else {}

    def _selected(aspect: str) -> dict[str, Any]:
        row = _rec(aspect).get("selected")
        return row if isinstance(row, dict) else {}

    def _actual(aspect: str) -> dict[str, Any]:
        row = _rec(aspect).get("actual")
        return row if isinstance(row, dict) else {}

    def _known(aspect: str) -> bool:
        return str(_rec(aspect).get("status") or "").strip() not in {"", "missing"}

    def _span_level(record: dict[str, Any]) -> str:
        status = str(record.get("status") or "").strip()
        if status == "failed":
            return "ERROR"
        if status in {"partial", "missing"}:
            return "WARNING"
        return "DEFAULT"

    def _span_status(aspect: str, record: dict[str, Any]) -> str:
        reason = str(record.get("failure_reason") or "").strip() or "none"
        return f"aspect={aspect} status={record.get('status') or 'missing'} reason={reason}"

    base_input = {
        "session_id": path_summary.get("session_id"),
        "module_id": path_summary.get("module_id"),
        "runtime_profile_id": ledger.get("runtime_profile_id") or path_summary.get("runtime_profile_id"),
        "turn_number": path_summary.get("turn_number"),
        "turn_kind": path_summary.get("turn_kind"),
        "raw_player_input": path_summary.get("raw_player_input"),
        "canonical_turn_id": path_summary.get("canonical_turn_id"),
        "environment": path_summary.get("environment"),
    }
    narrator_path_selected = bool(path_summary.get("narrator_path_selected")) or (
        str(path_summary.get("director_path_mode") or "").strip() == "narrator_path"
    )
    beat = _rec(ASPECT_BEAT)
    beat_selected = _selected(ASPECT_BEAT)
    beat_actual = _actual(ASPECT_BEAT)
    scene_energy_selected = _selected(ASPECT_SCENE_ENERGY)
    scene_energy_actual = _actual(ASPECT_SCENE_ENERGY)
    pacing_rhythm_selected = _selected(ASPECT_PACING_RHYTHM)
    pacing_rhythm_actual = _actual(ASPECT_PACING_RHYTHM)
    temporal_control_selected = _selected(ASPECT_TEMPORAL_CONTROL)
    temporal_control_actual = _actual(ASPECT_TEMPORAL_CONTROL)
    sensory_context_selected = _selected(ASPECT_SENSORY_CONTEXT)
    sensory_context_actual = _actual(ASPECT_SENSORY_CONTEXT)
    genre_awareness_selected = _selected(ASPECT_GENRE_AWARENESS)
    genre_awareness_actual = _actual(ASPECT_GENRE_AWARENESS)
    tonal_consistency_selected = _selected(ASPECT_TONAL_CONSISTENCY)
    tonal_consistency_actual = _actual(ASPECT_TONAL_CONSISTENCY)
    symbolic_object_selected = _selected(ASPECT_SYMBOLIC_OBJECT_RESONANCE)
    symbolic_object_actual = _actual(ASPECT_SYMBOLIC_OBJECT_RESONANCE)
    social_pressure_selected = _selected(ASPECT_SOCIAL_PRESSURE)
    social_pressure_actual = _actual(ASPECT_SOCIAL_PRESSURE)
    improvisational_selected = _selected(ASPECT_IMPROVISATIONAL_COHERENCE)
    improvisational_actual = _actual(ASPECT_IMPROVISATIONAL_COHERENCE)
    cap_selected = _selected(ASPECT_CAPABILITY_SELECTION)
    disclosure_selected = _selected(ASPECT_INFORMATION_DISCLOSURE)
    disclosure_actual = _actual(ASPECT_INFORMATION_DISCLOSURE)
    expectation_variation_selected = _selected(ASPECT_EXPECTATION_VARIATION)
    expectation_variation_actual = _actual(ASPECT_EXPECTATION_VARIATION)
    narrative_momentum_selected = _selected(ASPECT_NARRATIVE_MOMENTUM)
    narrative_momentum_actual = _actual(ASPECT_NARRATIVE_MOMENTUM)
    dramatic_irony_selected = _selected(ASPECT_DRAMATIC_IRONY)
    dramatic_irony_actual = _actual(ASPECT_DRAMATIC_IRONY)
    narrative_selected = _selected(ASPECT_NARRATIVE_ASPECT)
    narrative_actual = _actual(ASPECT_NARRATIVE_ASPECT)
    memory_selected = _selected(ASPECT_HIERARCHICAL_MEMORY)
    memory_actual = _actual(ASPECT_HIERARCHICAL_MEMORY)
    voice_expected = _expected(ASPECT_VOICE_CONSISTENCY)
    voice_actual = _actual(ASPECT_VOICE_CONSISTENCY)
    span_specs: list[tuple[str, str, dict[str, Any]]] = [
        ("story.aspect.input", ASPECT_INPUT, _rec(ASPECT_INPUT)),
        ("story.action.resolve", ASPECT_ACTION_RESOLUTION, _rec(ASPECT_ACTION_RESOLUTION)),
        (
            "story.affordance.evaluate",
            ASPECT_ACTION_RESOLUTION,
            {
                "affordance_status": _actual(ASPECT_ACTION_RESOLUTION).get("affordance_status"),
                "resolved_target_status": _actual(ASPECT_ACTION_RESOLUTION).get("resolved_target_status"),
                "action_commit_policy": _actual(ASPECT_ACTION_RESOLUTION).get("action_commit_policy"),
                "aspect_record": _rec(ASPECT_ACTION_RESOLUTION),
            },
        ),
        ("story.capability.select", ASPECT_CAPABILITY_SELECTION, _rec(ASPECT_CAPABILITY_SELECTION)),
        (
            "story.capability.realize",
            ASPECT_CAPABILITY_SELECTION,
            {
                "selected": cap_selected,
                "actual": _actual(ASPECT_CAPABILITY_SELECTION),
                "aspect_record": _rec(ASPECT_CAPABILITY_SELECTION),
            },
        ),
        (
            "story.beat.state",
            ASPECT_BEAT,
            {
                "prior_beat_id": _expected(ASPECT_BEAT).get("prior_beat_id"),
                "candidate_beats": _expected(ASPECT_BEAT).get("candidate_beats"),
                "aspect_record": beat,
            },
        ),
        ("story.beat.select", ASPECT_BEAT, {"selected": beat_selected, "aspect_record": beat}),
        ("story.beat.realize", ASPECT_BEAT, {"actual": beat_actual, "aspect_record": beat}),
        (
            "story.scene_energy.target",
            ASPECT_SCENE_ENERGY,
            {
                "selected": scene_energy_selected,
                "aspect_record": _rec(ASPECT_SCENE_ENERGY),
            },
        ),
        (
            "story.scene_energy.validate",
            ASPECT_SCENE_ENERGY,
            {
                "actual": scene_energy_actual,
                "aspect_record": _rec(ASPECT_SCENE_ENERGY),
            },
        ),
        (
            "story.pacing_rhythm.target",
            ASPECT_PACING_RHYTHM,
            {
                "selected": pacing_rhythm_selected,
                "aspect_record": _rec(ASPECT_PACING_RHYTHM),
            },
        ),
        (
            "story.pacing_rhythm.validate",
            ASPECT_PACING_RHYTHM,
            {
                "actual": pacing_rhythm_actual,
                "aspect_record": _rec(ASPECT_PACING_RHYTHM),
            },
        ),
        (
            "story.temporal_control.target",
            ASPECT_TEMPORAL_CONTROL,
            {
                "selected": temporal_control_selected,
                "aspect_record": _rec(ASPECT_TEMPORAL_CONTROL),
            },
        ),
        (
            "story.temporal_control.validate",
            ASPECT_TEMPORAL_CONTROL,
            {
                "actual": temporal_control_actual,
                "aspect_record": _rec(ASPECT_TEMPORAL_CONTROL),
            },
        ),
        (
            "story.sensory_context.target",
            ASPECT_SENSORY_CONTEXT,
            {
                "selected": sensory_context_selected,
                "aspect_record": _rec(ASPECT_SENSORY_CONTEXT),
            },
        ),
        (
            "story.sensory_context.validate",
            ASPECT_SENSORY_CONTEXT,
            {
                "actual": sensory_context_actual,
                "aspect_record": _rec(ASPECT_SENSORY_CONTEXT),
            },
        ),
        (
            "story.genre_awareness.target",
            ASPECT_GENRE_AWARENESS,
            {
                "selected": genre_awareness_selected,
                "aspect_record": _rec(ASPECT_GENRE_AWARENESS),
            },
        ),
        (
            "story.genre_awareness.validate",
            ASPECT_GENRE_AWARENESS,
            {
                "actual": genre_awareness_actual,
                "aspect_record": _rec(ASPECT_GENRE_AWARENESS),
            },
        ),
        (
            "story.tonal_consistency.target",
            ASPECT_TONAL_CONSISTENCY,
            {
                "selected": tonal_consistency_selected,
                "aspect_record": _rec(ASPECT_TONAL_CONSISTENCY),
            },
        ),
        (
            "story.tonal_consistency.validate",
            ASPECT_TONAL_CONSISTENCY,
            {
                "actual": tonal_consistency_actual,
                "aspect_record": _rec(ASPECT_TONAL_CONSISTENCY),
            },
        ),
        (
            "story.symbolic_object_resonance.target",
            ASPECT_SYMBOLIC_OBJECT_RESONANCE,
            {
\
                "selected": symbolic_object_selected,
                "aspect_record": _rec(ASPECT_SYMBOLIC_OBJECT_RESONANCE),
            },
        ),
        (
            "story.symbolic_object_resonance.validate",
            ASPECT_SYMBOLIC_OBJECT_RESONANCE,
            {
                "actual": symbolic_object_actual,
                "aspect_record": _rec(ASPECT_SYMBOLIC_OBJECT_RESONANCE),
            },
        ),
        (
            "story.social_pressure.target",
            ASPECT_SOCIAL_PRESSURE,
            {
                "selected": social_pressure_selected,
                "aspect_record": _rec(ASPECT_SOCIAL_PRESSURE),
            },
        ),
        (
            "story.social_pressure.validate",
            ASPECT_SOCIAL_PRESSURE,
            {
                "actual": social_pressure_actual,
                "aspect_record": _rec(ASPECT_SOCIAL_PRESSURE),
            },
        ),
        (
            "story.improvisational_coherence.target",
            ASPECT_IMPROVISATIONAL_COHERENCE,
            {
                "selected": improvisational_selected,
                "aspect_record": _rec(ASPECT_IMPROVISATIONAL_COHERENCE),
            },
        ),
        (
            "story.improvisational_coherence.validate",
            ASPECT_IMPROVISATIONAL_COHERENCE,
            {
                "actual": improvisational_actual,
                "aspect_record": _rec(ASPECT_IMPROVISATIONAL_COHERENCE),
            },
        ),
        (
            "story.information_disclosure.select",
            ASPECT_INFORMATION_DISCLOSURE,
            {
                "selected": disclosure_selected,
                "aspect_record": _rec(ASPECT_INFORMATION_DISCLOSURE),
            },
        ),
        (
            "story.information_disclosure.validate",
            ASPECT_INFORMATION_DISCLOSURE,
            {
                "actual": disclosure_actual,
                "aspect_record": _rec(ASPECT_INFORMATION_DISCLOSURE),
            },
        ),
        (
            "story.expectation_variation.select",
            ASPECT_EXPECTATION_VARIATION,
            {
                "selected": expectation_variation_selected,
                "aspect_record": _rec(ASPECT_EXPECTATION_VARIATION),
            },
        ),
        (
            "story.expectation_variation.validate",
            ASPECT_EXPECTATION_VARIATION,
            {
                "actual": expectation_variation_actual,
                "aspect_record": _rec(ASPECT_EXPECTATION_VARIATION),
            },
        ),
        (
            "story.narrative_momentum.target",
            ASPECT_NARRATIVE_MOMENTUM,
            {
                "selected": narrative_momentum_selected,
                "aspect_record": _rec(ASPECT_NARRATIVE_MOMENTUM),
            },
        ),
        (
            "story.narrative_momentum.validate",
            ASPECT_NARRATIVE_MOMENTUM,
            {
                "actual": narrative_momentum_actual,
                "aspect_record": _rec(ASPECT_NARRATIVE_MOMENTUM),
            },
        ),
        (
            "story.dramatic_irony.select",
            ASPECT_DRAMATIC_IRONY,
            {
                "selected": dramatic_irony_selected,
                "aspect_record": _rec(ASPECT_DRAMATIC_IRONY),
            },
        ),
        (
            "story.dramatic_irony.validate",
            ASPECT_DRAMATIC_IRONY,
            {
                "actual": dramatic_irony_actual,
                "aspect_record": _rec(ASPECT_DRAMATIC_IRONY),
            },
        ),
        ("story.authority.narrator", ASPECT_NARRATOR_AUTHORITY, _rec(ASPECT_NARRATOR_AUTHORITY)),
        ("story.authority.npc", ASPECT_NPC_AUTHORITY, _rec(ASPECT_NPC_AUTHORITY)),
        (
            "story.npc_agency.plan",
            ASPECT_NPC_AGENCY,
            {
                "expected": _expected(ASPECT_NPC_AGENCY),
                "selected": _selected(ASPECT_NPC_AGENCY),
                "aspect_record": _rec(ASPECT_NPC_AGENCY),
            },
        ),
        (
            "story.npc_agency.realize",
            ASPECT_NPC_AGENCY,
            {
                "actual": _actual(ASPECT_NPC_AGENCY),
                "aspect_record": _rec(ASPECT_NPC_AGENCY),
            },
        ),
        (
            "story.narrative_aspect.select",
            ASPECT_NARRATIVE_ASPECT,
            {"selected": narrative_selected, "aspect_record": _rec(ASPECT_NARRATIVE_ASPECT)},
        ),
        (
            "story.narrative_aspect.validate",
            ASPECT_NARRATIVE_ASPECT,
            {"actual": narrative_actual, "aspect_record": _rec(ASPECT_NARRATIVE_ASPECT)},
        ),
        (
            "story.voice.classify",
            ASPECT_VOICE_CONSISTENCY,
            {
                "expected": voice_expected,
                "actual": voice_actual,
                "aspect_record": _rec(ASPECT_VOICE_CONSISTENCY),
            },
        ),
        (
            "story.voice.validate",
            ASPECT_VOICE_CONSISTENCY,
            {
                "findings": voice_actual.get("findings") or [],
                "semantic_classifications": voice_actual.get("semantic_classifications") or [],
                "aspect_record": _rec(ASPECT_VOICE_CONSISTENCY),
            },
        ),
        (
            "story.memory.write",
            ASPECT_HIERARCHICAL_MEMORY,
            {"selected": memory_selected, "actual": memory_actual, "aspect_record": _rec(ASPECT_HIERARCHICAL_MEMORY)},
        ),
        (
            "story.memory.project",
            ASPECT_HIERARCHICAL_MEMORY,
            {"actual": memory_actual, "aspect_record": _rec(ASPECT_HIERARCHICAL_MEMORY)},
        ),
        ("story.validation.contract", ASPECT_VALIDATION, _rec(ASPECT_VALIDATION)),
        ("story.commit.apply", ASPECT_COMMIT, _rec(ASPECT_COMMIT)),
        ("story.visible.project", ASPECT_VISIBLE_PROJECTION, _rec(ASPECT_VISIBLE_PROJECTION)),
        (
            "story.turn.aspect_summary",
            ASPECT_INPUT,
            {
                "turn_aspect_ledger_present": ledger_present,
                "canonical_turn_id": path_summary.get("canonical_turn_id"),
                "aspect_statuses": {
                    aspect_name: (_rec(aspect_name).get("status") or "missing")
                    for aspect_name in (
                        ASPECT_INPUT,
                        ASPECT_ACTION_RESOLUTION,
                        ASPECT_BEAT,
                        ASPECT_SCENE_ENERGY,
                        ASPECT_PACING_RHYTHM,
                        ASPECT_TEMPORAL_CONTROL,
                        ASPECT_SENSORY_CONTEXT,
                        ASPECT_GENRE_AWARENESS,
                        ASPECT_TONAL_CONSISTENCY,
                        ASPECT_IMPROVISATIONAL_COHERENCE,
                        ASPECT_INFORMATION_DISCLOSURE,
                        ASPECT_EXPECTATION_VARIATION,
                        ASPECT_NARRATIVE_MOMENTUM,
                        ASPECT_CAPABILITY_SELECTION,
                        ASPECT_NARRATOR_AUTHORITY,
                        ASPECT_NPC_AUTHORITY,
                        ASPECT_NPC_AGENCY,
                        ASPECT_NARRATIVE_ASPECT,
                        ASPECT_VOICE_CONSISTENCY,
                        ASPECT_HIERARCHICAL_MEMORY,
                        ASPECT_VALIDATION,
                        ASPECT_COMMIT,
                        ASPECT_VISIBLE_PROJECTION,
                    )
                },
            },
        ),
    ]
    for name, aspect, output in span_specs:
        record = _rec(aspect)
        if narrator_path_selected:
            narrator_path_span_names = {
                "story.aspect.input",
                "story.authority.narrator",
                "story.narrative_aspect.select",
                "story.narrative_aspect.validate",
                "story.validation.contract",
                "story.commit.apply",
                "story.visible.project",
                "story.turn.aspect_summary",
            }
            if name not in narrator_path_span_names:
                continue
        level = _span_level(record)
        status_message = _span_status(aspect, record)
        try:
            span = adapter.create_child_span(
                name=name,
                input=base_input,
                output=output,
                metadata={
                    "phase": "runtime_aspect",
                    "runtime_aspect": aspect,
                    "module_id": path_summary.get("module_id"),
                    "runtime_profile_id": ledger.get("runtime_profile_id") or path_summary.get("runtime_profile_id"),
                    "turn_number": path_summary.get("turn_number"),
                    "session_id": path_summary.get("session_id"),
                    "canonical_turn_id": path_summary.get("canonical_turn_id"),
                    "selected_beat_id": beat_selected.get("selected_beat_id"),
                    "selected_capabilities": cap_selected.get("selected_capabilities") or [],
                    "authority_policy": _expected(ASPECT_NPC_AUTHORITY).get("policy"),
                    "status": record.get("status"),
                    "failure_reason": record.get("failure_reason"),
\
                    "trace_origin": path_summary.get("trace_origin"),
                    "execution_tier": path_summary.get("execution_tier"),
                    "canonical_player_flow": path_summary.get("canonical_player_flow"),
                },
                level=level,
                status_message=status_message,
            )
        except Exception:
            logger.debug("Langfuse runtime aspect span creation failed for %s", name, exc_info=True)
            continue
        _finish_langfuse_span(span, output=output, level=level, status_message=status_message)

    input_actual = _actual(ASPECT_INPUT)
    action_actual = _actual(ASPECT_ACTION_RESOLUTION)
    narrator_expected = _expected(ASPECT_NARRATOR_AUTHORITY)
    narrator_actual = _actual(ASPECT_NARRATOR_AUTHORITY)
    npc_actual = _actual(ASPECT_NPC_AUTHORITY)
    npc_agency_actual = _actual(ASPECT_NPC_AGENCY)
    dramatic_irony_expected = _expected(ASPECT_DRAMATIC_IRONY)
    dramatic_irony_actual = _actual(ASPECT_DRAMATIC_IRONY)
    cap_actual = _actual(ASPECT_CAPABILITY_SELECTION)
    visible_actual = _actual(ASPECT_VISIBLE_PROJECTION)
    narrative_expected = _expected(ASPECT_NARRATIVE_ASPECT)
    memory_expected = _expected(ASPECT_HIERARCHICAL_MEMORY)
    voice_expected = _expected(ASPECT_VOICE_CONSISTENCY)
    voice_actual = _actual(ASPECT_VOICE_CONSISTENCY)
    validation_actual = _actual(ASPECT_VALIDATION)
    beat_transition_allowed = _selected(ASPECT_BEAT).get("transition_allowed")
    scene_energy_target = (
        scene_energy_selected.get("target")
        if isinstance(scene_energy_selected.get("target"), dict)
        else scene_energy_selected
    )
    scene_energy_failure_codes = scene_energy_actual.get("failure_codes") or []
    if not isinstance(scene_energy_failure_codes, list):
        scene_energy_failure_codes = []
    pacing_rhythm_target = (
        pacing_rhythm_selected.get("target")
        if isinstance(pacing_rhythm_selected.get("target"), dict)
        else pacing_rhythm_selected
    )
    pacing_rhythm_failure_codes = pacing_rhythm_actual.get("failure_codes") or []
    if not isinstance(pacing_rhythm_failure_codes, list):
        pacing_rhythm_failure_codes = []
    temporal_control_target = (
        temporal_control_selected.get("target")
        if isinstance(temporal_control_selected.get("target"), dict)
        else temporal_control_selected
    )
    temporal_control_failure_codes = temporal_control_actual.get("failure_codes") or []
    if not isinstance(temporal_control_failure_codes, list):
        temporal_control_failure_codes = []
    sensory_context_target = (
        sensory_context_selected.get("target")
        if isinstance(sensory_context_selected.get("target"), dict)
        else sensory_context_selected
    )
    sensory_context_failure_codes = sensory_context_actual.get("failure_codes") or []
    if not isinstance(sensory_context_failure_codes, list):
        sensory_context_failure_codes = []
    genre_awareness_target = (
        genre_awareness_selected.get("target")
        if isinstance(genre_awareness_selected.get("target"), dict)
        else genre_awareness_selected
    )
    genre_awareness_failure_codes = genre_awareness_actual.get("failure_codes") or []
    if not isinstance(genre_awareness_failure_codes, list):
        genre_awareness_failure_codes = []
    tonal_consistency_target = (
        tonal_consistency_selected.get("target")
        if isinstance(tonal_consistency_selected.get("target"), dict)
        else tonal_consistency_selected
    )
    tonal_consistency_failure_codes = tonal_consistency_actual.get("failure_codes") or []
    if not isinstance(tonal_consistency_failure_codes, list):
        tonal_consistency_failure_codes = []
    symbolic_object_target = (
        symbolic_object_selected.get("target")
        if isinstance(symbolic_object_selected.get("target"), dict)
        else symbolic_object_selected
    )
    symbolic_object_failure_codes = symbolic_object_actual.get("failure_codes") or []
    if not isinstance(symbolic_object_failure_codes, list):
        symbolic_object_failure_codes = []
    improvisational_failure_codes = improvisational_actual.get("failure_codes") or []
    if not isinstance(improvisational_failure_codes, list):
        improvisational_failure_codes = []
    social_pressure_target = (
        social_pressure_selected.get("target")
        if isinstance(social_pressure_selected.get("target"), dict)
        else social_pressure_selected
    )
    social_pressure_failure_codes = social_pressure_actual.get("failure_codes") or []
    if not isinstance(social_pressure_failure_codes, list):
        social_pressure_failure_codes = []
    disclosure_failure_codes = disclosure_actual.get("failure_codes") or []
    if not isinstance(disclosure_failure_codes, list):
        disclosure_failure_codes = []
    expectation_variation_failure_codes = (
        expectation_variation_actual.get("failure_codes") or []
    )
    if not isinstance(expectation_variation_failure_codes, list):
        expectation_variation_failure_codes = []
    narrative_momentum_target = (
        narrative_momentum_selected.get("target")
        if isinstance(narrative_momentum_selected.get("target"), dict)
        else narrative_momentum_selected
    )
    narrative_momentum_failure_codes = narrative_momentum_actual.get("failure_codes") or []
    if not isinstance(narrative_momentum_failure_codes, list):
        narrative_momentum_failure_codes = []
    try:
        narrative_momentum_progress_event_count = int(
            narrative_momentum_actual.get("progress_event_count") or 0
        )
    except (TypeError, ValueError):
        narrative_momentum_progress_event_count = 0
    try:
        narrative_momentum_min_progress_event_count = int(
            narrative_momentum_target.get("min_progress_event_count") or 0
        )
    except (TypeError, ValueError):
        narrative_momentum_min_progress_event_count = 0
    dramatic_irony_violation_codes = dramatic_irony_actual.get("violation_codes") or []
    if not isinstance(dramatic_irony_violation_codes, list):
        dramatic_irony_violation_codes = []
    npc_failure_reason = str(_rec(ASPECT_NPC_AUTHORITY).get("failure_reason") or "")
    violated_capabilities = cap_actual.get("violated_capabilities") or []
    if not isinstance(violated_capabilities, list):
        violated_capabilities = []
    turn_number = int(path_summary.get("turn_number") or ledger.get("turn_number") or 0)
    input_kind = str(
        action_actual.get("input_kind")
        or input_actual.get("player_input_kind")
        or input_actual.get("input_kind")
        or ""
    ).strip().lower()
    action_requires_narrator = turn_number > 0 and input_kind in {
        "action",
        "perception",
        "mixed",
        "movement_action",
        "perception_action",
    }
    narrator_required = bool(narrator_expected.get("required"))
    missing_required_capabilities = cap_actual.get("missing_required_capabilities") or []
    if not isinstance(missing_required_capabilities, list):
        missing_required_capabilities = []
    selected_theme_aspects = narrative_actual.get("selected_theme_aspects") or []
    if not isinstance(selected_theme_aspects, list):
        selected_theme_aspects = []
    narrative_semantic_classification_count = int(
        narrative_actual.get("semantic_classification_count") or 0
    )
    narrative_semantic_required_weak_alignment_count = int(
        narrative_actual.get("semantic_required_weak_alignment_count") or 0
    )
    voice_spoken_line_count = int(voice_actual.get("spoken_line_count") or 0)
    voice_semantic_classification_count = int(
        voice_actual.get("semantic_classification_count") or 0
    )
    voice_drift_counts = (
        voice_actual.get("drift_class_counts")
        if isinstance(voice_actual.get("drift_class_counts"), dict)
        else {}
    )
    voice_forbidden_marker_count = int(
        voice_drift_counts.get("forbidden_language_marker") or 0
    )
    voice_cross_actor_count = int(
        voice_actual.get("semantic_cross_actor_confusion_count")
        or voice_drift_counts.get("cross_actor_voice_confusion")
        or 0
    )
    recoverable_turn = bool(validation_actual.get("recoverable_rejection")) or str(
        path_summary.get("turn_status") or ""
    ).strip().lower() in {"rejected_recoverable", "player_rejected_recoverable"}
    http_status = int(path_summary.get("http_status") or 200)
    visible_output_for_recovery = bool(
        visible_actual.get("visible_output_present")
        or visible_actual.get("visible_block_origin_present")
        or int(visible_actual.get("scene_block_count") or 0) > 0
    )
    scores: list[tuple[str, str, float]] = [
        ("turn_aspect_ledger_present", ASPECT_INPUT, _runtime_aspect_score_value(ledger_present)),
        (
            "beat_selected",
            ASPECT_BEAT,
            _runtime_aspect_score_value(bool(beat_selected.get("selected_beat_id") or beat_selected.get("selected_scene_function"))),
        ),
        ("beat_realized", ASPECT_BEAT, _runtime_aspect_score_value(beat_actual.get("realized") is True)),
        (
            "beat_realization_visible",
            ASPECT_BEAT,
            _runtime_aspect_score_value(beat_actual.get("realized") is True and beat_actual.get("visible") is True),
        ),
        (
            "beat_transition_valid",
            ASPECT_BEAT,
            _runtime_aspect_score_value(beat_transition_allowed is not False),
        ),
        (
            "beat_contract_pass",
            ASPECT_BEAT,
            _runtime_aspect_score_value(_rec(ASPECT_BEAT).get("status") == "passed"),
        ),
        (
            "scene_energy_target_present",
            ASPECT_SCENE_ENERGY,
            _runtime_aspect_score_value(bool(scene_energy_target)),
        ),
        (
            "scene_energy_contract_pass",
            ASPECT_SCENE_ENERGY,
            _runtime_aspect_score_value(
                _rec(ASPECT_SCENE_ENERGY).get("status") in {"passed", "not_applicable"}
            ),
        ),
        (
            "scene_energy_transition_allowed",
            ASPECT_SCENE_ENERGY,
            _runtime_aspect_score_value(scene_energy_actual.get("transition_allowed") is not False),
        ),
        (
            "scene_energy_pressure_realized",
            ASPECT_SCENE_ENERGY,
            _runtime_aspect_score_value(
                "scene_energy_missing_required_pressure" not in scene_energy_failure_codes
            ),
        ),
        (
            "pacing_rhythm_target_present",
            ASPECT_PACING_RHYTHM,
            _runtime_aspect_score_value(bool(pacing_rhythm_target)),
        ),
        (
            "pacing_rhythm_contract_pass",
            ASPECT_PACING_RHYTHM,
            _runtime_aspect_score_value(
                _rec(ASPECT_PACING_RHYTHM).get("status") in {"passed", "not_applicable"}
\
            ),
        ),
        (
            "pacing_rhythm_density_respected",
            ASPECT_PACING_RHYTHM,
            _runtime_aspect_score_value(
                "pacing_rhythm_visible_density_exceeded" not in pacing_rhythm_failure_codes
            ),
        ),
        (
            "pacing_rhythm_pause_respected",
            ASPECT_PACING_RHYTHM,
            _runtime_aspect_score_value(
                "pacing_rhythm_pause_obligation_lost" not in pacing_rhythm_failure_codes
                and "pacing_rhythm_forced_speech_violation" not in pacing_rhythm_failure_codes
            ),
        ),
        (
            "temporal_control_policy_present",
            ASPECT_TEMPORAL_CONTROL,
            _runtime_aspect_score_value(
                bool(_expected(ASPECT_TEMPORAL_CONTROL).get("policy_present"))
            ),
        ),
        (
            "temporal_control_target_selected",
            ASPECT_TEMPORAL_CONTROL,
            _runtime_aspect_score_value(bool(temporal_control_target.get("operation"))),
        ),
        (
            "temporal_control_operation_allowed",
            ASPECT_TEMPORAL_CONTROL,
            _runtime_aspect_score_value(
                "temporal_control_operation_not_allowed"
                not in temporal_control_failure_codes
            ),
        ),
        (
            "temporal_control_committed_sources_bounded",
            ASPECT_TEMPORAL_CONTROL,
            _runtime_aspect_score_value(
                "temporal_control_uncommitted_source"
                not in temporal_control_failure_codes
                and "temporal_control_unbounded_jump"
                not in temporal_control_failure_codes
            ),
        ),
        (
            "temporal_control_history_rewrite_absent",
            ASPECT_TEMPORAL_CONTROL,
            _runtime_aspect_score_value(
                "temporal_control_history_rewrite_attempt"
                not in temporal_control_failure_codes
                and "temporal_control_branch_state_adoption"
                not in temporal_control_failure_codes
            ),
        ),
        (
            "temporal_control_contract_pass",
            ASPECT_TEMPORAL_CONTROL,
            _runtime_aspect_score_value(
                _rec(ASPECT_TEMPORAL_CONTROL).get("status")
                in {"passed", "not_applicable"}
                and temporal_control_actual.get("contract_pass") is not False
                and not temporal_control_failure_codes
            ),
        ),
        (
            "sensory_context_target_present",
            ASPECT_SENSORY_CONTEXT,
            _runtime_aspect_score_value(bool(sensory_context_target)),
        ),
        (
            "sensory_context_contract_pass",
            ASPECT_SENSORY_CONTEXT,
            _runtime_aspect_score_value(
                _rec(ASPECT_SENSORY_CONTEXT).get("status") in {"passed", "not_applicable"}
            ),
        ),
        (
            "sensory_context_required_layers_realized",
            ASPECT_SENSORY_CONTEXT,
            _runtime_aspect_score_value(
                "sensory_context_missing_required_layer" not in sensory_context_failure_codes
                and "sensory_context_structured_event_missing" not in sensory_context_failure_codes
            ),
        ),
        (
            "sensory_context_source_refs_valid",
            ASPECT_SENSORY_CONTEXT,
            _runtime_aspect_score_value(
                "sensory_context_source_ref_mismatch" not in sensory_context_failure_codes
                and "sensory_context_unselected_layer" not in sensory_context_failure_codes
            ),
        ),
        (
            "genre_awareness_policy_present",
            ASPECT_GENRE_AWARENESS,
            _runtime_aspect_score_value(
                bool(_expected(ASPECT_GENRE_AWARENESS).get("policy_present"))
            ),
        ),
        (
            "genre_awareness_target_selected",
            ASPECT_GENRE_AWARENESS,
            _runtime_aspect_score_value(bool(genre_awareness_target.get("genre_profile_id"))),
        ),
        (
            "genre_awareness_registers_valid",
            ASPECT_GENRE_AWARENESS,
            _runtime_aspect_score_value(
                "genre_awareness_register_not_allowed" not in genre_awareness_failure_codes
            ),
        ),
        (
            "genre_awareness_required_conventions_realized",
            ASPECT_GENRE_AWARENESS,
            _runtime_aspect_score_value(
                "genre_awareness_missing_required_convention"
                not in genre_awareness_failure_codes
                and "genre_awareness_missing_required_event"
                not in genre_awareness_failure_codes
            ),
        ),
        (
            "genre_awareness_forbidden_markers_absent",
            ASPECT_GENRE_AWARENESS,
            _runtime_aspect_score_value(
                "genre_awareness_forbidden_marker" not in genre_awareness_failure_codes
            ),
        ),
        (
            "genre_awareness_contract_pass",
            ASPECT_GENRE_AWARENESS,
            _runtime_aspect_score_value(
                _rec(ASPECT_GENRE_AWARENESS).get("status") in {"passed", "not_applicable"}
                and genre_awareness_actual.get("contract_pass") is not False
            ),
        ),
        (
            "tonal_consistency_policy_present",
            ASPECT_TONAL_CONSISTENCY,
            _runtime_aspect_score_value(
                bool(_expected(ASPECT_TONAL_CONSISTENCY).get("policy_present"))
            ),
        ),
        (
            "tonal_consistency_target_selected",
            ASPECT_TONAL_CONSISTENCY,
            _runtime_aspect_score_value(bool(tonal_consistency_target.get("profile_id"))),
        ),
        (
            "tonal_consistency_independent_classification_present",
            ASPECT_TONAL_CONSISTENCY,
            _runtime_aspect_score_value(
                bool(tonal_consistency_actual.get("structured_classification_present"))
                and tonal_consistency_actual.get("independent_classifier") is not False
            ),
        ),
        (
            "tonal_consistency_classification_present",
            ASPECT_TONAL_CONSISTENCY,
            _runtime_aspect_score_value(
                bool(tonal_consistency_actual.get("structured_classification_present"))
                and tonal_consistency_actual.get("independent_classifier") is not False
            ),
        ),
        (
            "tonal_consistency_marker_hits_absent",
            ASPECT_TONAL_CONSISTENCY,
            _runtime_aspect_score_value(
                "tonal_consistency_forbidden_marker_detected"
                not in tonal_consistency_failure_codes
            ),
        ),
        (
            "tonal_consistency_contract_pass",
            ASPECT_TONAL_CONSISTENCY,
            _runtime_aspect_score_value(
                _rec(ASPECT_TONAL_CONSISTENCY).get("status")
                in {"passed", "not_applicable"}
                and tonal_consistency_actual.get("contract_pass") is not False
                and not tonal_consistency_failure_codes
            ),
        ),
        (
            "symbolic_object_resonance_policy_present",
            ASPECT_SYMBOLIC_OBJECT_RESONANCE,
            _runtime_aspect_score_value(
                bool(_expected(ASPECT_SYMBOLIC_OBJECT_RESONANCE).get("policy_present"))
            ),
        ),
        (
            "symbolic_object_resonance_target_selected",
            ASPECT_SYMBOLIC_OBJECT_RESONANCE,
            _runtime_aspect_score_value(
                bool(symbolic_object_selected.get("selected_object_ids"))
            ),
        ),
        (
            "symbolic_object_resonance_source_refs_valid",
            ASPECT_SYMBOLIC_OBJECT_RESONANCE,
            _runtime_aspect_score_value(
                "symbolic_object_resonance_source_ref_mismatch"
                not in symbolic_object_failure_codes
                and "symbolic_object_resonance_unselected_object"
                not in symbolic_object_failure_codes
            ),
        ),
        (
            "symbolic_object_resonance_budget_pass",
            ASPECT_SYMBOLIC_OBJECT_RESONANCE,
            _runtime_aspect_score_value(
                "symbolic_object_resonance_budget_exceeded"
                not in symbolic_object_failure_codes
            ),
        ),
        (
            "symbolic_object_resonance_contract_pass",
            ASPECT_SYMBOLIC_OBJECT_RESONANCE,
            _runtime_aspect_score_value(
                _rec(ASPECT_SYMBOLIC_OBJECT_RESONANCE).get("status")
                in {"passed", "not_applicable"}
                and symbolic_object_actual.get("contract_pass") is not False
                and not symbolic_object_failure_codes
            ),
        ),
        (
            "improvisational_coherence_policy_present",
            ASPECT_IMPROVISATIONAL_COHERENCE,
            _runtime_aspect_score_value(
                bool(_expected(ASPECT_IMPROVISATIONAL_COHERENCE).get("policy_present"))
            ),
        ),
        (
            "improvisational_coherence_target_selected",
            ASPECT_IMPROVISATIONAL_COHERENCE,
            _runtime_aspect_score_value(
                bool(
                    improvisational_selected.get("contribution_id")
\
                    or improvisational_selected.get("acceptance_mode")
                    or improvisational_selected.get("required_anchor_refs")
                )
            ),
        ),
        (
            "improvisational_coherence_acknowledged",
            ASPECT_IMPROVISATIONAL_COHERENCE,
            _runtime_aspect_score_value(
                _rec(ASPECT_IMPROVISATIONAL_COHERENCE).get("status")
                in {"passed", "not_applicable"}
                and "improv_player_contribution_dropped" not in improvisational_failure_codes
            ),
        ),
        (
            "improvisational_coherence_scene_anchor_preserved",
            ASPECT_IMPROVISATIONAL_COHERENCE,
            _runtime_aspect_score_value(
                "improv_scene_anchor_missing" not in improvisational_failure_codes
            ),
        ),
        (
            "improvisational_coherence_contract_pass",
            ASPECT_IMPROVISATIONAL_COHERENCE,
            _runtime_aspect_score_value(
                _rec(ASPECT_IMPROVISATIONAL_COHERENCE).get("status")
                in {"passed", "not_applicable"}
                and improvisational_actual.get("contract_pass") is not False
                and not improvisational_failure_codes
            ),
        ),
        (
            "social_pressure_target_present",
            ASPECT_SOCIAL_PRESSURE,
            _runtime_aspect_score_value(bool(social_pressure_target)),
        ),
        (
            "social_pressure_contract_pass",
            ASPECT_SOCIAL_PRESSURE,
            _runtime_aspect_score_value(
                _rec(ASPECT_SOCIAL_PRESSURE).get("status") in {"passed", "not_applicable"}
            ),
        ),
        (
            "social_pressure_metric_bounded",
            ASPECT_SOCIAL_PRESSURE,
            _runtime_aspect_score_value(
                "social_pressure_score_out_of_bounds" not in social_pressure_failure_codes
            ),
        ),
        (
            "information_disclosure_policy_present",
            ASPECT_INFORMATION_DISCLOSURE,
            _runtime_aspect_score_value(
                bool(_expected(ASPECT_INFORMATION_DISCLOSURE).get("policy_present"))
            ),
        ),
        (
            "information_disclosure_target_selected",
            ASPECT_INFORMATION_DISCLOSURE,
            _runtime_aspect_score_value(bool(disclosure_selected.get("selected_unit_ids"))),
        ),
        (
            "information_disclosure_budget_pass",
            ASPECT_INFORMATION_DISCLOSURE,
            _runtime_aspect_score_value(
                "information_disclosure_over_budget" not in disclosure_failure_codes
            ),
        ),
        (
            "information_disclosure_premature_reveal_absent",
            ASPECT_INFORMATION_DISCLOSURE,
            _runtime_aspect_score_value(
                "information_disclosure_forbidden_unit" not in disclosure_failure_codes
            ),
        ),
        (
            "information_disclosure_contract_pass",
            ASPECT_INFORMATION_DISCLOSURE,
            _runtime_aspect_score_value(
                _rec(ASPECT_INFORMATION_DISCLOSURE).get("status")
                in {"passed", "not_applicable"}
                and disclosure_actual.get("contract_pass") is not False
                and not disclosure_failure_codes
            ),
        ),
        (
            "expectation_variation_policy_present",
            ASPECT_EXPECTATION_VARIATION,
            _runtime_aspect_score_value(
                bool(_expected(ASPECT_EXPECTATION_VARIATION).get("policy_present"))
            ),
        ),
        (
            "expectation_variation_target_selected",
            ASPECT_EXPECTATION_VARIATION,
            _runtime_aspect_score_value(
                bool(expectation_variation_selected.get("selected_variation_ids"))
            ),
        ),
        (
            "expectation_variation_budget_pass",
            ASPECT_EXPECTATION_VARIATION,
            _runtime_aspect_score_value(
                "expectation_variation_over_budget"
                not in expectation_variation_failure_codes
            ),
        ),
        (
            "expectation_variation_setup_supported",
            ASPECT_EXPECTATION_VARIATION,
            _runtime_aspect_score_value(
                "expectation_variation_unearned_event"
                not in expectation_variation_failure_codes
                and "expectation_variation_target_mismatch"
                not in expectation_variation_failure_codes
            ),
        ),
        (
            "expectation_variation_contract_pass",
            ASPECT_EXPECTATION_VARIATION,
            _runtime_aspect_score_value(
                _rec(ASPECT_EXPECTATION_VARIATION).get("status")
                in {"passed", "not_applicable"}
                and expectation_variation_actual.get("contract_pass") is not False
                and not expectation_variation_failure_codes
            ),
        ),
        (
            "narrative_momentum_policy_present",
            ASPECT_NARRATIVE_MOMENTUM,
            _runtime_aspect_score_value(
                bool(_expected(ASPECT_NARRATIVE_MOMENTUM).get("policy_present"))
            ),
        ),
        (
            "narrative_momentum_target_selected",
            ASPECT_NARRATIVE_MOMENTUM,
            _runtime_aspect_score_value(bool(narrative_momentum_target.get("target_state"))),
        ),
        (
            "narrative_momentum_transition_allowed",
            ASPECT_NARRATIVE_MOMENTUM,
            _runtime_aspect_score_value(
                narrative_momentum_actual.get("transition_allowed") is not False
                and "narrative_momentum_transition_forbidden"
                not in narrative_momentum_failure_codes
            ),
        ),
        (
            "narrative_momentum_progress_event_present",
            ASPECT_NARRATIVE_MOMENTUM,
            _runtime_aspect_score_value(
                narrative_momentum_progress_event_count
                >= narrative_momentum_min_progress_event_count
            ),
        ),
        (
            "narrative_momentum_stall_budget_respected",
            ASPECT_NARRATIVE_MOMENTUM,
            _runtime_aspect_score_value(
                narrative_momentum_actual.get("stall_budget_respected") is not False
                and "narrative_momentum_stall_budget_exceeded"
                not in narrative_momentum_failure_codes
            ),
        ),
        (
            "narrative_momentum_contract_pass",
            ASPECT_NARRATIVE_MOMENTUM,
            _runtime_aspect_score_value(
                _rec(ASPECT_NARRATIVE_MOMENTUM).get("status")
                in {"passed", "not_applicable"}
                and narrative_momentum_actual.get("contract_pass") is not False
                and not narrative_momentum_failure_codes
            ),
        ),
        (
            "dramatic_irony_policy_present",
            ASPECT_DRAMATIC_IRONY,
            _runtime_aspect_score_value(bool(dramatic_irony_expected.get("policy_present"))),
        ),
        (
            "dramatic_irony_opportunity_present",
            ASPECT_DRAMATIC_IRONY,
            _runtime_aspect_score_value(bool(dramatic_irony_actual.get("opportunity_count"))),
        ),
        (
            "dramatic_irony_contract_pass",
            ASPECT_DRAMATIC_IRONY,
            _runtime_aspect_score_value(
                _rec(ASPECT_DRAMATIC_IRONY).get("status")
                in {"passed", "not_applicable"}
                and dramatic_irony_actual.get("contract_pass") is not False
                and not dramatic_irony_violation_codes
            ),
        ),
        (
            "narrator_authority_contract_present",
            ASPECT_NARRATOR_AUTHORITY,
            _runtime_aspect_score_value(_known(ASPECT_NARRATOR_AUTHORITY)),
        ),
        (
            "narrator_required_when_expected",
            ASPECT_NARRATOR_AUTHORITY,
            _runtime_aspect_score_value((not action_requires_narrator) or narrator_required),
        ),
        (
            "narrator_owns_consequence",
            ASPECT_NARRATOR_AUTHORITY,
            _runtime_aspect_score_value(
                (not narrator_required)
                or (
                    _rec(ASPECT_NARRATOR_AUTHORITY).get("status") == "passed"
                    and narrator_actual.get("actual_owner") == "narrator"
                    and narrator_actual.get("consequence_realized") is True
                )
            ),
        ),
        (
            "narrator_consequence_present",
            ASPECT_NARRATOR_AUTHORITY,
            _runtime_aspect_score_value((not narrator_required) or narrator_actual.get("consequence_realized") is True),
        ),
        (
            "narrator_authority_contract_pass",
            ASPECT_NARRATOR_AUTHORITY,
            _runtime_aspect_score_value(_rec(ASPECT_NARRATOR_AUTHORITY).get("status") == "passed"),
        ),
        (
            "npc_authority_contract_present",
            ASPECT_NPC_AUTHORITY,
            _runtime_aspect_score_value(_known(ASPECT_NPC_AUTHORITY)),
        ),
        (
            "npc_takeover_absent",
            ASPECT_NPC_AUTHORITY,
            _runtime_aspect_score_value(not bool(npc_actual.get("npc_takeover_detected"))),
        ),
        (
            "npc_policy_realized",
\
            ASPECT_NPC_AUTHORITY,
            _runtime_aspect_score_value(_rec(ASPECT_NPC_AUTHORITY).get("status") == "passed"),
        ),
        (
            "npc_agency_plan_present",
            ASPECT_NPC_AGENCY,
            _runtime_aspect_score_value(_known(ASPECT_NPC_AGENCY)),
        ),
        (
            "npc_independent_planning_used",
            ASPECT_NPC_AGENCY,
            _runtime_aspect_score_value(bool(npc_agency_actual.get("independent_planning_used"))),
        ),
        (
            "npc_long_horizon_state_present",
            ASPECT_NPC_AGENCY,
            _runtime_aspect_score_value(bool(npc_agency_actual.get("long_horizon_state_present"))),
        ),
        (
            "npc_private_plan_resolution_present",
            ASPECT_NPC_AGENCY,
            _runtime_aspect_score_value(bool(npc_agency_actual.get("private_plan_resolution_present"))),
        ),
        (
            "npc_private_plan_visibility_respected",
            ASPECT_NPC_AGENCY,
            _runtime_aspect_score_value(
                npc_agency_actual.get("private_plan_visibility_respected") is not False
                and not bool(npc_agency_actual.get("unrealized_selected_private_plan_actor_ids"))
            ),
        ),
        (
            "npc_intention_threads_carried_forward",
            ASPECT_NPC_AGENCY,
            _runtime_aspect_score_value(
                int(npc_agency_actual.get("intention_threads_carried_forward") or 0) > 0
                or int(npc_agency_actual.get("intention_threads_active") or 0)
                > len(npc_agency_actual.get("candidate_actor_ids") or [])
            ),
        ),
        (
            "npc_required_initiatives_realized",
            ASPECT_NPC_AGENCY,
            _runtime_aspect_score_value(not bool(npc_agency_actual.get("missing_required_actor_ids"))),
        ),
        (
            "multi_npc_initiative_realized",
            ASPECT_NPC_AGENCY,
            _runtime_aspect_score_value(bool(npc_agency_actual.get("multi_npc_initiative_realized"))),
        ),
        (
            "npc_carry_forward_closed",
            ASPECT_NPC_AGENCY,
            _runtime_aspect_score_value(
                not bool(npc_agency_actual.get("carry_forward_actor_ids"))
                and not bool(npc_agency_actual.get("missing_required_actor_ids"))
            ),
        ),
        (
            "npc_forbidden_actor_absent",
            ASPECT_NPC_AGENCY,
            _runtime_aspect_score_value(
                not bool(npc_agency_actual.get("forbidden_planned_actor_ids"))
                and not bool(npc_agency_actual.get("forbidden_realized_actor_ids"))
            ),
        ),
        (
            "npc_consequence_takeover_absent",
            ASPECT_NPC_AUTHORITY,
            _runtime_aspect_score_value(not bool(npc_actual.get("npc_takeover_detected"))),
        ),
        (
            "npc_exposition_absent",
            ASPECT_NPC_AUTHORITY,
            _runtime_aspect_score_value("narrated_player_perception" not in npc_failure_reason and "explained_environment" not in npc_failure_reason),
        ),
        (
            "player_agency_violation_absent",
            ASPECT_NPC_AUTHORITY,
            _runtime_aspect_score_value(
                "ai_controlled_human_actor" not in npc_failure_reason
                and "npc.force_player_speech.forbidden" not in violated_capabilities
            ),
        ),
        (
            "capability_selection_present",
            ASPECT_CAPABILITY_SELECTION,
            _runtime_aspect_score_value(_known(ASPECT_CAPABILITY_SELECTION)),
        ),
        (
            "capability_selection_valid",
            ASPECT_CAPABILITY_SELECTION,
            _runtime_aspect_score_value(_rec(ASPECT_CAPABILITY_SELECTION).get("status") != "failed"),
        ),
        (
            "forbidden_capability_absent",
            ASPECT_CAPABILITY_SELECTION,
            _runtime_aspect_score_value(not bool(cap_actual.get("forbidden_capability_realized"))),
        ),
        (
            "selected_capabilities_realized",
            ASPECT_CAPABILITY_SELECTION,
            _runtime_aspect_score_value(not missing_required_capabilities),
        ),
        (
            "dramatic_capability_contract_pass",
            ASPECT_CAPABILITY_SELECTION,
            _runtime_aspect_score_value(_rec(ASPECT_CAPABILITY_SELECTION).get("status") == "passed"),
        ),
        (
            "visible_block_origin_present",
            ASPECT_VISIBLE_PROJECTION,
            _runtime_aspect_score_value(bool(visible_actual.get("visible_block_origin_present"))),
        ),
        (
            "required_visible_origin_preserved",
            ASPECT_VISIBLE_PROJECTION,
            _runtime_aspect_score_value(bool(visible_actual.get("required_visible_origin_preserved"))),
        ),
        (
            "visible_projection_contract_pass",
            ASPECT_VISIBLE_PROJECTION,
            _runtime_aspect_score_value(_rec(ASPECT_VISIBLE_PROJECTION).get("status") == "passed"),
        ),
        (
            "narrative_aspect_policy_present",
            ASPECT_NARRATIVE_ASPECT,
            _runtime_aspect_score_value(bool(narrative_expected.get("policy_present"))),
        ),
        (
            "narrative_aspect_selected",
            ASPECT_NARRATIVE_ASPECT,
            _runtime_aspect_score_value(bool(narrative_selected.get("selected_aspects"))),
        ),
        (
            "narrative_aspect_visible_when_required",
            ASPECT_NARRATIVE_ASPECT,
            _runtime_aspect_score_value(narrative_actual.get("visible_when_required") is not False),
        ),
        (
            "narrative_aspect_contract_pass",
            ASPECT_NARRATIVE_ASPECT,
            _runtime_aspect_score_value(_rec(ASPECT_NARRATIVE_ASPECT).get("status") in {"passed", "not_applicable"}),
        ),
        (
            "theme_tracking_policy_present",
            ASPECT_NARRATIVE_ASPECT,
            _runtime_aspect_score_value(bool(narrative_expected.get("theme_tracking_policy_present"))),
        ),
        (
            "theme_tracking_selected",
            ASPECT_NARRATIVE_ASPECT,
            _runtime_aspect_score_value(bool(selected_theme_aspects)),
        ),
        (
            "theme_semantic_classification_present",
            ASPECT_NARRATIVE_ASPECT,
            _runtime_aspect_score_value(
                (
                    not bool(narrative_expected.get("semantic_tracking_enabled"))
                    or not selected_theme_aspects
                    or narrative_semantic_classification_count >= len(selected_theme_aspects)
                )
            ),
        ),
        (
            "theme_weak_alignment_absent",
            ASPECT_NARRATIVE_ASPECT,
            _runtime_aspect_score_value(narrative_semantic_required_weak_alignment_count == 0),
        ),
        (
            "theme_tracking_contract_pass",
            ASPECT_NARRATIVE_ASPECT,
            _runtime_aspect_score_value(
                _rec(ASPECT_NARRATIVE_ASPECT).get("status") in {"passed", "not_applicable"}
                and narrative_semantic_required_weak_alignment_count == 0
            ),
        ),
        (
            "voice_consistency_policy_present",
            ASPECT_VOICE_CONSISTENCY,
            _runtime_aspect_score_value(bool(voice_expected.get("policy_present"))),
        ),
        (
            "voice_semantic_classification_present",
            ASPECT_VOICE_CONSISTENCY,
            _runtime_aspect_score_value(
                (
                    not bool(voice_expected.get("semantic_classification_enabled"))
                    or voice_spoken_line_count <= 0
                    or voice_semantic_classification_count >= voice_spoken_line_count
                )
            ),
        ),
        (
            "voice_cross_actor_confusion_absent",
            ASPECT_VOICE_CONSISTENCY,
            _runtime_aspect_score_value(voice_cross_actor_count == 0),
        ),
        (
            "voice_forbidden_markers_absent",
            ASPECT_VOICE_CONSISTENCY,
            _runtime_aspect_score_value(voice_forbidden_marker_count == 0),
        ),
        (
            "voice_consistency_contract_pass",
            ASPECT_VOICE_CONSISTENCY,
            _runtime_aspect_score_value(
                _rec(ASPECT_VOICE_CONSISTENCY).get("status")
                in {"passed", "not_applicable"}
            ),
        ),
        (
            "hierarchical_memory_present",
            ASPECT_HIERARCHICAL_MEMORY,
            _runtime_aspect_score_value(bool(memory_actual.get("memory_present"))),
        ),
        (
            "memory_policy_applied",
            ASPECT_HIERARCHICAL_MEMORY,
            _runtime_aspect_score_value(
                (not bool(memory_expected.get("policy_present")))
                or _rec(ASPECT_HIERARCHICAL_MEMORY).get("status") in {"passed", "not_applicable"}
            ),
        ),
        (
            "memory_write_from_committed_turn",
            ASPECT_HIERARCHICAL_MEMORY,
            _runtime_aspect_score_value(not bool(memory_actual.get("uncommitted_write_detected"))),
        ),
        (
            "memory_context_bounded",
            ASPECT_HIERARCHICAL_MEMORY,
            _runtime_aspect_score_value(bool(memory_actual.get("context_bounded")) or not bool(memory_expected.get("policy_present"))),
        ),
        (
            "hierarchical_memory_contract_pass",
            ASPECT_HIERARCHICAL_MEMORY,
            _runtime_aspect_score_value(_rec(ASPECT_HIERARCHICAL_MEMORY).get("status") in {"passed", "not_applicable"}),
        ),
\
        (
            "recoverable_turn_http_200",
            ASPECT_VALIDATION,
            _runtime_aspect_score_value((not recoverable_turn) or http_status == 200),
        ),
        (
            "recoverable_turn_visible_output_present",
            ASPECT_VISIBLE_PROJECTION,
            _runtime_aspect_score_value((not recoverable_turn) or visible_output_for_recovery),
        ),
    ]
    if narrator_path_selected:
        narrator_path_score_names = {
            "turn_aspect_ledger_present",
            "narrator_authority_contract_present",
            "narrator_required_when_expected",
            "narrator_owns_consequence",
            "narrator_consequence_present",
            "narrator_authority_contract_pass",
            "visible_block_origin_present",
            "required_visible_origin_preserved",
            "visible_projection_contract_pass",
            "narrative_aspect_policy_present",
            "narrative_aspect_selected",
            "narrative_aspect_visible_when_required",
            "narrative_aspect_contract_pass",
            "theme_tracking_policy_present",
            "theme_tracking_selected",
            "theme_semantic_classification_present",
            "theme_weak_alignment_absent",
            "theme_tracking_contract_pass",
            "recoverable_turn_http_200",
            "recoverable_turn_visible_output_present",
        }
        scores = [row for row in scores if row[0] in narrator_path_score_names]
    for score_name, aspect_name, score_value in scores:
        try:
            adapter.add_score(
                name=score_name,
                value=score_value,
                comment="deterministic runtime aspect evidence",
                metadata=_runtime_aspect_score_metadata(
                    ledger=ledger,
                    aspect_name=aspect_name,
                    score_name=score_name,
                    value=score_value,
                    path_summary=path_summary,
                ),
            )
        except Exception:
            logger.debug("Langfuse runtime aspect score write failed for %s", score_name, exc_info=True)
    branching_forecast = (
        path_summary.get("branching_forecast")
        if isinstance(path_summary.get("branching_forecast"), dict)
        else {}
    )
    if branching_forecast and not narrator_path_selected:
        branch_status = str(branching_forecast.get("status") or "").strip()
        branch_option_count = int(branching_forecast.get("option_count") or 0)
        branch_meta = {
            "branching_forecast_score": True,
            "aspect_name": "branching_forecast",
            "session_id": path_summary.get("session_id"),
            "module_id": path_summary.get("module_id"),
            "runtime_profile_id": path_summary.get("runtime_profile_id"),
            "turn_number": path_summary.get("turn_number"),
            "turn_kind": path_summary.get("turn_kind"),
            "canonical_turn_id": path_summary.get("canonical_turn_id"),
            "status": branch_status,
            "forecast_only": bool(branching_forecast.get("forecast_only")),
            "authoritative": bool(branching_forecast.get("authoritative")),
            "inactive_branches_authoritative": bool(
                branching_forecast.get("inactive_branches_authoritative")
            ),
            "mutates_canonical_state": bool(branching_forecast.get("mutates_canonical_state")),
            "trigger_reasons": list(branching_forecast.get("trigger_reasons") or []),
            "option_count": branch_option_count,
            "environment": path_summary.get("environment"),
        }
        branch_scores = [
            ("branching_forecast_present", _runtime_aspect_score_value(bool(branching_forecast))),
            ("branch_options_count", float(branch_option_count)),
            (
                "inactive_branches_non_authoritative",
                _runtime_aspect_score_value(
                    branching_forecast.get("forecast_only") is True
                    and branching_forecast.get("authoritative") is False
                    and branching_forecast.get("inactive_branches_authoritative") is False
                    and branching_forecast.get("mutates_canonical_state") is False
                ),
            ),
        ]
        for score_name, score_value in branch_scores:
            try:
                adapter.add_score(
                    name=score_name,
                    value=score_value,
                    comment="deterministic branching forecast evidence",
                    metadata={**branch_meta, "score_name": score_name, "score_value": score_value},
                )
            except Exception:
                logger.debug("Langfuse branching forecast score write failed for %s", score_name, exc_info=True)

__all__ = ['_emit_langfuse_runtime_aspect_observability']
