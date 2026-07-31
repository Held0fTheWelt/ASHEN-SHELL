"""Scripted continuation helpers.

Provides deterministic scripted continuation paths used when model-driven continuation is unavailable or not desired.
"""
from __future__ import annotations

from ._deps import *

class _ScriptedContinuationMixin:
    @staticmethod
    def _npc_speak_directive(block: dict[str, Any]) -> dict[str, Any]:
        directive = block.get("npc_speak_directive")
        return directive if isinstance(directive, dict) else {}

    @staticmethod
    def _npc_speak_source_facts(block: dict[str, Any]) -> dict[str, Any]:
        source_facts = block.get("source_facts")
        return source_facts if isinstance(source_facts, dict) else {}

    @staticmethod
    def _npc_speak_target_language(session: StorySession) -> str:
        return (
            str(session.session_output_language or DEFAULT_SESSION_LANGUAGE).strip().lower()[:2]
            or DEFAULT_SESSION_LANGUAGE
        )

    @staticmethod
    def _npc_speak_prompt_lines(
        *,
        actor_id: str,
        intent: str,
        required_facts: Any,
        paraphrase_policy: str,
        minimum_visible: str,
        forbidden_drift: Any,
        quote_excerpt: str,
        quote_use_as: str,
        source_facts: dict[str, Any],
        target_language: str,
    ) -> list[str]:
        prompt_lines = [
            f"You are realizing scripted NPC speech for character '{actor_id}' in the God of Carnage interactive experience.",
            f"Output language: {target_language}",
            "",
            "## Directive",
            f"- Actor: {actor_id}",
            f"- Intent: {intent}",
            f"- Required facts to include: {', '.join(str(f) for f in required_facts) if isinstance(required_facts, list) else str(required_facts)}",
            f"- Paraphrase policy: {paraphrase_policy}",
            f"- Minimum visible: {minimum_visible}",
            f"- Forbidden drift: {', '.join(str(f) for f in forbidden_drift) if isinstance(forbidden_drift, list) else str(forbidden_drift)}",
        ]
        if quote_excerpt:
            prompt_lines.extend([
                "",
                "## Quote anchor (short reference only, do NOT reproduce verbatim)",
                f"- Excerpt: \"{quote_excerpt}\"",
                f"- Use as: {quote_use_as}",
            ])

        step_info = source_facts.get("step") if isinstance(source_facts.get("step"), dict) else {}
        presence = source_facts.get("presence") if isinstance(source_facts.get("presence"), dict) else {}
        if step_info or presence:
            prompt_lines.extend([
                "",
                "## Scene context",
                f"- Step: {step_info.get('name', '')}",
                f"- Present characters: {', '.join(presence.get('named_characters', []))}",
                f"- Speaker in focus: {presence.get('speaker_in_focus', actor_id)}",
            ])
        return prompt_lines

    @staticmethod
    def _npc_speak_instruction_lines(
        *,
        actor_id: str,
        target_language: str,
        paraphrase_policy: str,
        minimum_visible: str,
    ) -> list[str]:
        return [
            "",
            "## Instructions",
            f"Produce a single spoken line (1-3 sentences) for {actor_id}.",
            "The line must:",
            f"- Be in {target_language}",
            "- Include all required facts naturally",
            f"- Respect the paraphrase policy ({paraphrase_policy})",
            "- Match the character's voice and personality",
            f"- Stay within the minimum_visible description",
            "- Avoid all forbidden drift items",
            "",
            "Return ONLY the spoken line text, nothing else.",
        ]

    def _realized_or_fallback_npc_speech(
        self,
        *,
        prompt_text: str,
        actor_id: str,
        intent: str,
        required_facts: Any,
        quote_excerpt: str,
        target_language: str,
    ) -> tuple[str, str, Any, Any, Any, Any]:
        fallback_speech = _scripted_npc_speech_text(
            actor_ref=actor_id,
            intent=intent,
            required_facts=required_facts,
            quote_excerpt=quote_excerpt,
            language=target_language,
        )
        speech_text = fallback_speech
        fallback_status = "deterministic_scripted_speech"
        model_id, provider, adapter, api_model, timeout_seconds = self._narrator_path_output_adapter_candidate()
        if adapter is None:
            return speech_text, "fallback_no_adapter", model_id, provider, adapter, api_model
        try:
            result = adapter.generate(
                prompt_text,
                timeout_seconds=timeout_seconds or 20.0,
                model_name=api_model,
            )
            generated = str(result.content or "").strip() if result.success else ""
            if generated and not generated.startswith("["):
                speech_text = generated.strip().strip("\"“”„")
                fallback_status = "realized"
            else:
                fallback_status = "fallback_generation_failed"
        except Exception:
            fallback_status = "fallback_adapter_error"
        return speech_text, fallback_status, model_id, provider, adapter, api_model

    @staticmethod
    def _realized_npc_speech_block(
        *,
        block: dict[str, Any],
        actor_id: str,
        intent: str,
        narrator_perception: Any,
        target_language: str,
        speech_text: str,
        fallback_speech: str,
        fallback_status: str,
        model_id: Any,
        provider: Any,
        adapter: Any,
        api_model: Any,
    ) -> dict[str, Any]:
        frame = _scripted_narration_frame(
            actor_ref=actor_id,
            intent=intent,
            perception=narrator_perception,
            language=target_language,
        )
        realized_block = dict(block)
        realized_block["block_type"] = "narrator"
        realized_block["composition_kind"] = "narrated_actor_speech"
        realized_block["text"] = f"{frame} {_scripted_quote(speech_text, language=target_language)}".strip()
        realized_block["speaker_label"] = "Narrator"
        realized_block["actor_id"] = None
        realized_block["target_actor_id"] = _resolve_goc_runtime_actor_id(actor_id) or None
        realized_block["embedded_speech_spans"] = [
            _embedded_speech_span(
                actor_ref=actor_id,
                speech_text=speech_text,
                intent=intent,
                block=block,
            )
        ]
        realized_block["realization_status"] = fallback_status
        realized_block["requires_llm_realization"] = False
        realized_block["realization_metadata"] = {
            "provider": provider,
            "model": api_model,
            "adapter": str(getattr(adapter, "adapter_id", model_id) or "") if adapter is not None else None,
            "fallback_speech_used": speech_text == fallback_speech,
            "speech_composition": "narrator_with_embedded_actor_speech",
        }
        return realized_block

    def _realize_npc_speak_block(
        self,
        *,
        block: dict[str, Any],
        session: StorySession,
        continuation: dict[str, Any],
        trace_id: str | None,
    ) -> dict[str, Any]:
        """Realize a single ``npc_speak`` block via LLM.

        Builds a prompt from the block's ``npc_speak_directive`` and
        ``source_facts``, calls the same adapter used for narrator path
        output, and replaces the placeholder text with the realized speech.
        """
        directive = self._npc_speak_directive(block)
        source_facts = self._npc_speak_source_facts(block)
        actor_id = str(directive.get("actor") or block.get("actor_id") or "").strip()
        intent = str(directive.get("intent") or "").strip()
        required_facts = directive.get("required_facts") or []
        paraphrase_policy = str(directive.get("paraphrase_policy") or "structural_paraphrase_required").strip()
        minimum_visible = str(directive.get("minimum_visible") or "").strip()
        forbidden_drift = directive.get("forbidden_drift") or []
        quote_excerpt = str(directive.get("quote_anchor_excerpt") or "").strip()
        quote_use_as = str(directive.get("quote_anchor_use_as") or "").strip()
        narrator_perception = directive.get("narrator_perception")

        target_language = self._npc_speak_target_language(session)
        prompt_lines = self._npc_speak_prompt_lines(
            actor_id=actor_id,
            intent=intent,
            required_facts=required_facts,
            paraphrase_policy=paraphrase_policy,
            minimum_visible=minimum_visible,
            forbidden_drift=forbidden_drift,
            quote_excerpt=quote_excerpt,
            quote_use_as=quote_use_as,
            source_facts=source_facts,
            target_language=target_language,
        )
        prompt_lines.extend(
            self._npc_speak_instruction_lines(
                actor_id=actor_id,
                target_language=target_language,
                paraphrase_policy=paraphrase_policy,
                minimum_visible=minimum_visible,
            )
        )
        fallback_speech = _scripted_npc_speech_text(
            actor_ref=actor_id,
            intent=intent,
            required_facts=required_facts,
            quote_excerpt=quote_excerpt,
            language=target_language,
        )
        speech_text, fallback_status, model_id, provider, adapter, api_model = self._realized_or_fallback_npc_speech(
            prompt_text="\n".join(prompt_lines),
            actor_id=actor_id,
            intent=intent,
            required_facts=required_facts,
            quote_excerpt=quote_excerpt,
            target_language=target_language,
        )
        return self._realized_npc_speech_block(
            block=block,
            actor_id=actor_id,
            intent=intent,
            narrator_perception=narrator_perception,
            target_language=target_language,
            speech_text=speech_text,
            fallback_speech=fallback_speech,
            fallback_status=fallback_status,
            model_id=model_id,
            provider=provider,
            adapter=adapter,
            api_model=api_model,
        )

    @staticmethod
    def _merge_continuation_into_opening_state(
        graph_state: dict[str, Any],
        continuation: dict[str, Any],
    ) -> dict[str, Any]:
        """Append continuation scene blocks to the opening graph state."""
        graph_state = dict(graph_state)

        # The narrator-path opening stores blocks in
        # ``visible_output_bundle.scene_blocks``.
        bundle = graph_state.get("visible_output_bundle")
        if isinstance(bundle, dict):
            bundle = dict(bundle)
            existing_blocks = list(bundle.get("scene_blocks") or [])
            existing_blocks.extend(continuation.get("scene_blocks", []))
            bundle["scene_blocks"] = existing_blocks
            gm_narration = list(bundle.get("gm_narration") or [])
            for blk in continuation.get("scene_blocks", []):
                if isinstance(blk, dict) and str(blk.get("text") or "").strip():
                    gm_narration.append(str(blk["text"]).strip())
            bundle["gm_narration"] = gm_narration
            graph_state["visible_output_bundle"] = bundle
        else:
            cont_blocks = continuation.get("scene_blocks", [])
            graph_state["visible_output_bundle"] = {
                "scene_blocks": cont_blocks,
                "gm_narration": [
                    str(blk.get("text") or "").strip()
                    for blk in cont_blocks
                    if isinstance(blk, dict) and str(blk.get("text") or "").strip()
                ],
                "spoken_lines": [],
                "action_lines": [],
            }

        opening_step_ids = list(
            graph_state.get("opening_scene_sequence", {}).get("canonical_step_ids") or []
        ) if isinstance(graph_state.get("opening_scene_sequence"), dict) else []
        cont_step_ids = continuation.get("canonical_step_ids", [])
        if cont_step_ids:
            merged_ids = list(dict.fromkeys([*opening_step_ids, *cont_step_ids]))
            if isinstance(graph_state.get("opening_scene_sequence"), dict):
                graph_state["opening_scene_sequence"] = dict(graph_state["opening_scene_sequence"])
                graph_state["opening_scene_sequence"]["canonical_step_ids"] = merged_ids
            if isinstance(graph_state.get("narrator_path"), dict):
                graph_state["narrator_path"] = dict(graph_state["narrator_path"])
                graph_state["narrator_path"]["canonical_step_ids"] = merged_ids

        graph_state["scripted_continuation_applied"] = True
        return graph_state


__all__ = ["_ScriptedContinuationMixin"]
