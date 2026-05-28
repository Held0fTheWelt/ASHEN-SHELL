from __future__ import annotations

import json
from pathlib import Path

from story_runtime_core.adapters import BaseModelAdapter, ModelCallResult
from story_runtime_core.model_registry import RoutingPolicy, build_default_registry

from ai_stack.langgraph.langgraph_runtime import RuntimeTurnGraphExecutor
from ai_stack.language_io.language_adapter import load_session_language_model_directive


class OutputTranslationAdapter(BaseModelAdapter):
    adapter_name = "openai"

    def __init__(
        self,
        translations: list[str] | None = None,
        *,
        success: bool = True,
        error: Exception | None = None,
    ) -> None:
        self.translations = list(translations or [])
        self.success = success
        self.error = error
        self.prompts: list[str] = []
        self.model_names: list[str | None] = []

    def generate(
        self,
        prompt: str,
        *,
        timeout_seconds: float = 10.0,
        retrieval_context: str | None = None,
        model_name: str | None = None,
    ) -> ModelCallResult:
        self.prompts.append(prompt)
        self.model_names.append(model_name)
        assert timeout_seconds == 30.0
        assert retrieval_context is None
        if self.error is not None:
            raise self.error
        if not self.success:
            return ModelCallResult(content="", success=False, metadata={"error": "forced_translation_failure"})
        return ModelCallResult(
            content=json.dumps({"translated": list(self.translations)}),
            success=True,
            metadata={"adapter": self.adapter_name},
        )


def _executor(adapter: BaseModelAdapter | None = None) -> RuntimeTurnGraphExecutor:
    registry = build_default_registry()
    graph = object.__new__(RuntimeTurnGraphExecutor)
    graph.routing = RoutingPolicy(registry)
    graph.registry = registry
    graph.adapters = {"openai": adapter} if adapter is not None else {}
    return graph


def test_translate_output_registered_between_render_and_package() -> None:
    from ai_stack.langgraph.runtime_executor.executor_graph_build import SOURCE_LINES
    from ai_stack.langgraph.runtime_executor.semantic_boundaries import SOURCE_BOUNDARIES

    boundary = next(b for b in SOURCE_BOUNDARIES if b.name == "commit_render")
    assert boundary.modules == (
        "executor_validation_commit",
        "executor_commit_render_start",
        "executor_visible_render",
        "executor_output_translation",
        "executor_package_output",
    )

    source = "".join(SOURCE_LINES)
    assert 'graph.add_node("translate_output", self._translate_output)' in source
    assert 'graph.add_edge("render_visible", "translate_output")' in source
    assert 'graph.add_edge("translate_output", "package_output")' in source
    assert hasattr(RuntimeTurnGraphExecutor, "_translate_output")


def test_narrator_prompt_language_workarounds_are_removed() -> None:
    from ai_stack.langgraph.runtime_executor.executor_goc_canonical_content import SOURCE_LINES

    source = "".join(SOURCE_LINES)
    assert "OUTPUT LANGUAGE" not in source
    assert "Never default to English" not in source
    assert "Do not use English" not in source
    assert "Use second-person address in session_output_language" not in source
    assert "in-world label in the session_output_language" not in source

    prompts = json.loads(Path("prompts/ai_stack/core_prompts.json").read_text(encoding="utf-8"))
    runtime_prompt = next(p for p in prompts["prompts"] if p["prompt_key"] == "runtime_turn_system")
    runtime_text = "\n".join(runtime_prompt["template_lines"])
    assert "OUTPUT LANGUAGE" not in runtime_text
    assert "Never default to English" not in runtime_text
    assert "PLAYER-VISIBLE TYPOGRAPHY (spoken vs stage)" in runtime_text


def test_session_language_directive_keeps_output_language_as_metadata() -> None:
    text = load_session_language_model_directive(
        module_id="god_of_carnage",
        lang="en",
        session_input_language="de",
    )

    assert "session_input_language=de" in text
    assert "session_output_language=en" in text
    assert "translate/normalize it to English" in text
    assert "output translation gateway" in text
    assert "player-visible narration in session_output_language" not in text


def test_translate_output_skips_adapter_for_english_output() -> None:
    translator = OutputTranslationAdapter(["unused"])
    graph = _executor(translator)

    update = graph._translate_output(
        {
            "session_output_language": "en",
            "visible_output_bundle": {"gm_narration": ["The room is quiet."]},
        }
    )

    assert update["output_translation"]["status"] == "skipped_same_language"
    assert "visible_output_bundle" not in update
    assert translator.prompts == []


def test_translate_output_updates_only_visible_text_fields() -> None:
    translator = OutputTranslationAdapter(
        [
            "Der Raum ist still.",
            '"Guten Tag."',
            "Annette legt die Hand auf den Tisch.",
        ]
    )
    graph = _executor(translator)
    original_bundle = {
        "gm_narration": ["The room is quiet."],
        "spoken_lines": [{"speaker_id": "annette_reille", "text": '"Hello."'}],
        "action_lines": [{"actor_id": "annette_reille", "text": "Annette sets her hand on the table."}],
    }

    update = graph._translate_output(
        {
            "session_output_language": "de",
            "visible_output_bundle": original_bundle,
        }
    )

    assert update["output_translation"]["status"] == "translated"
    assert update["output_translation"]["language"] == "de"
    assert update["output_translation"]["count"] == 3
    translated = update["visible_output_bundle"]
    assert translated["gm_narration"] == ["Der Raum ist still."]
    assert translated["spoken_lines"] == [{"speaker_id": "annette_reille", "text": '"Guten Tag."'}]
    assert translated["action_lines"] == [
        {"actor_id": "annette_reille", "text": "Annette legt die Hand auf den Tisch."}
    ]
    assert original_bundle["gm_narration"] == ["The room is quiet."]
    assert original_bundle["spoken_lines"][0]["text"] == '"Hello."'


def test_translate_output_passthrough_statuses_leave_bundle_unmodified() -> None:
    unavailable_graph = _executor()
    unavailable_update = unavailable_graph._translate_output(
        {
            "session_output_language": "de",
            "visible_output_bundle": {"gm_narration": ["The room is quiet."]},
        }
    )
    assert unavailable_update["output_translation"]["status"] == "adapter_unavailable"
    assert "visible_output_bundle" not in unavailable_update

    failing_graph = _executor(OutputTranslationAdapter(error=RuntimeError("boom")))
    failing_update = failing_graph._translate_output(
        {
            "session_output_language": "de",
            "visible_output_bundle": {"gm_narration": ["The room is quiet."]},
        }
    )
    assert failing_update["output_translation"]["status"] == "adapter_error_passthrough"
    assert "visible_output_bundle" not in failing_update

    mismatch_graph = _executor(OutputTranslationAdapter(["eins", "zwei"]))
    mismatch_update = mismatch_graph._translate_output(
        {
            "session_output_language": "de",
            "visible_output_bundle": {"gm_narration": ["The room is quiet."]},
        }
    )
    assert mismatch_update["output_translation"]["status"] == "length_mismatch_passthrough"
    assert "visible_output_bundle" not in mismatch_update
