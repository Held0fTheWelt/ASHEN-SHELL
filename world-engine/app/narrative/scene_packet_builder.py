"""Scene packet builder for typed runtime execution contract."""

from __future__ import annotations

from app.narrative.package_models import NarrativeDirectorScenePacket, NarrativePackage
from app.narrative.policy_resolver import resolve_effective_policy


def build_scene_packet(
    *,
    package: NarrativePackage,
    scene_id: str,
    phase_id: str,
    turn_number: int,
    player_input: str,
    selected_scene_function: str,
    pacing_mode: str,
) -> NarrativeDirectorScenePacket:
    """Build deterministic scene packet from compiled package."""
    policy = resolve_effective_policy(policy_layers=package.policy_layers, scene_id=scene_id)
    return NarrativeDirectorScenePacket(
        module_id=package.manifest.module_id,
        package_version=package.manifest.package_version,
        scene_id=scene_id,
        phase_id=phase_id,
        turn_number=turn_number,
        player_input=player_input,
        selected_scene_function=selected_scene_function,
        pacing_mode=pacing_mode,
        responder_set=[],
        active_threads=[],
        scene_constraints=package.scene_constraints.get(scene_id, {}),
        scene_guidance=package.scene_guidance.get(scene_id, {}),
        actor_minds=package.actor_minds,
        voice_rules=package.voice_rules,
        legality_table=package.legality_tables.get(scene_id, {"allowed_triggers": []}),
        effective_policy=policy,
    )
