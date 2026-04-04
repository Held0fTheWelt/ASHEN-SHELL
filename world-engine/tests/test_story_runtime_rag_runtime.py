from __future__ import annotations

from story_runtime_core.adapters import BaseModelAdapter, ModelCallResult
from wos_ai_stack import ContextPackAssembler, ContextRetriever, RagIngestionPipeline

from app.story_runtime import StoryRuntimeManager


class CaptureAdapter(BaseModelAdapter):
    adapter_name = "mock"

    def __init__(self) -> None:
        self.last_prompt: str | None = None
        self.last_retrieval_context: str | None = None

    def generate(self, prompt: str, *, timeout_seconds: float = 10.0, retrieval_context: str | None = None) -> ModelCallResult:
        self.last_prompt = prompt
        self.last_retrieval_context = retrieval_context
        return ModelCallResult(content="ok", success=True, metadata={"adapter": self.adapter_name})


class FailingAdapter(BaseModelAdapter):
    adapter_name = "failing"

    def generate(self, prompt: str, *, timeout_seconds: float = 10.0, retrieval_context: str | None = None) -> ModelCallResult:
        return ModelCallResult(content="", success=False, metadata={"error": "forced_failure"})


def test_story_runtime_retrieval_context_influences_authoritative_turn(tmp_path):
    content_file = tmp_path / "content" / "god_of_carnage.md"
    content_file.parent.mkdir(parents=True, exist_ok=True)
    content_file.write_text(
        "God of Carnage scene where two families argue about their children.",
        encoding="utf-8",
    )
    corpus = RagIngestionPipeline().build_corpus(tmp_path)
    assert corpus.chunks

    adapter = CaptureAdapter()
    manager = StoryRuntimeManager(
        adapters={"mock": adapter, "openai": adapter, "ollama": adapter},
        retriever=ContextRetriever(corpus),
        context_assembler=ContextPackAssembler(),
    )
    session = manager.create_session(
        module_id="god_of_carnage",
        runtime_projection={"start_scene_id": "scene_1", "scenes": []},
    )
    turn = manager.execute_turn(session_id=session.session_id, player_input="I open the door")

    assert "retrieval" in turn
    assert turn["retrieval"]["domain"] == "runtime"
    assert "status" in turn["retrieval"]
    assert turn["model_route"]["generation"]["retrieval_context_attached"] is True
    assert adapter.last_retrieval_context
    assert any(
        entry["capability_name"] == "wos.context_pack.build"
        for entry in turn["graph"]["capability_audit"]
    )


def test_story_runtime_graph_uses_fallback_branch_on_model_failure(tmp_path):
    content_file = tmp_path / "content" / "god_of_carnage.md"
    content_file.parent.mkdir(parents=True, exist_ok=True)
    content_file.write_text("God of Carnage fallback branch test content.", encoding="utf-8")
    corpus = RagIngestionPipeline().build_corpus(tmp_path)
    retriever = ContextRetriever(corpus)
    assembler = ContextPackAssembler()

    mock_adapter = CaptureAdapter()
    failing_adapter = FailingAdapter()
    manager = StoryRuntimeManager(
        adapters={"openai": failing_adapter, "ollama": failing_adapter, "mock": mock_adapter},
        retriever=retriever,
        context_assembler=assembler,
    )
    session = manager.create_session(
        module_id="god_of_carnage",
        runtime_projection={"start_scene_id": "scene_1", "scenes": []},
    )

    turn = manager.execute_turn(session_id=session.session_id, player_input="I escalate the argument")

    assert turn["graph"]["fallback_path_taken"] is True
    assert "fallback_model" in turn["graph"]["nodes_executed"]
    assert turn["model_route"]["generation"]["fallback_used"] is True
