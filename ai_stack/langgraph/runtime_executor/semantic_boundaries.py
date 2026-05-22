"""Semantic boundary registry for the runtime-executor compatibility loader.

DS-010 keeps the public executor facade stable while making the remaining
``SOURCE_LINES`` chunks addressable by responsibility. The registry is data,
not execution logic: ``public.py`` consumes it in order, and tests can assert
the intended boundaries without reaching into the loader.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeExecutorBoundary:
    name: str
    modules: tuple[str, ...]
    description: str


SOURCE_BOUNDARIES: tuple[RuntimeExecutorBoundary, ...] = (
    RuntimeExecutorBoundary(
        name="imports",
        modules=("executor_imports_core", "executor_imports_narrative"),
        description="shared executor dependency surface",
    ),
    RuntimeExecutorBoundary(
        name="semantic_input",
        modules=("semantic_input_translation",),
        description="player input language, semantic translation, and payload parsing",
    ),
    RuntimeExecutorBoundary(
        name="actor_lanes",
        modules=(
            "actor_lane_scope",
            "actor_lane_structured_lines",
            "actor_lane_scene_function",
        ),
        description="actor legality, responder reconciliation, and scene-function checks",
    ),
    RuntimeExecutorBoundary(
        name="runtime_aspect_records",
        modules=(
            "authority_aspect_records",
            "authority_voice_profiles",
            "runtime_dispatch_and_voice_aspects",
            "scene_energy_pacing_aspects",
            "social_pressure_aspect_records",
            "information_disclosure_aspect_records",
            "npc_agency_aspect_records",
        ),
        description="runtime aspect record builders and validation evidence",
    ),
    RuntimeExecutorBoundary(
        name="retrieval",
        modules=(
            "retrieval_actor_keys",
            "retrieval_continuity_query",
            "retrieval_adapter_invocation",
            "relationship_dynamics_context",
        ),
        description="active actor keys, retrieval continuity, adapter calls, and relationship context",
    ),
    RuntimeExecutorBoundary(
        name="npc_projection",
        modules=("reaction_order_governance", "npc_agency_projection"),
        description="reaction-order diagnostics and W5-first NPC projection",
    ),
    RuntimeExecutorBoundary(
        name="dramatic_packet",
        modules=(
            "dramatic_generation_packet_opening",
            "dramatic_generation_packet_context",
            "dramatic_generation_packet_authority",
            "dramatic_generation_packet_payload",
        ),
        description="dramatic generation packet opening, context, authority, and payload assembly",
    ),
    RuntimeExecutorBoundary(
        name="director",
        modules=(
            "director_routing_requirements",
            "director_location_completion",
            "director_w5_location_projection",
        ),
        description="director routing, location completion, and W5 location projection",
    ),
    RuntimeExecutorBoundary(
        name="executor_shell",
        modules=("executor_graph_build", "executor_run_prepare", "executor_run_finish"),
        description="executor dataclass, graph wiring, run preparation, and run completion",
    ),
    RuntimeExecutorBoundary(
        name="input_action_pipeline",
        modules=(
            "executor_translation_adapter",
            "executor_input_interpretation_start",
            "executor_input_interpretation_semantics",
            "executor_input_interpretation_finish",
            "executor_meta_control",
            "executor_retrieval_context",
            "executor_action_resolution_start",
            "executor_action_resolution_commit",
            "executor_realization_capabilities",
        ),
        description="translation, interpretation, meta-control, retrieval, and action resolution",
    ),
    RuntimeExecutorBoundary(
        name="director_pipeline",
        modules=(
            "executor_goc_canonical_content",
            "executor_scene_assessment",
            "executor_director_selection_opening",
            "executor_director_selection_context",
            "executor_director_selection_parameters",
            "executor_director_selection_finish",
        ),
        description="canonical content, scene assessment, and director parameter selection",
    ),
    RuntimeExecutorBoundary(
        name="aspect_derivation",
        modules=(
            "executor_scene_energy_temporal_derivation",
            "executor_social_tonal_relationship_derivation",
            "executor_symbolic_meta_genre_derivation",
            "executor_sensory_improv_info_derivation",
            "executor_irony_expectation_momentum_derivation",
            "executor_context_synthesis_derivation",
        ),
        description="runtime aspect derivation and context synthesis",
    ),
    RuntimeExecutorBoundary(
        name="model_pipeline",
        modules=(
            "executor_model_context_prompt",
            "executor_model_context_retrieval",
            "executor_model_context_validation",
            "executor_model_context_payload",
            "executor_model_routing_invocation",
            "executor_model_fallback",
            "executor_generation_self_correction",
            "executor_generation_normalization",
        ),
        description="model context, routing, fallback, self-correction, and normalization",
    ),
    RuntimeExecutorBoundary(
        name="commit_render",
        modules=(
            "executor_validation_commit",
            "executor_commit_render_start",
            "executor_visible_render",
            "executor_package_output",
        ),
        description="validation, commit, visible render, and output packaging",
    ),
)


def iter_source_module_names() -> tuple[str, ...]:
    """Return source segment module names in compatibility-loader order."""
    return tuple(module for boundary in SOURCE_BOUNDARIES for module in boundary.modules)
