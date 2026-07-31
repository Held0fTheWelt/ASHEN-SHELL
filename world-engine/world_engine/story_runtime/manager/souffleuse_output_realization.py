"""Souffleuse output realization.

Builds assisted narrator output used by the souffleuse path without replacing authoritative committed truth.
"""
from __future__ import annotations

from ._deps import *

class _SouffleuseOutputRealizationMixin:
    def _attach_souffleuse_shadow_judge_meta(
        self,
        realized: list[dict[str, Any]],
        meta: dict[str, Any],
    ) -> dict[str, Any]:
        """Non-blocking shadow gate (Sub-Plan 4 PR-4D) — diagnostics only."""
        from ai_stack.quality_lab.souffleuse_production_judge import evaluate_souffleuse_visible_text_shadow

        judgments: list[dict[str, Any]] = []
        for block in realized:
            source_facts = block.get("source_facts") if isinstance(block.get("source_facts"), dict) else {}
            judgments.append(
                evaluate_souffleuse_visible_text_shadow(
                    str(block.get("text") or ""),
                    character_voice_profile=source_facts.get("character_voice_profile"),
                )
            )
        out = dict(meta)
        out["souffleuse_production_judge_shadow"] = judgments
        return out

    def _source_projected_souffleuse_output(
        self,
        *,
        source_blocks: list[dict[str, Any]],
        source_language: str,
        target_language: str,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        realized: list[dict[str, Any]] = []
        for block in source_blocks:
            nb = dict(block)
            visible_text = _compose_souffleuse_visible_source_text(nb).strip()
            if visible_text and visible_text != str(nb.get("text") or "").strip():
                nb["source_text"] = nb.get("text")
                nb["text"] = visible_text
                nb["player_display_text"] = visible_text
                nb["output_realization_source"] = "souffleuse_source_projection"
            nb["source_language"] = source_language
            nb["session_output_language"] = target_language
            nb["visible_output_language"] = target_language
            nb["requires_output_realization"] = False
            realized.append(nb)
        meta = {
            "contract": "souffleuse_output_realization.v1",
            "status": "not_required",
            "source_language": source_language,
            "session_output_language": target_language,
            "adapter": SOUFFLEUSE_ADAPTER,
            "adapter_invocation_mode": SOUFFLEUSE_INVOCATION_MODE,
            "usage_source": "prompt_store_internal_english_visible_projection",
            "block_count": len(source_blocks),
        }
        return realized, self._attach_souffleuse_shadow_judge_meta(realized, meta)

    def _fallback_souffleuse_realization_result(
        self,
        *,
        source_blocks: list[dict[str, Any]],
        source_language: str,
        target_language: str,
        status: str,
        fallback_reason: str,
        attempts: list[dict[str, Any]] | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        realized = self._fallback_souffleuse_output_blocks(
            source_blocks=source_blocks,
            source_language=source_language,
            target_language=target_language,
            status=status,
        )
        meta = {
            "contract": "souffleuse_output_realization.v1",
            "status": status,
            "source_language": source_language,
            "session_output_language": target_language,
            "visible_output_language": target_language
            if target_language == source_language
            else source_language,
            "adapter": SOUFFLEUSE_ADAPTER,
            "adapter_invocation_mode": SOUFFLEUSE_INVOCATION_MODE,
            "usage_source": "prompt_store_internal_english_visible_projection",
            "fallback_reason": fallback_reason,
            "translation_required": target_language != source_language,
            "output_language_mismatch": target_language != source_language,
            "block_count": len(realized),
        }
        if attempts is not None:
            meta["failed_attempts"] = attempts
            meta["attempt_count"] = len(attempts)
        return realized, meta

    def _run_souffleuse_output_attempt(
        self,
        *,
        adapter_spec: tuple[Any, ...],
        prompt: str,
    ) -> tuple[dict[str, Any], Any | None]:
        model_id, provider, adapter, api_model, timeout_seconds = adapter_spec
        attempt: dict[str, Any] = {
            "provider": provider,
            "model_id": model_id,
            "api_model": api_model,
            "adapter": str(getattr(adapter, "adapter_name", "") or provider),
            "timeout_seconds": timeout_seconds or 20.0,
        }
        try:
            result = adapter.generate(
                prompt,
                timeout_seconds=timeout_seconds or 20.0,
                model_name=api_model,
            )
        except Exception as exc:
            attempt["success"] = False
            attempt["error"] = str(exc) or type(exc).__name__
            return attempt, None
        return attempt, result

    def _realize_souffleuse_module_blocks(
        self,
        *,
        source_blocks: list[dict[str, Any]],
        rows: list[Any],
        source_language: str,
        target_language: str,
    ) -> tuple[list[dict[str, Any]], list[str]]:
        by_id = {
            str(row.get("id") or "").strip(): row
            for row in rows
            if isinstance(row, dict) and str(row.get("id") or "").strip()
        }
        realized: list[dict[str, Any]] = []
        missing_ids: list[str] = []
        for block in source_blocks:
            block_id = str(block.get("id") or "").strip()
            out_row = by_id.get(block_id)
            text = str(out_row.get("text") or "").strip() if isinstance(out_row, dict) else ""
            if not text:
                missing_ids.append(block_id or f"index:{len(realized)}")
                continue
            visible_text, _partial = sanitize_visible_block_text(
                text,
                block_type=SOUFFLEUSE_BLOCK_TYPE,
                speaker_label=str(block.get("speaker_label") or "Souffleuse"),
                actor_id=None,
                expected_language=target_language,
            )
            nb = dict(block)
            nb["text"] = visible_text.strip() or text
            nb["player_display_text"] = nb["text"]
            nb["source_language"] = source_language
            nb["session_output_language"] = target_language
            nb["visible_output_language"] = target_language
            nb["requires_output_realization"] = False
            nb["source_before_output_module"] = nb.get("source")
            nb["output_realization_source"] = "souffleuse_output_module"
            realized.append(nb)
        return realized, missing_ids

    def _souffleuse_output_module_result(
        self,
        *,
        source_blocks: list[dict[str, Any]],
        source_language: str,
        target_language: str,
        candidates: list[tuple[Any, ...]],
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        prompt = self._souffleuse_output_prompt(
            source_blocks=source_blocks,
            source_language=source_language,
            target_language=target_language,
        )
        attempts: list[dict[str, Any]] = []
        for model_id, provider, adapter, api_model, timeout_seconds in candidates:
            attempt, result = self._run_souffleuse_output_attempt(
                adapter_spec=(model_id, provider, adapter, api_model, timeout_seconds),
                prompt=prompt,
            )
            if result is None:
                attempts.append(attempt)
                continue
            result_metadata = result.metadata if isinstance(result.metadata, dict) else {}
            if not result.success:
                attempt["success"] = False
                attempt["error"] = str(result_metadata.get("error") or "souffleuse_output_module_failed")
                attempts.append(attempt)
                continue
            parsed = self._parse_narrator_path_output_json(result.content)
            rows = parsed.get("scene_blocks") if isinstance(parsed.get("scene_blocks"), list) else []
            realized, missing_ids = self._realize_souffleuse_module_blocks(
                source_blocks=source_blocks,
                rows=rows,
                source_language=source_language,
                target_language=target_language,
            )
            if missing_ids or len(realized) != len(source_blocks):
                attempt["success"] = False
                attempt["error"] = "souffleuse_output_module_incomplete_blocks"
                attempt["missing_block_ids"] = missing_ids
                attempts.append(attempt)
                continue
            meta = {
                "contract": "souffleuse_output_realization.v1",
                "status": "realized",
                "source_language": source_language,
                "session_output_language": target_language,
                "adapter": str(result_metadata.get("adapter") or getattr(adapter, "adapter_name", "") or provider),
                "adapter_invocation_mode": "souffleuse_output_module",
                "provider": provider,
                "model_id": model_id,
                "api_model": api_model,
                "usage_source": "output_module",
                "block_count": len(realized),
                "attempt_count": len(attempts) + 1,
                "failed_attempts": attempts,
            }
            return realized, self._attach_souffleuse_shadow_judge_meta(realized, meta)

        status = "fallback_output_module_failed"
        last_error = str(attempts[-1].get("error") or "").strip() if attempts else status
        return self._fallback_souffleuse_realization_result(
            source_blocks=source_blocks,
            source_language=source_language,
            target_language=target_language,
            status=status,
            fallback_reason=last_error or status,
            attempts=attempts,
        )

    def _realize_souffleuse_output(
        self,
        *,
        source_blocks: list[dict[str, Any]],
        session: StorySession,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        source_language = SOUFFLEUSE_INTERNAL_LANGUAGE
        target_language = str(session.session_output_language or source_language).strip().lower()[:2] or source_language
        if target_language == source_language or not source_blocks:
            return self._source_projected_souffleuse_output(
                source_blocks=source_blocks,
                source_language=source_language,
                target_language=target_language,
            )
        candidates = self._narrator_path_output_adapter_candidates()
        if not candidates:
            return self._fallback_souffleuse_realization_result(
                source_blocks=source_blocks,
                source_language=source_language,
                target_language=target_language,
                status="fallback_no_output_model",
                fallback_reason="no_non_mock_output_model",
            )
        return self._souffleuse_output_module_result(
            source_blocks=source_blocks,
            source_language=source_language,
            target_language=target_language,
            candidates=candidates,
        )


__all__ = ["_SouffleuseOutputRealizationMixin"]
