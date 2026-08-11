"""Resolve module-configured player-visible projection behavior."""

from __future__ import annotations

from typing import Any

from ai_stack.module_runtime_policy import load_module_runtime_policy


def _runtime_profile_id(projection: dict[str, Any]) -> str | None:
    for key in ("runtime_profile_id", "experience_template_id", "seed_template_id", "template_id"):
        value = str(projection.get(key) or "").strip()
        if value:
            return value
    return None


def resolve_visible_projection_policy(
    *,
    module_id: str,
    runtime_projection: dict[str, Any] | None,
    graph_state: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return a closed, generic policy; missing configuration enables no rich adapter."""

    graph = graph_state if isinstance(graph_state, dict) else {}
    module_policy = (
        graph.get("module_runtime_policy")
        if isinstance(graph.get("module_runtime_policy"), dict)
        else None
    )
    projection = runtime_projection if isinstance(runtime_projection, dict) else {}
    if module_policy is None:
        try:
            module_policy = load_module_runtime_policy(
                module_id=module_id,
                runtime_profile_id=_runtime_profile_id(projection),
            ).to_dict()
        except Exception:
            module_policy = {}
    governance = (
        module_policy.get("runtime_governance_policy")
        if isinstance(module_policy.get("runtime_governance_policy"), dict)
        else {}
    )
    raw = governance.get("visible_projection")
    raw = raw if isinstance(raw, dict) else {}
    return {
        "schema_version": str(raw.get("schema_version") or "visible_projection_policy.v1"),
        "enabled": bool(raw.get("enabled", False)),
        "projection_profile": str(raw.get("projection_profile") or "generic_blocks").strip()
        or "generic_blocks",
        "live_scene_projection_enabled": bool(raw.get("live_scene_projection_enabled", False)),
        "deterministic_fallback": str(raw.get("deterministic_fallback") or "none").strip()
        or "none",
        "opening_shape": str(raw.get("opening_shape") or "preserve").strip() or "preserve",
        "opening_narration_normalization_enabled": bool(
            raw.get("opening_narration_normalization_enabled", False)
        ),
        "diagnostics_envelope_enabled": bool(raw.get("diagnostics_envelope_enabled", False)),
        "human_input_attribution_enabled": bool(raw.get("human_input_attribution_enabled", False)),
        "hard_failure_behavior": str(raw.get("hard_failure_behavior") or "recover").strip()
        or "recover",
        "require_origin_metadata": bool(raw.get("require_origin_metadata", True)),
    }


def rich_scene_projection_enabled(policy: dict[str, Any]) -> bool:
    return bool(
        policy.get("enabled")
        and policy.get("live_scene_projection_enabled")
        and policy.get("projection_profile") == "scene_turn_envelope_v2"
    )


__all__ = ["resolve_visible_projection_policy", "rich_scene_projection_enabled"]
