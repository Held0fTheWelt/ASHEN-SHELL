from __future__ import annotations

from importlib import import_module


def test_runtime_executor_boundaries_are_semantic_and_complete() -> None:
    from ai_stack.langgraph.runtime_executor.semantic_boundaries import (
        SOURCE_BOUNDARIES,
        iter_source_module_names,
    )

    boundary_names = [boundary.name for boundary in SOURCE_BOUNDARIES]
    assert boundary_names == [
        "imports",
        "semantic_input",
        "actor_lanes",
        "runtime_aspect_records",
        "retrieval",
        "npc_projection",
        "dramatic_packet",
        "director",
        "executor_shell",
        "input_action_pipeline",
        "director_pipeline",
        "aspect_derivation",
        "model_pipeline",
        "commit_render",
    ]

    source_modules = iter_source_module_names()
    assert len(source_modules) == len(set(source_modules))
    assert all(not name.endswith(("_01", "_02", "_03", "_04", "_05", "_06")) for name in source_modules)

    for module_name in source_modules:
        module = import_module(f"ai_stack.langgraph.runtime_executor.{module_name}")
        assert getattr(module, "SOURCE_LINES")


def test_runtime_executor_facade_still_exports_executor_without_loader_group_map() -> None:
    import ai_stack.langgraph.langgraph_runtime_executor as facade
    import ai_stack.langgraph.runtime_executor.public as public

    assert hasattr(facade, "RuntimeTurnGraphExecutor")
    assert not hasattr(public, "_GROUPS")
    assert hasattr(facade, "_build_dramatic_generation_packet")
    assert hasattr(facade, "resolve_w5_first_npc_context")
