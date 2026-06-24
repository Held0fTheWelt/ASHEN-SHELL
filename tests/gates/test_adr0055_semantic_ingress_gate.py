"""ADR-0055 / world-engine SAD D14 — semantic input translation ingress gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from story_runtime_core import RoutingPolicy, interpret_player_input
from story_runtime_core.adapters import BaseModelAdapter, ModelCallResult
from story_runtime_core.model_registry import build_default_registry

langgraph_runtime = pytest.importorskip(
    "ai_stack.langgraph.langgraph_runtime",
    reason="LangGraph/LangChain stack required for semantic ingress gate",
)
from ai_stack.langgraph.langgraph_runtime import RuntimeTurnGraphExecutor
from ai_stack.rag import ContextPackAssembler, ContextRetriever, RagIngestionPipeline

SEMANTIC_INPUT_TRANSLATION_SCHEMA_VERSION = "semantic_language_adapter.input_translation.v1"


class _IngressSemanticAdapter(BaseModelAdapter):
    adapter_name = "openai"

    def __init__(self, semantic_action: dict) -> None:
        self.semantic_action = dict(semantic_action)
        self.prompts: list[str] = []

    def generate(
        self,
        prompt: str,
        *,
        timeout_seconds: float = 10.0,
        retrieval_context: str | None = None,
        model_name: str | None = None,
    ) -> ModelCallResult:
        self.prompts.append(prompt)
        return ModelCallResult(
            content=json.dumps({"semantic_action": dict(self.semantic_action)}),
            success=True,
            metadata={"adapter": self.adapter_name, "model_name": model_name},
        )


def _build_executor(tmp_path: Path, semantic_action: dict) -> tuple[RuntimeTurnGraphExecutor, _IngressSemanticAdapter]:
    content_file = tmp_path / "content" / "god_of_carnage.md"
    content_file.parent.mkdir(parents=True, exist_ok=True)
    content_file.write_text("God of Carnage semantic ingress gate sample.", encoding="utf-8")
    corpus = RagIngestionPipeline().build_corpus(tmp_path)
    registry = build_default_registry()
    routing = RoutingPolicy(registry)
    translator = _IngressSemanticAdapter(semantic_action)
    graph = RuntimeTurnGraphExecutor(
        interpreter=interpret_player_input,
        routing=routing,
        registry=registry,
        adapters={"openai": translator},
        retriever=ContextRetriever(corpus),
        assembler=ContextPackAssembler(),
    )
    return graph, translator


def test_translate_player_input_uses_catalog_backed_semantic_prompt(tmp_path: Path) -> None:
    graph, translator = _build_executor(
        tmp_path,
        {
            "normalized_english_text": "Go to the kitchen.",
            "commit_policy": "commit_action",
            "confidence": "high",
        },
    )
    graph._translate_player_input(
        {
            "module_id": "god_of_carnage",
            "player_input": "Gehe in die Kueche",
            "session_input_language": "de",
            "session_output_language": "de",
            "turn_number": 1,
        }
    )
    assert translator.prompts
    prompt = translator.prompts[0]
    assert "content_catalog" in prompt
    assert "semantic_resolution_contract" in prompt
    assert "Resolve the player input before any story turn processing." in prompt


def test_translate_player_input_produces_bounded_semantic_evidence(tmp_path: Path) -> None:
    graph, _translator = _build_executor(
        tmp_path,
        {
            "normalized_english_text": "Go to the kitchen.",
            "player_input_kind": "physical_action",
            "action_kind": "go_to",
            "verb": "go_to",
            "target_query_english": "the kitchen",
            "resolved_target_id": "kitchen",
            "resolved_target_type": "location",
            "commit_policy": "commit_action",
            "confidence": "high",
        },
    )
    update = graph._translate_player_input(
        {
            "module_id": "god_of_carnage",
            "player_input": "Gehe in die Kueche",
            "session_input_language": "de",
            "session_output_language": "de",
            "turn_number": 1,
        }
    )
    translation = update["input_translation"]
    assert translation["schema_version"] == SEMANTIC_INPUT_TRANSLATION_SCHEMA_VERSION
    assert translation["status"] == "resolved"
    assert translation["semantic_resolution_required"] is False
    assert isinstance(translation.get("semantic_action"), dict)
    assert translation["semantic_action"].get("resolved_target_id") == "kitchen"
    assert translation.get("normalized_english_text") == "Go to the kitchen."
    assert translation["session_input_language"] == "de"
    assert translation["session_output_language"] == "de"


def test_graph_runs_translate_player_input_before_interpret_input(tmp_path: Path) -> None:
    graph, _translator = _build_executor(
        tmp_path,
        {
            "normalized_english_text": "Go to the kitchen.",
            "player_input_kind": "physical_action",
            "action_kind": "go_to",
            "verb": "go_to",
            "commit_policy": "commit_action",
            "confidence": "high",
        },
    )
    result = graph.run(
        session_id="session_adr0055_gate",
        module_id="god_of_carnage",
        current_scene_id="living_room",
        player_input="Gehe in die Kueche",
        turn_number=1,
    )
    nodes = result["graph_diagnostics"]["nodes_executed"]
    assert "translate_player_input" in nodes
    assert "interpret_input" in nodes
    assert nodes.index("translate_player_input") < nodes.index("interpret_input")
