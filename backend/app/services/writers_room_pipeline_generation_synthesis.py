"""Writers Room generation stage — synthesis routing, LangChain primary path, mock fallback, evidence."""

from __future__ import annotations

from typing import Any

from ai_stack import invoke_writers_room_adapter_with_langchain

from app.runtime.model_routing import route_model
from app.runtime.model_routing_contracts import (
    AdapterModelSpec,
    RoutingRequest,
    TaskKind,
    WorkflowPhase,
)
from app.runtime.model_routing_evidence import attach_stage_routing_evidence


def _norm_wr_adapter(name: str | None) -> str:
    return (name or "").strip().lower()


def route_synthesis_and_build_generation_shell(
    *,
    specs: list[AdapterModelSpec],
    preflight_trace: dict[str, Any],
) -> tuple[Any, dict[str, Any], dict[str, Any], str]:
    """Return synthesis decision, synthesis_trace, initial generation dict, selected_provider."""
    synthesis_req = RoutingRequest(
        workflow_phase=WorkflowPhase.generation,
        task_kind=TaskKind.narrative_formulation,
        requires_structured_output=True,
    )
    syn_decision = route_model(synthesis_req, specs=specs)
    synthesis_trace: dict[str, Any] = {
        "stage": "synthesis",
        "workflow_phase": WorkflowPhase.generation.value,
        "task_kind": TaskKind.narrative_formulation.value,
        "decision": syn_decision.model_dump(mode="json"),
    }
    selected_provider = syn_decision.selected_adapter_name or "mock"
    generation: dict[str, Any] = {
        "provider": selected_provider,
        "success": False,
        "content": "",
        "error": None,
        "adapter_invocation_mode": None,
        "raw_fallback_reason": None,
        "metadata": {},
        "task_2a_routing": {"preflight": preflight_trace, "synthesis": synthesis_trace},
    }
    return syn_decision, synthesis_req, synthesis_trace, generation


def fill_generation_from_primary_adapter(
    *,
    generation: dict[str, Any],
    adapter: Any | None,
    module_id: str,
    focus: str,
    retrieval_text: str,
    selected_provider: str,
) -> None:
    """Mutate generation when a real adapter is available (LangChain structured path)."""
    if not adapter:
        generation["error"] = f"adapter_not_registered:{selected_provider}"
        generation["raw_fallback_reason"] = "primary_adapter_missing"
        return
    wr_result = invoke_writers_room_adapter_with_langchain(
        adapter=adapter,
        module_id=module_id,
        focus=focus,
        retrieval_context=retrieval_text or None,
        timeout_seconds=12.0,
    )
    generation["success"] = wr_result.call.success
    generation["error"] = wr_result.call.metadata.get("error") if not wr_result.call.success else None
    generation["adapter_invocation_mode"] = "langchain_structured_primary"
    if wr_result.parsed_output is not None:
        notes = (wr_result.parsed_output.review_notes or "").strip()
        generation["content"] = notes or wr_result.call.content
        generation["metadata"] = {
            "langchain_prompt_used": True,
            "langchain_parser_error": None,
            "structured_output": wr_result.parsed_output.model_dump(mode="json"),
        }
    elif wr_result.call.success:
        generation["content"] = wr_result.call.content
        generation["metadata"] = {
            "langchain_prompt_used": True,
            "langchain_parser_error": wr_result.parser_error,
            "structured_output": None,
        }
    else:
        generation["content"] = ""
        generation["metadata"] = {
            "langchain_prompt_used": True,
            "langchain_parser_error": wr_result.parser_error,
            "structured_output": None,
        }


def apply_generation_mock_fallback(
    *,
    generation: dict[str, Any],
    adapters: dict[str, Any],
    module_id: str,
    focus: str,
    retrieval_text: str,
) -> None:
    """If primary path failed, try mock/raw adapter fallback (mutates generation)."""
    if generation["success"]:
        return
    fallback = adapters.get("mock")
    fallback_prompt = (
        f"Writers-Room review for module={module_id}.\n"
        f"Focus: {focus}\n"
        f"Use evidence from retrieved context and produce concise recommendations.\n\n"
        f"{retrieval_text}"
    )
    if fallback:
        call = fallback.generate(fallback_prompt, timeout_seconds=5.0, retrieval_context=retrieval_text or None)
        generation["provider"] = "mock"
        generation["success"] = call.success
        generation["content"] = call.content
        generation["error"] = call.metadata.get("error") if not call.success else None
        generation["adapter_invocation_mode"] = "raw_adapter_fallback"
        generation["raw_fallback_reason"] = (
            generation.get("raw_fallback_reason") or "primary_failed_or_unavailable"
        )
        generation["metadata"] = {
            "langchain_prompt_used": False,
            "langchain_parser_error": None,
            "structured_output": None,
            "bypass_note": (
                "Mock/raw fallback skips LangChain structured parse because default mock output is not JSON; "
                "graph-runtime primary path uses the same pattern."
            ),
        }


def attach_synthesis_routing_evidence(
    *,
    generation: dict[str, Any],
    synthesis_req: RoutingRequest,
    syn_decision: Any,
) -> None:
    """Annotate synthesis trace with execution vs routing deltas."""
    syn_stage = generation["task_2a_routing"]["synthesis"]
    syn_executed = str(generation.get("provider") or "").strip() or None
    syn_bounded = generation.get("adapter_invocation_mode") is not None
    syn_dev_note = None
    if syn_executed and syn_decision.selected_adapter_name:
        if _norm_wr_adapter(syn_executed) != _norm_wr_adapter(syn_decision.selected_adapter_name):
            syn_dev_note = str(generation.get("raw_fallback_reason") or "executed_adapter_differs_from_routed")
    attach_stage_routing_evidence(
        syn_stage,
        synthesis_req,
        executed_adapter_name=syn_executed,
        bounded_model_call=syn_bounded,
        skip_reason=None,
        execution_deviation_note=syn_dev_note,
    )
