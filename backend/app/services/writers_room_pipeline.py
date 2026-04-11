"""Writers Room retrieval → routing → generation pipeline (internal).

Public API remains in ``writers_room_service``.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from story_runtime_core.adapters import build_default_model_adapters
from app.runtime.model_routing_contracts import AdapterModelSpec
from app.runtime.area2_operator_truth import (
    bounded_traces_from_task_2a_routing,
    enrich_operator_audit_with_area2_truth,
    resolve_routing_bootstrap_enabled,
)
from app.runtime.area2_routing_authority import AUTHORITY_SOURCE_WRITERS_ROOM
from app.runtime.operator_audit import build_bounded_surface_operator_audit
from app.services.writers_room_model_routing import build_writers_room_model_route_specs
from app.contracts.writers_room_artifact_class import (
    GOC_SHARED_SEMANTIC_CONTRACT_VERSION,
    WritersRoomArtifactClass,
    build_writers_room_artifact_record,
)
from ai_stack import (
    build_capability_tool_bridge,
    build_langchain_retriever_bridge,
    build_runtime_retriever,
    build_seed_writers_room_graph,
    create_default_capability_registry,
)
from app.services.writers_room_pipeline_context_preview import _context_fingerprint
from app.services.writers_room_pipeline_manifest import (
    _utc_now,
    _workflow_stage_ids,
    _writers_room_artifact_manifest,
)
from app.services.writers_room_pipeline_generation_stage import (
    _norm_wr_adapter,
    run_writers_room_generation_stage,
)
from app.services.writers_room_pipeline_packaging_stage import run_writers_room_packaging_stage
from app.services.writers_room_pipeline_retrieval_stage import run_writers_room_retrieval_stage


@dataclass
class _WritersRoomWorkflow:
    capability_registry: Any
    model_route_specs: list[AdapterModelSpec]
    adapters: dict[str, Any]
    seed_graph: Any
    langchain_retriever: Any
    review_bundle_tool: Any


_WORKFLOW: _WritersRoomWorkflow | None = None


@dataclass
class WritersRoomStore:
    root: Path

    @classmethod
    def default(cls) -> "WritersRoomStore":
        root = Path(__file__).resolve().parents[2] / "var" / "writers_room"
        return cls(root=root)

    def ensure_dirs(self) -> None:
        (self.root / "reviews").mkdir(parents=True, exist_ok=True)

    def write_review(self, review_id: str, payload: dict[str, Any]) -> Path:
        self.ensure_dirs()
        path = self.root / "reviews" / f"{review_id}.json"
        path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
        return path

    def read_review(self, review_id: str) -> dict[str, Any]:
        path = self.root / "reviews" / f"{review_id}.json"
        return json.loads(path.read_text(encoding="utf-8"))


def _get_workflow() -> _WritersRoomWorkflow:
    global _WORKFLOW
    if _WORKFLOW is not None:
        return _WORKFLOW
    repo_root = Path(__file__).resolve().parents[3]
    retriever, assembler, _corpus = build_runtime_retriever(repo_root)
    capability_registry = create_default_capability_registry(
        retriever=retriever,
        assembler=assembler,
        repo_root=repo_root,
    )
    _WORKFLOW = _WritersRoomWorkflow(
        capability_registry=capability_registry,
        model_route_specs=build_writers_room_model_route_specs(),
        adapters=build_default_model_adapters(),
        seed_graph=build_seed_writers_room_graph(),
        langchain_retriever=build_langchain_retriever_bridge(retriever),
        review_bundle_tool=build_capability_tool_bridge(
            capability_registry=capability_registry,
            capability_name="wos.review_bundle.build",
            mode="writers_room",
            actor="writers_room:tool_bridge",
        ),
    )
    return _WORKFLOW


def _execute_writers_room_workflow_package(
    *,
    workflow: _WritersRoomWorkflow,
    module_id: str,
    focus: str,
    actor_id: str,
    trace_id: str | None,
) -> dict[str, Any]:
    """Run retrieval â†’ generation â†’ packaging â†’ governance tool â†’ LangChain preview.

    Returns workflow fields for persistence (no review_id / review_state / revision_cycles).
    """
    manifest_stages: list[dict[str, Any]] = []
    rv = run_writers_room_retrieval_stage(
        seed_graph=workflow.seed_graph,
        capability_registry=workflow.capability_registry,
        module_id=module_id,
        focus=focus,
        actor_id=actor_id,
        manifest_stages=manifest_stages,
    )
    seed = rv.seed
    context_payload = rv.context_payload
    retrieval_inner = rv.retrieval_inner
    source_rows = rv.source_rows
    early_evidence_paths = rv.early_evidence_paths
    retrieval_trace = rv.retrieval_trace
    evidence_tag = rv.evidence_tag
    retrieval_text = rv.retrieval_text
    ctx_fingerprint = rv.ctx_fingerprint

    generation = run_writers_room_generation_stage(
        adapters=workflow.adapters,
        model_route_specs=workflow.model_route_specs,
        module_id=module_id,
        focus=focus,
        retrieval_text=retrieval_text,
        evidence_tag=evidence_tag,
    ).generation
    _t2a_routing = generation.get("task_2a_routing") if isinstance(generation.get("task_2a_routing"), dict) else {}
    preflight_trace: dict[str, Any] = (
        _t2a_routing["preflight"] if isinstance(_t2a_routing.get("preflight"), dict) else {}
    )

    packaging = run_writers_room_packaging_stage(
        review_bundle_tool=workflow.review_bundle_tool,
        manifest_stages=manifest_stages,
        generation=generation,
        module_id=module_id,
        focus=focus,
        evidence_tag=evidence_tag,
        source_rows=source_rows,
        retrieval_inner=retrieval_inner,
        retrieval_trace=retrieval_trace,
        ctx_fingerprint=ctx_fingerprint,
        preflight_trace=preflight_trace,
        early_evidence_paths=early_evidence_paths,
    )
    issues = packaging.issues
    recommendation_artifacts = packaging.recommendation_artifacts
    review_bundle = packaging.review_bundle
    proposal_package = packaging.proposal_package
    comment_bundle = packaging.comment_bundle
    patch_candidates = packaging.patch_candidates
    variant_candidates = packaging.variant_candidates
    review_summary = packaging.review_summary
    langchain_documents = packaging.langchain_documents
    langchain_preview_paths = packaging.langchain_preview_paths
    evidence_paths = packaging.evidence_paths
    workflow_manifest = {
        "workflow": "writers_room_unified_stack_workflow",
        "stages": manifest_stages,
    }
    workflow_stages = _workflow_stage_ids(manifest_stages)

    capability_audit_rows = workflow.capability_registry.recent_audit(limit=20)
    t2a_routing = generation.get("task_2a_routing") if isinstance(generation.get("task_2a_routing"), dict) else {}
    operator_audit_wr = build_bounded_surface_operator_audit(
        surface="writers_room",
        task_2a_routing=t2a_routing,
        execution_hints={
            "adapter_invocation_mode": generation.get("adapter_invocation_mode"),
            "raw_fallback_reason": generation.get("raw_fallback_reason"),
            "executed_provider": generation.get("provider"),
        },
    )
    _wr_specs = workflow.model_route_specs
    enrich_operator_audit_with_area2_truth(
        operator_audit_wr,
        surface="writers_room",
        authority_source=AUTHORITY_SOURCE_WRITERS_ROOM,
        bootstrap_enabled=resolve_routing_bootstrap_enabled(),
        registry_model_spec_count=len(_wr_specs),
        specs_for_coverage=list(_wr_specs),
        bounded_traces=bounded_traces_from_task_2a_routing(t2a_routing),
    )
    gov_truth = {
        "retrieval_evidence_tier": evidence_tag,
        "model_generation_path": generation.get("adapter_invocation_mode"),
        "capabilities_invoked": [
            row.get("capability_name")
            for row in capability_audit_rows
            if isinstance(row, dict) and isinstance(row.get("capability_name"), str)
        ],
        "langgraph_orchestration_depth": "seed_graph_stub",
        "outputs_are_recommendations_only": True,
    }
    gov_truth.update(
        build_writers_room_artifact_record(
            artifact_id=f"governance_truth_{module_id}_{uuid4().hex[:10]}",
            artifact_class=WritersRoomArtifactClass.analysis_artifact,
            source_module_id=module_id,
            evidence_refs=[p for p in evidence_paths if p][:20],
            proposal_scope="writers_room_operational_governance_snapshot",
            approval_state="pending_review",
        )
    )
    lc_preview = {
        "document_count": len(langchain_documents),
        "sources": [doc.metadata.get("source_path") for doc in langchain_documents],
    }
    lc_preview.update(
        build_writers_room_artifact_record(
            artifact_id=f"langchain_preview_{module_id}_{uuid4().hex[:10]}",
            artifact_class=WritersRoomArtifactClass.analysis_artifact,
            source_module_id=module_id,
            evidence_refs=langchain_preview_paths[:10],
            proposal_scope="langchain_primary_context_preview",
            approval_state="pending_review",
        )
    )
    legacy_notice = {
        **build_writers_room_artifact_record(
            artifact_id="notice_legacy_oracle_route",
            artifact_class=WritersRoomArtifactClass.analysis_artifact,
            source_module_id=module_id,
            evidence_refs=[],
            proposal_scope="deprecation_policy_notice",
            approval_state="not_applicable",
        ),
        "body": "Legacy direct chat is deprecated and no longer canonical.",
    }
    package_out: dict[str, Any] = {
        "canonical_flow": "writers_room_unified_stack_workflow",
        "shared_semantic_contract_version": GOC_SHARED_SEMANTIC_CONTRACT_VERSION,
        "trace_id": trace_id,
        "module_id": module_id,
        "focus": focus,
        "workflow_seed": seed,
        "workflow_manifest": workflow_manifest,
        "workflow_stages": workflow_stages,
        "review_summary": review_summary,
        "retrieval": context_payload.get("retrieval", {}),
        "retrieval_trace": retrieval_trace,
        "issues": issues,
        "recommendation_artifacts": recommendation_artifacts,
        "model_generation": generation,
        "review_bundle": review_bundle,
        "proposal_package": proposal_package,
        "comment_bundle": comment_bundle,
        "patch_candidates": patch_candidates,
        "variant_candidates": variant_candidates,
        "outputs_are_recommendations_only": True,
        "legacy_paths": [legacy_notice],
        "capability_audit": capability_audit_rows,
        "operator_audit": operator_audit_wr,
        "governance_truth": gov_truth,
        "langchain_retriever_preview": lc_preview,
        "stack_components": {
            "retrieval": "wos.context_pack.build",
            "orchestration": "langgraph_seed_writers_room_graph",
            "capabilities": ["wos.context_pack.build", "wos.review_bundle.build"],
            "model_routing": "app.runtime.model_routing.route_model + writers_room_model_route_specs",
            "langchain_integration": {
                "enabled": True,
                "runtime_turn_bridge": "invoke_runtime_adapter_with_langchain",
                "writers_room_generation_bridge": "invoke_writers_room_adapter_with_langchain",
                "retriever_bridge": "build_langchain_retriever_bridge",
                "writers_room_document_preview": "primary_context_pack_sources_to_langchain_documents",
                "tool_bridge": "build_capability_tool_bridge",
            },
        },
    }
    package_out["writers_room_artifact_manifest"] = _writers_room_artifact_manifest(package_out)
    return package_out
