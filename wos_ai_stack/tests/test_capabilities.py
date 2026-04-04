from __future__ import annotations

from pathlib import Path

import pytest

from wos_ai_stack import (
    CapabilityAccessDeniedError,
    CapabilityValidationError,
    ContextPackAssembler,
    ContextRetriever,
    RagIngestionPipeline,
    create_default_capability_registry,
)


def _build_registry(tmp_path: Path):
    content_file = tmp_path / "content" / "god_of_carnage.md"
    content_file.parent.mkdir(parents=True, exist_ok=True)
    content_file.write_text("God of Carnage capability retrieval sample.", encoding="utf-8")
    corpus = RagIngestionPipeline().build_corpus(tmp_path)
    retriever = ContextRetriever(corpus)
    assembler = ContextPackAssembler()
    return create_default_capability_registry(retriever=retriever, assembler=assembler, repo_root=tmp_path)


def test_capability_registration_exposes_schema_and_modes(tmp_path: Path) -> None:
    registry = _build_registry(tmp_path)
    capabilities = registry.list_capabilities()

    assert any(cap["name"] == "wos.context_pack.build" for cap in capabilities)
    context_pack_cap = next(cap for cap in capabilities if cap["name"] == "wos.context_pack.build")
    assert "profile" in context_pack_cap["input_schema"]["required"]
    assert "runtime" in context_pack_cap["allowed_modes"]


def test_capability_denied_access_is_typed_and_audited(tmp_path: Path) -> None:
    registry = _build_registry(tmp_path)
    with pytest.raises(CapabilityAccessDeniedError):
        registry.invoke(
            name="wos.review_bundle.build",
            mode="runtime",
            actor="runtime_turn_graph",
            payload={"module_id": "god_of_carnage"},
        )
    audit = registry.recent_audit(limit=1)[0]
    assert audit["outcome"] == "denied"
    assert audit["capability_name"] == "wos.review_bundle.build"


def test_capability_validation_failure_is_typed_and_audited(tmp_path: Path) -> None:
    registry = _build_registry(tmp_path)
    with pytest.raises(CapabilityValidationError):
        registry.invoke(
            name="wos.context_pack.build",
            mode="runtime",
            actor="runtime_turn_graph",
            payload={"query": "missing profile"},
        )
    audit = registry.recent_audit(limit=1)[0]
    assert audit["outcome"] == "error"


def test_runtime_context_pack_capability_returns_retrieval_payload(tmp_path: Path) -> None:
    registry = _build_registry(tmp_path)
    result = registry.invoke(
        name="wos.context_pack.build",
        mode="runtime",
        actor="runtime_turn_graph",
        payload={
            "domain": "runtime",
            "profile": "runtime_turn_support",
            "query": "god of carnage sample",
            "module_id": "god_of_carnage",
            "scene_id": "scene_1",
        },
    )

    assert "retrieval" in result
    assert result["retrieval"]["profile"] == "runtime_turn_support"
    assert "context_text" in result
    assert registry.recent_audit(limit=1)[0]["outcome"] == "allowed"
