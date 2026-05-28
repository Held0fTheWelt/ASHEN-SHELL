"""Template and semantic NPC follow-up composition."""

from __future__ import annotations

from typing import Any

from .constants import *
from .feature_flags import is_follow_up_semantic_composition_enabled
from .player_input import _compact_one_line
from .safety_gates import _derive_source_contexts, _profile_forbidden_language_markers, _run_safety_gates
from .voice_profiles import (
    _follow_up_template_from_profile,
    _motivation_score_for_actor,
    _render_follow_up_template,
    _voice_profile_actor_id,
    _voice_profiles_by_actor,
)


def _template_follow_up_result(
    *,
    composed: bool,
    reason: str,
    actor_id: str,
    profile: dict[str, Any],
    source_field: str | None,
    placeholders: list[str],
    motivation_score: float | None,
    replanning: dict[str, Any],
    context: dict[str, Any],
    safety_gate_result: str,
    safety_gate_decisions: dict[str, Any],
    rejected_reason: str | None,
    text: str | None = None,
) -> dict[str, Any]:
    result = {
        "attempted": True,
        "composed": composed,
        "composition_kind": NEXT_ACTION_SOURCE_NPC_RESPONSE,
        "composition_mode": COMPOSITION_MODE_TEMPLATE_RENDER,
        "reason": reason,
        "voice_profile_used": True,
        "voice_profile_actor_id": _voice_profile_actor_id(profile),
        "voice_profile_source_field": source_field,
        "input_fields_used": placeholders,
        "motivation_score": motivation_score,
        "source_contexts": _derive_source_contexts(
            replanning=replanning,
            context=context,
            profile_used=True,
            motivation_score=motivation_score,
            placeholders_used=placeholders,
        ),
        "safety_gate_result": safety_gate_result,
        "safety_gate_decisions": safety_gate_decisions,
        "rejected_reason": rejected_reason,
        "new_people_introduced": False,
        "new_rooms_introduced": False,
        "plot_facts_introduced": False,
        "provider_metadata": None,
    }
    if text is not None:
        result["text"] = text
    return result


def _template_material_unavailable_result(
    *,
    replanning: dict[str, Any],
    context: dict[str, Any],
    actor_id: str,
    profile: dict[str, Any],
    motivation_score: float | None,
) -> dict[str, Any]:
    return _template_follow_up_result(
        composed=False,
        reason="voice_profile_follow_up_material_unavailable",
        actor_id=actor_id,
        profile=profile,
        source_field=None,
        placeholders=[],
        motivation_score=motivation_score,
        replanning=replanning,
        context=context,
        safety_gate_result="reject",
        safety_gate_decisions={},
        rejected_reason="voice_profile_follow_up_material_unavailable",
    )


def _semantic_follow_up_result(
    *,
    composed: bool,
    reason: str,
    actor_id: str,
    profile: dict[str, Any],
    motivation_score: float | None,
    source_contexts: list[dict[str, Any]],
    safety_gate_result: str,
    safety_gate_decisions: dict[str, Any],
    rejected_reason: str | None,
    provider_metadata: dict[str, Any] | None,
    text: str | None = None,
) -> dict[str, Any]:
    result = {
        "attempted": True,
        "composed": composed,
        "composition_kind": NEXT_ACTION_SOURCE_NPC_RESPONSE,
        "composition_mode": COMPOSITION_MODE_SEMANTIC_GENERATION,
        "reason": reason,
        "voice_profile_used": True,
        "voice_profile_actor_id": _voice_profile_actor_id(profile),
        "voice_profile_source_field": None,
        "input_fields_used": [],
        "motivation_score": motivation_score,
        "source_contexts": source_contexts,
        "safety_gate_result": safety_gate_result,
        "safety_gate_decisions": safety_gate_decisions,
        "rejected_reason": rejected_reason,
        "new_people_introduced": False,
        "new_rooms_introduced": False,
        "plot_facts_introduced": False,
        "provider_metadata": provider_metadata,
    }
    if text is not None:
        result["text"] = text
    return result


