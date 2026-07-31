"""Narrator output realization.

Turns narrative commit state and model output into narrator-visible text and structured player-facing blocks.
"""
from __future__ import annotations

from ._deps import *

def _narrator_output_languages(
    *,
    narrator_path: dict[str, Any],
    session: StorySession,
) -> tuple[str, str]:
    source_language = str(narrator_path.get("authoring_language") or "en").strip().lower()[:2] or "en"
    target_language = str(session.session_output_language or source_language).strip().lower()[:2] or source_language
    return source_language, target_language


def _fallback_narrator_output(
    *,
    owner: Any,
    source_blocks: list[dict[str, Any]],
    source_language: str,
    target_language: str,
    status: str,
    fallback_reason: str,
    attempts: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    realized = owner._fallback_narrator_path_output_blocks(
        source_blocks=source_blocks,
        source_language=source_language,
        target_language=target_language,
        status=status,
    )
    metadata = {
        "contract": "narrator_path_output_realization.v1",
        "status": status,
        "source_language": source_language,
        "session_output_language": target_language,
        "visible_output_language": target_language
        if target_language == source_language
        else source_language,
        "adapter": NARRATOR_PATH_ADAPTER,
        "adapter_invocation_mode": NARRATOR_PATH_INVOCATION_MODE,
        "usage_source": "canonical_content_renderer_fallback",
        "fallback_reason": fallback_reason,
        "translation_required": target_language != source_language,
        "output_language_mismatch": target_language != source_language,
    }
    if attempts is not None:
        metadata["failed_attempts"] = attempts
        metadata["attempt_count"] = len(attempts)
    return realized, metadata


def _realized_narrator_blocks_from_rows(
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
    realized = []
    missing_ids: list[str] = []
    for block in source_blocks:
        block_id = str(block.get("id") or "").strip()
        out_row = by_id.get(block_id)
        text = str(out_row.get("text") or "").strip() if isinstance(out_row, dict) else ""
        if not text:
            missing_ids.append(block_id or f"index:{len(realized)}")
            continue
        nb = dict(block)
        nb["source_before_output_module"] = nb.get("source")
        nb["text"] = text
        if "player_display_text" in nb:
            nb["player_display_text"] = text
        nb["source_language"] = source_language
        nb["session_output_language"] = target_language
        nb["visible_output_language"] = target_language
        nb["source"] = "narrator_path_synthesis_module"
        realized.append(nb)
    return realized, missing_ids


def _attempt_narrator_output_candidate(
    *,
    owner: Any,
    candidate: tuple[str, str, Any, str | None, float | None],
    prompt: str,
    source_blocks: list[dict[str, Any]],
    source_language: str,
    target_language: str,
    attempts: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]] | None:
    model_id, provider, adapter, api_model, timeout_seconds = candidate
    attempt: dict[str, Any] = {
        "provider": provider,
        "model_id": model_id,
        "api_model": api_model,
        "adapter": str(getattr(adapter, "adapter_name", "") or provider),
        "timeout_seconds": timeout_seconds or 20.0,
    }
    try:
        result = adapter.generate(prompt, timeout_seconds=timeout_seconds or 20.0, model_name=api_model)
    except Exception as exc:
        attempt["success"] = False
        attempt["error"] = str(exc) or type(exc).__name__
        attempts.append(attempt)
        return None
    result_metadata = result.metadata if isinstance(result.metadata, dict) else {}
    if not result.success:
        attempt["success"] = False
        attempt["error"] = str(result_metadata.get("error") or "narrator_path_synthesis_module_failed")
        attempts.append(attempt)
        return None
    parsed = owner._parse_narrator_path_output_json(result.content)
    rows = parsed.get("scene_blocks") if isinstance(parsed.get("scene_blocks"), list) else []
    realized, missing_ids = _realized_narrator_blocks_from_rows(
        source_blocks=source_blocks,
        rows=rows,
        source_language=source_language,
        target_language=target_language,
    )
    if missing_ids or len(realized) != len(source_blocks):
        attempt["success"] = False
        attempt["error"] = "narrator_path_synthesis_module_incomplete_blocks"
        attempt["missing_block_ids"] = missing_ids
        attempts.append(attempt)
        return None
    return realized, {
        "contract": "narrator_path_output_realization.v1",
        "status": "synthesized",
        "source_language": source_language,
        "session_output_language": target_language,
        "adapter": str(result_metadata.get("adapter") or getattr(adapter, "adapter_name", "") or provider),
        "adapter_invocation_mode": "narrator_path_synthesis_module",
        "provider": provider,
        "model_id": model_id,
        "api_model": api_model,
        "usage_source": "narrator_synthesis_module",
        "block_count": len(realized),
        "attempt_count": len(attempts) + 1,
        "failed_attempts": attempts,
    }


class _NarratorOutputRealizationMixin:
    def _realize_narrator_path_output(
        self,
        *,
        source_blocks: list[dict[str, Any]],
        narrator_path: dict[str, Any],
        session: StorySession,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        source_language, target_language = _narrator_output_languages(
            narrator_path=narrator_path,
            session=session,
        )
        # ADR-0063 Phase 2: optionally enrich each block's ``source_facts`` with
        # the typed W5 narrator projection. Fail-closed flag — when disabled,
        # behavior is identical to pre-Phase-2 (no w5_projection key emitted).
        source_blocks = self._maybe_enrich_blocks_with_w5_narrator_projection(
            session=session, source_blocks=source_blocks
        )
        candidates = self._narrator_path_output_adapter_candidates()
        if not candidates:
            return _fallback_narrator_output(
                owner=self,
                source_blocks=source_blocks,
                source_language=source_language,
                target_language=target_language,
                status="fallback_no_output_model",
                fallback_reason="no_non_mock_output_model",
            )

        prompt = self._narrator_path_output_prompt(
            source_blocks=source_blocks,
            narrator_path=narrator_path,
            source_language=source_language,
            target_language=target_language,
        )
        attempts: list[dict[str, Any]] = []
        for candidate in candidates:
            result = _attempt_narrator_output_candidate(
                owner=self,
                candidate=candidate,
                prompt=prompt,
                source_blocks=source_blocks,
                source_language=source_language,
                target_language=target_language,
                attempts=attempts,
            )
            if result is not None:
                return result

        last_error = str(attempts[-1].get("error") or "").strip() if attempts else ""
        return _fallback_narrator_output(
            owner=self,
            source_blocks=source_blocks,
            source_language=source_language,
            target_language=target_language,
            status="fallback_output_module_failed",
            fallback_reason=last_error or "narrator_path_synthesis_module_failed",
            attempts=attempts,
        )


__all__ = ["_NarratorOutputRealizationMixin"]
