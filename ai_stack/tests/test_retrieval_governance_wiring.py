"""Tests that governed retrieval config flows correctly through the live turn path.

Verifies:
- RuntimeRetrievalConfig defaults
- retrieval_config_from_governed factory
- RuntimeTurnGraphExecutor respects disabled / sparse_only / hybrid modes
- ContextRetriever records last_retrieval_route
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from ai_stack.rag_retrieval_dtos import (
    RuntimeRetrievalConfig,
    retrieval_config_from_governed,
)


# ---------------------------------------------------------------------------
# RuntimeRetrievalConfig unit tests
# ---------------------------------------------------------------------------

class TestRuntimeRetrievalConfigDefaults:
    def test_default_mode_is_hybrid(self) -> None:
        rc = RuntimeRetrievalConfig()
        assert rc.retrieval_execution_mode == "hybrid_dense_sparse"
        assert not rc.use_sparse_only
        assert not rc.retrieval_disabled

    def test_sparse_only_mode(self) -> None:
        rc = RuntimeRetrievalConfig(retrieval_execution_mode="sparse_only")
        assert rc.use_sparse_only
        assert not rc.retrieval_disabled

    def test_disabled_mode(self) -> None:
        rc = RuntimeRetrievalConfig(retrieval_execution_mode="disabled")
        assert rc.retrieval_disabled
        assert not rc.use_sparse_only  # disabled ≠ sparse_only

    def test_embeddings_enabled_false_forces_sparse(self) -> None:
        rc = RuntimeRetrievalConfig(embeddings_enabled=False)
        assert rc.use_sparse_only

    def test_embeddings_enabled_false_with_hybrid_mode(self) -> None:
        rc = RuntimeRetrievalConfig(
            retrieval_execution_mode="hybrid_dense_sparse",
            embeddings_enabled=False,
        )
        assert rc.use_sparse_only
        assert not rc.retrieval_disabled


# ---------------------------------------------------------------------------
# retrieval_config_from_governed factory
# ---------------------------------------------------------------------------

class TestRetrievalConfigFromGoverned:
    def test_none_input_returns_defaults(self) -> None:
        rc = retrieval_config_from_governed(None)
        assert rc.retrieval_execution_mode == "hybrid_dense_sparse"
        assert rc.max_chunks == 4
        assert rc.retrieval_profile == "runtime_turn_support"
        assert rc.retrieval_min_score is None
        assert rc.embeddings_enabled is True

    def test_empty_dict_returns_defaults(self) -> None:
        rc = retrieval_config_from_governed({})
        assert rc.retrieval_execution_mode == "hybrid_dense_sparse"

    def test_reads_top_level_retrieval_execution_mode(self) -> None:
        rc = retrieval_config_from_governed({"retrieval_execution_mode": "disabled"})
        assert rc.retrieval_disabled

    def test_reads_retrieval_settings_subdict(self) -> None:
        rc = retrieval_config_from_governed(
            {
                "retrieval_execution_mode": "hybrid_dense_sparse",
                "retrieval_settings": {
                    "retrieval_top_k": 8,
                    "retrieval_profile": "writers_review",
                    "retrieval_min_score": 0.25,
                    "embeddings_enabled": False,
                    "retrieval_execution_mode": "sparse_only",
                },
            }
        )
        # top-level wins for mode
        assert rc.retrieval_execution_mode == "hybrid_dense_sparse"
        assert rc.max_chunks == 8
        assert rc.retrieval_profile == "writers_review"
        assert rc.retrieval_min_score == pytest.approx(0.25)
        assert rc.embeddings_enabled is False

    def test_fallback_mode_from_retrieval_settings_when_top_level_absent(self) -> None:
        rc = retrieval_config_from_governed(
            {"retrieval_settings": {"retrieval_execution_mode": "sparse_only"}}
        )
        assert rc.retrieval_execution_mode == "sparse_only"
        assert rc.use_sparse_only

    def test_max_chunks_clamped_to_12(self) -> None:
        rc = retrieval_config_from_governed(
            {"retrieval_settings": {"retrieval_top_k": 99}}
        )
        assert rc.max_chunks == 12

    def test_max_chunks_clamped_to_1(self) -> None:
        rc = retrieval_config_from_governed(
            {"retrieval_settings": {"retrieval_top_k": 0}}
        )
        assert rc.max_chunks == 1

    def test_invalid_max_chunks_falls_back_to_4(self) -> None:
        rc = retrieval_config_from_governed(
            {"retrieval_settings": {"retrieval_top_k": "not-a-number"}}
        )
        assert rc.max_chunks == 4

    def test_sparse_only_mode_sets_use_sparse_only(self) -> None:
        rc = retrieval_config_from_governed(
            {"retrieval_execution_mode": "sparse_only"}
        )
        assert rc.use_sparse_only
        assert not rc.retrieval_disabled


# ---------------------------------------------------------------------------
# ContextRetriever last-observed tracking
# ---------------------------------------------------------------------------

class TestContextRetrieverLastObserved:
    def test_last_route_set_after_retrieve(self, tmp_path: Path) -> None:
        from ai_stack.rag import build_runtime_retriever

        (tmp_path / "content").mkdir()
        (tmp_path / "content" / "mod.md").write_text(
            "God of Carnage: a play about civility and violence.", encoding="utf-8"
        )
        retriever, _, _ = build_runtime_retriever(tmp_path)
        assert retriever.last_retrieval_route == ""  # unset before first call

        from ai_stack.rag_retrieval_dtos import RetrievalRequest
        from ai_stack.rag_types import RetrievalDomain

        retriever.retrieve(
            RetrievalRequest(
                domain=RetrievalDomain.RUNTIME,
                profile="runtime_turn_support",
                query="civility violence",
            )
        )
        assert retriever.last_retrieval_route in ("hybrid", "sparse_fallback")

    def test_last_route_sparse_when_embeddings_disabled(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("WOS_RAG_DISABLE_EMBEDDINGS", "1")
        from ai_stack.semantic_embedding import clear_embedding_model_singleton
        clear_embedding_model_singleton()

        from ai_stack.rag import build_runtime_retriever

        (tmp_path / "content").mkdir()
        (tmp_path / "content" / "mod.md").write_text("test content", encoding="utf-8")
        retriever, _, _ = build_runtime_retriever(tmp_path)

        from ai_stack.rag_retrieval_dtos import RetrievalRequest
        from ai_stack.rag_types import RetrievalDomain

        retriever.retrieve(
            RetrievalRequest(
                domain=RetrievalDomain.RUNTIME,
                profile="runtime_turn_support",
                query="test",
            )
        )
        assert retriever.last_retrieval_route == "sparse_fallback"
        clear_embedding_model_singleton()


# ---------------------------------------------------------------------------
# RuntimeTurnGraphExecutor respects retrieval_config (unit-level)
# ---------------------------------------------------------------------------

class TestExecutorRetrievalConfigWiring:
    """Verify _retrieve_context honours retrieval_config without running the full graph."""

    def _make_minimal_executor(self, retrieval_config: RuntimeRetrievalConfig):
        """Build the minimum executor needed to call _retrieve_context."""
        from ai_stack.langgraph_runtime_executor import RuntimeTurnGraphExecutor
        from ai_stack.rag_context_retriever import ContextRetriever
        from ai_stack.rag_context_pack_assembler import ContextPackAssembler
        from ai_stack.rag_corpus import InMemoryRetrievalCorpus

        corpus = InMemoryRetrievalCorpus(chunks=[], built_at="2026-01-01T00:00:00Z", source_count=0)
        retriever = ContextRetriever(corpus)
        assembler = ContextPackAssembler()

        # Minimal stubs for required constructor fields
        routing = MagicMock()
        registry = MagicMock()
        registry.list_routes.return_value = []
        adapters = {}

        executor = RuntimeTurnGraphExecutor(
            interpreter=lambda x: {"kind": "action", "intent": x},
            routing=routing,
            registry=registry,
            adapters=adapters,
            retriever=retriever,
            assembler=assembler,
            retrieval_config=retrieval_config,
        )
        return executor

    def _minimal_state(self) -> dict:
        return {
            "player_input": "hello",
            "current_scene_id": "scene_1",
            "module_id": "god_of_carnage",
            "nodes_executed": [],
            "graph_errors": [],
        }

    def test_disabled_mode_skips_retrieval(self) -> None:
        rc = RuntimeRetrievalConfig(retrieval_execution_mode="disabled")
        executor = self._make_minimal_executor(rc)
        state = self._minimal_state()
        result = executor._retrieve_context(state)
        assert result["retrieval"]["retrieval_route"] == "disabled_by_config"
        assert result["retrieval"]["status"] == "skipped"
        assert result["context_text"] == ""

    def test_disabled_mode_profile_preserved(self) -> None:
        rc = RuntimeRetrievalConfig(
            retrieval_execution_mode="disabled",
            retrieval_profile="writers_review",
        )
        executor = self._make_minimal_executor(rc)
        result = executor._retrieve_context(self._minimal_state())
        assert result["retrieval"]["profile"] == "writers_review"

    def test_sparse_only_sets_use_sparse_only_on_request(self) -> None:
        rc = RuntimeRetrievalConfig(retrieval_execution_mode="sparse_only")
        executor = self._make_minimal_executor(rc)
        captured: list[Any] = []
        original_retrieve = executor.retriever.retrieve

        def spy(request):
            captured.append(request)
            return original_retrieve(request)

        executor.retriever.retrieve = spy
        executor._retrieve_context(self._minimal_state())
        assert captured, "retrieve() was not called"
        assert captured[0].use_sparse_only is True

    def test_hybrid_mode_does_not_force_sparse(self) -> None:
        rc = RuntimeRetrievalConfig(retrieval_execution_mode="hybrid_dense_sparse")
        executor = self._make_minimal_executor(rc)
        captured: list[Any] = []
        original_retrieve = executor.retriever.retrieve

        def spy(request):
            captured.append(request)
            return original_retrieve(request)

        executor.retriever.retrieve = spy
        executor._retrieve_context(self._minimal_state())
        assert captured
        assert captured[0].use_sparse_only is False

    def test_max_chunks_respected(self) -> None:
        rc = RuntimeRetrievalConfig(max_chunks=7)
        executor = self._make_minimal_executor(rc)
        captured: list[Any] = []
        original_retrieve = executor.retriever.retrieve

        def spy(request):
            captured.append(request)
            return original_retrieve(request)

        executor.retriever.retrieve = spy
        executor._retrieve_context(self._minimal_state())
        assert captured
        assert captured[0].max_chunks == 7

    def test_profile_respected(self) -> None:
        rc = RuntimeRetrievalConfig(retrieval_profile="improvement_eval")
        executor = self._make_minimal_executor(rc)
        captured: list[Any] = []
        original_retrieve = executor.retriever.retrieve

        def spy(request):
            captured.append(request)
            return original_retrieve(request)

        executor.retriever.retrieve = spy
        executor._retrieve_context(self._minimal_state())
        assert captured
        assert captured[0].profile == "improvement_eval"

    def test_min_score_filters_sources(self, tmp_path: Path) -> None:
        """Sources below min_score threshold are removed."""
        from ai_stack.langgraph_runtime_executor import RuntimeTurnGraphExecutor
        from ai_stack.rag_context_retriever import ContextRetriever
        from ai_stack.rag_corpus import InMemoryRetrievalCorpus
        from ai_stack.rag_context_pack_assembler import ContextPackAssembler

        rc = RuntimeRetrievalConfig(retrieval_min_score=0.5)

        # Patch assembler.assemble to return a pack with mixed-score sources
        corpus = InMemoryRetrievalCorpus(chunks=[], built_at="2026-01-01T00:00:00Z", source_count=0)
        retriever = ContextRetriever(corpus)
        assembler = ContextPackAssembler()

        from ai_stack.rag_retrieval_dtos import ContextPack, RetrievalResult, RetrievalRequest
        from ai_stack.rag_types import RetrievalDomain, RetrievalStatus

        fake_pack = ContextPack(
            summary="",
            compact_context="ctx",
            sources=[
                {"chunk_id": "a", "score": 0.8, "source_path": "p1", "source_name": "n1",
                 "content_class": "authored_module", "source_version": "1", "snippet": "",
                 "selection_reason": "", "pack_role": "", "why_selected": ""},
                {"chunk_id": "b", "score": 0.3, "source_path": "p2", "source_name": "n2",
                 "content_class": "authored_module", "source_version": "1", "snippet": "",
                 "selection_reason": "", "pack_role": "", "why_selected": ""},
            ],
            hit_count=2,
            profile="runtime_turn_support",
            domain="runtime",
            status="ok",
            ranking_notes=[],
        )
        assembler.assemble = lambda _r: fake_pack

        routing = MagicMock()
        registry = MagicMock()
        registry.list_routes.return_value = []

        executor = RuntimeTurnGraphExecutor(
            interpreter=lambda x: {"kind": "action", "intent": x},
            routing=routing,
            registry=registry,
            adapters={},
            retriever=retriever,
            assembler=assembler,
            retrieval_config=rc,
        )
        result = executor._retrieve_context(self._minimal_state())
        sources = result["retrieval"]["sources"]
        assert len(sources) == 1
        assert float(sources[0]["score"]) >= 0.5