def _compose_template_render_follow_up(
    *,
    replanning: dict[str, Any],
    context: dict[str, Any],
    actor_id: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    """Deterministic template path. Renders an authored template from the
    voice profile and runs every safety gate on the rendered text.
    """
    selected_template = _follow_up_template_from_profile(profile)
    motivation_score = _motivation_score_for_actor(context=context, actor_id=actor_id)
    if selected_template is None:
        return _template_material_unavailable_result(
            replanning=replanning,
            context=context,
            actor_id=actor_id,
            profile=profile,
            motivation_score=motivation_score,
        )

    template, source_field = selected_template
    text, placeholders, reason = _render_follow_up_template(
        template=template,
        replanning=replanning,
        profile=profile,
        actor_id=actor_id,
        motivation_score=motivation_score,
    )
    if reason:
        return _template_follow_up_result(
            composed=False,
            reason=reason,
            actor_id=actor_id,
            profile=profile,
            source_field=source_field,
            placeholders=placeholders,
            motivation_score=motivation_score,
            replanning=replanning,
            context=context,
            safety_gate_result="reject",
            safety_gate_decisions={},
            rejected_reason=reason,
        )

    gate_result = _run_safety_gates(
        text=text,
        actor_id=actor_id,
        profile=profile,
        context=context,
    )
    if not gate_result["all_pass"]:
        return _template_follow_up_result(
            composed=False,
            reason=gate_result["rejected_reason"] or "safety_gate_rejected",
            actor_id=actor_id,
            profile=profile,
            source_field=source_field,
            placeholders=placeholders,
            motivation_score=motivation_score,
            replanning=replanning,
            context=context,
            safety_gate_result="reject",
            safety_gate_decisions=gate_result["decisions"],
            rejected_reason=gate_result["rejected_reason"],
        )
    return _template_follow_up_result(
        composed=True,
        reason="composed_from_voice_profile",
        actor_id=actor_id,
        profile=profile,
        source_field=source_field,
        placeholders=placeholders,
        motivation_score=motivation_score,
        replanning=replanning,
        context=context,
        safety_gate_result="pass",
        safety_gate_decisions=gate_result["decisions"],
        rejected_reason=None,
        text=text,
    )


def _build_follow_up_composition_request(
    *,
    replanning: dict[str, Any],
    context: dict[str, Any],
    actor_id: str,
    profile: dict[str, Any],
    motivation_score: float | None,
) -> dict[str, Any]:
    """Structured input handed to the semantic composition provider.

    The provider sees a *projection* of the runtime — never the canonical
    graph. It receives no mutators and no commit handles. The only writable
    thing the provider influences is its returned ``text``.
    """
    promoted = (
        replanning.get("promoted_input")
        if isinstance(replanning.get("promoted_input"), dict)
        else {}
    )
    return {
        "schema_version": "follow_up_composition_request.v1",
        "actor_id": actor_id,
        "voice_profile": dict(profile),
        "promoted_player_input": {
            "text": str(promoted.get("text_excerpt") or "").strip(),
            "promoted_player_input_id": str(
                promoted.get("promoted_player_input_id")
                or replanning.get("promoted_player_input_id")
                or ""
            ).strip(),
        },
        "interrupted_block": {
            "interrupted_block_id": str(replanning.get("interrupted_block_id") or "").strip(),
            "interrupted_block_type": str(
                replanning.get("interrupted_block_type") or ""
            ).strip(),
        },
        "motivation_score": motivation_score,
        "relationship_state": (
            context.get("relationship_state_output")
            if isinstance(context.get("relationship_state_output"), dict)
            else None
        ),
        "scene_energy": (
            context.get("scene_energy_output")
            if isinstance(context.get("scene_energy_output"), dict)
            else None
        ),
        "social_pressure": (
            context.get("social_pressure_output")
            if isinstance(context.get("social_pressure_output"), dict)
            else None
        ),
        "recent_visible_context": (
            list(context.get("recent_visible_blocks"))
            if isinstance(context.get("recent_visible_blocks"), list)
            else []
        ),
        "information_disclosure_target": (
            context.get("information_disclosure_target")
            if isinstance(context.get("information_disclosure_target"), dict)
            else None
        ),
        "max_text_chars": MAX_COMPOSED_FOLLOW_UP_CHARS,
        "voice_forbidden_markers": _profile_forbidden_language_markers(profile),
    }


def _compose_semantic_npc_follow_up(
    *,
    replanning: dict[str, Any],
    context: dict[str, Any],
    actor_id: str,
    profile: dict[str, Any],
    provider: FollowUpSemanticProvider,
) -> dict[str, Any]:
    """Semantic path. Calls the injected provider, then runs every safety gate.

    The provider's claim of success is *advisory*; the gates own the final
    pass/reject decision. The provider never touches state — it just returns
    text or an error code.
    """
    motivation_score = _motivation_score_for_actor(context=context, actor_id=actor_id)
    request = _build_follow_up_composition_request(
        replanning=replanning,
        context=context,
        actor_id=actor_id,
        profile=profile,
        motivation_score=motivation_score,
    )
    source_contexts = _derive_source_contexts(
        replanning=replanning,
        context=context,
        profile_used=True,
        motivation_score=motivation_score,
    )
    try:
        response = provider(request) or {}
    except Exception as exc:  # noqa: BLE001 — provider faults must not crash the loop
        return _semantic_follow_up_result(
            composed=False,
            reason="semantic_provider_exception",
            actor_id=actor_id,
            profile=profile,
            motivation_score=motivation_score,
            source_contexts=source_contexts,
            safety_gate_result="not_applicable",
            safety_gate_decisions={},
            rejected_reason="semantic_provider_exception",
            provider_metadata={"exception_type": type(exc).__name__},
        )
    if not isinstance(response, dict):
        response = {}
    provider_metadata = (
        response.get("metadata") if isinstance(response.get("metadata"), dict) else {}
    )
    if not response.get("success") or not isinstance(response.get("text"), str):
        error_code = str(response.get("error_code") or "semantic_provider_returned_no_text")
        return _semantic_follow_up_result(
            composed=False,
            reason=error_code,
            actor_id=actor_id,
            profile=profile,
            motivation_score=motivation_score,
            source_contexts=source_contexts,
            safety_gate_result="not_applicable",
            safety_gate_decisions={},
            rejected_reason=error_code,
            provider_metadata=dict(provider_metadata),
        )
    candidate_text = _compact_one_line(
        str(response.get("text") or ""), limit=MAX_COMPOSED_FOLLOW_UP_CHARS
    )
    gate_result = _run_safety_gates(
        text=candidate_text,
        actor_id=actor_id,
        profile=profile,
        context=context,
    )
    if not gate_result["all_pass"]:
        return _semantic_follow_up_result(
            composed=False,
            reason=gate_result["rejected_reason"] or "semantic_output_safety_gate_rejected",
            actor_id=actor_id,
            profile=profile,
            motivation_score=motivation_score,
            source_contexts=source_contexts,
            safety_gate_result="reject",
            safety_gate_decisions=gate_result["decisions"],
            rejected_reason=gate_result["rejected_reason"],
            provider_metadata=dict(provider_metadata),
        )
    return _semantic_follow_up_result(
        composed=True,
        reason="composed_from_semantic_provider",
        actor_id=actor_id,
        profile=profile,
        motivation_score=motivation_score,
        source_contexts=source_contexts,
        safety_gate_result="pass",
        safety_gate_decisions=gate_result["decisions"],
        rejected_reason=None,
        provider_metadata=dict(provider_metadata),
        text=candidate_text,
    )


def _compose_npc_follow_up(
    *,
    replanning: dict[str, Any],
    context: dict[str, Any],
    actor_id: str,
    composition_provider: FollowUpSemanticProvider | None = None,
) -> dict[str, Any]:
    """Dispatcher: tries semantic first when enabled + provider available, then
    falls back to the deterministic template path. The voice profile gate is
    the *first* hard prerequisite — without a profile the dispatcher never
    invokes a provider.
    """
    profiles_by_actor = _voice_profiles_by_actor(context)
    profile = profiles_by_actor.get(actor_id)
    if not isinstance(profile, dict):
        return {
            "attempted": True,
            "composed": False,
            "composition_kind": NEXT_ACTION_SOURCE_NPC_RESPONSE,
            "composition_mode": COMPOSITION_MODE_NOT_APPLICABLE,
            "reason": "voice_profile_unavailable",
            "voice_profile_used": False,
            "voice_profile_actor_id": None,
            "voice_profile_source_field": None,
            "input_fields_used": [],
            "motivation_score": None,
            "source_contexts": [],
            "safety_gate_result": "reject",
            "safety_gate_decisions": {},
            "rejected_reason": "voice_profile_unavailable",
            "new_people_introduced": False,
            "new_rooms_introduced": False,
            "plot_facts_introduced": False,
            "provider_metadata": None,
        }

    semantic_enabled = is_follow_up_semantic_composition_enabled()
    semantic_attempted = False
    semantic_result: dict[str, Any] | None = None
    if semantic_enabled and composition_provider is not None:
        semantic_attempted = True
        semantic_result = _compose_semantic_npc_follow_up(
            replanning=replanning,
            context=context,
            actor_id=actor_id,
            profile=profile,
            provider=composition_provider,
        )
        if semantic_result.get("composed"):
            return semantic_result

    template_result = _compose_template_render_follow_up(
        replanning=replanning,
        context=context,
        actor_id=actor_id,
        profile=profile,
    )
    if semantic_attempted:
        # Tag mode so observers can tell "template-was-direct" from
        # "template-after-semantic-failure".
        template_result = dict(template_result)
        template_result["composition_mode"] = (
            COMPOSITION_MODE_TEMPLATE_FALLBACK_AFTER_SEMANTIC_FAILURE
        )
        template_result["semantic_attempt_metadata"] = {
            "composition_mode": COMPOSITION_MODE_SEMANTIC_GENERATION,
            "rejected_reason": (semantic_result or {}).get("rejected_reason"),
            "provider_metadata": (semantic_result or {}).get("provider_metadata"),
            "safety_gate_decisions": (semantic_result or {}).get("safety_gate_decisions") or {},
        }
    return template_result


def _non_composed_result(
    *,
    composition_kind: str,
    reason: str,
    attempted: bool = False,
) -> dict[str, Any]:
    return {
        "attempted": attempted,
        "composed": False,
        "composition_kind": composition_kind,
        "composition_mode": COMPOSITION_MODE_NOT_APPLICABLE,
        "reason": reason,
        "voice_profile_used": False,
        "voice_profile_actor_id": None,
        "voice_profile_source_field": None,
        "input_fields_used": [],
        "motivation_score": None,
        "source_contexts": [],
        "safety_gate_result": "not_applicable" if not attempted else "reject",
        "safety_gate_decisions": {},
        "rejected_reason": None if not attempted else reason,
        "new_people_introduced": False,
        "new_rooms_introduced": False,
        "plot_facts_introduced": False,
        "provider_metadata": None,
    }
