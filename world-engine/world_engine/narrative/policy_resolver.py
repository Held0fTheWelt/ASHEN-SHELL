"""Effective policy resolver for scene execution packets."""

from __future__ import annotations


def resolve_effective_policy(
    *,
    policy_layers: dict[str, dict[str, object]],
    scene_id: str,
    actor_id: str | None = None,
) -> dict[str, object]:
    """Resolve policy layers in deterministic precedence order."""
    resolved: dict[str, object] = {}
    for key in ("global_policy", "module_policy", "scene_policy", "actor_policy", "turn_override_policy", "fallback_policy"):
        resolved.update(policy_layers.get(key, {}))
    scene_policy = policy_layers.get("scene_policy", {})
    if scene_id in scene_policy and isinstance(scene_policy[scene_id], dict):
        resolved.update(scene_policy[scene_id])
    actor_policy = policy_layers.get("actor_policy", {})
    if actor_id and actor_id in actor_policy and isinstance(actor_policy[actor_id], dict):
        resolved.update(actor_policy[actor_id])
    return resolved
