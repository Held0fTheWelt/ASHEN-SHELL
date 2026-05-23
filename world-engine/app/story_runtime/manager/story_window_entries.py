"""Story-window entry helpers.

Builds story-window history entries from committed turns for context retrieval and player-visible continuity.
"""
from __future__ import annotations

from ._deps import *
from .story_window_entry_parts import (
    actor_summary_for_story_window,
    authority_summary_for_story_window,
    build_story_window_player_entry,
    build_story_window_runtime_entry,
    detect_thin_path_narrator_fold,
    event_surfaces_for_story_window,
    vitality_readout_for_story_window,
)

def _story_window_entries_for_session(session: StorySession) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for event in session.diagnostics:
        if not isinstance(event, dict):
            continue
        surfaces = event_surfaces_for_story_window(event)
        turn_number = surfaces["turn_number"]
        turn_kind = surfaces["turn_kind"]
        consequence_lines = surfaces["consequence_lines"]
        spoken_lines = surfaces["spoken_lines"]
        action_lines = surfaces["action_lines"]
        render_support = surfaces["render_support"]
        runtime_governance_surface = surfaces["runtime_governance_surface"]
        story_dramatic_context = surfaces["story_dramatic_context"]
        actor_turn_summary = actor_summary_for_story_window(
            event=event,
            story_dramatic_context=story_dramatic_context,
            spoken_lines=spoken_lines,
            action_lines=action_lines,
        )
        authority_summary = authority_summary_for_story_window(
            event=event,
            commit=surfaces["commit"],
            validation=surfaces["validation"],
            authority=surfaces["authority"],
            social_summary=surfaces["social_summary"],
            story_dramatic_context=story_dramatic_context,
        )

        # Thin-path narrator fold: when realize_via_capabilities produced a single
        # narrator block (and no actor_line / actor_action), the narrator's prose IS
        # the outcome of the player's input. Fold it into the player_input_outcome
        # card and suppress the duplicate runtime_response entry below.
        thin_path_narrator_text, thin_path_fold = detect_thin_path_narrator_fold(event)

        if turn_kind != "opening":
            raw_input = str(event.get("raw_input") or "").strip()
            player_entry = build_story_window_player_entry(
                session=session,
                event=event,
                turn_number=turn_number,
                raw_input=raw_input,
                thin_path_narrator_text=thin_path_narrator_text,
                thin_path_fold=thin_path_fold,
            )
            if player_entry:
                entries.append(player_entry)

        visible_lines = _visible_lines_from_turn_event(event)
        scene_blocks = _scene_blocks_from_turn_event(event)
        if thin_path_fold:
            scene_blocks = [
                b
                for b in scene_blocks
                if str(b.get("block_type") or "").strip().lower() != "narrator"
            ]
            visible_lines = []
        quality_class, degradation_signals, degradation_summary = _canonical_quality_fields_from_surfaces(
            runtime_governance_surface=runtime_governance_surface,
            authority_summary=authority_summary,
        )
        vitality_readout = vitality_readout_for_story_window(event)
        actor_survival_telemetry = vitality_readout["actor_survival_telemetry"]
        vitality_summary = vitality_readout["vitality_summary"]
        passivity_diagnosis = vitality_readout["passivity_diagnosis"]

        if not visible_lines and not spoken_lines and not action_lines and not consequence_lines:
            continue
        runtime_entry = build_story_window_runtime_entry(
            session=session,
            turn_number=turn_number,
            turn_kind=turn_kind,
            visible_lines=visible_lines,
            spoken_lines=spoken_lines,
            action_lines=action_lines,
            consequence_lines=consequence_lines,
            story_dramatic_context=story_dramatic_context,
            authority_summary=authority_summary,
            quality_class=quality_class,
            degradation_signals=degradation_signals,
            degradation_summary=degradation_summary,
            actor_turn_summary=actor_turn_summary,
            actor_survival_telemetry=actor_survival_telemetry,
            vitality_summary=vitality_summary,
            passivity_diagnosis=passivity_diagnosis,
            runtime_governance_surface=runtime_governance_surface,
            scene_blocks=scene_blocks,
            render_support=render_support,
        )
        entries.append(runtime_entry)
    return entries

__all__ = [
    name
    for name in globals()
    if not name.startswith("__") and name != "annotations"
]
