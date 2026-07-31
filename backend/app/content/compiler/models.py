from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SourceProvenance(BaseModel):
    """Where an authored runtime fact came from (Wave 7 / DRIFT-004)."""

    module_id: str
    module_version: str
    source_path: str
    content_kind: str


class AuthoredFact(BaseModel):
    """One runtime-facing fact with mandatory provenance."""

    fact_id: str
    content_version: str
    value: Any = None
    source_provenance: SourceProvenance


class RuntimeProjection(BaseModel):
    compiler_version: str = "m1.v1"
    module_id: str
    module_version: str
    start_scene_id: str
    scenes: list[dict[str, Any]] = Field(default_factory=list)
    triggers: list[dict[str, Any]] = Field(default_factory=list)
    endings: list[dict[str, Any]] = Field(default_factory=list)
    relationship_axes: list[dict[str, Any]] = Field(default_factory=list)
    relationships: list[dict[str, Any]] = Field(default_factory=list)
    escalation_axes: dict[str, Any] = Field(default_factory=dict)
    opening_scene_sequence: dict[str, Any] = Field(default_factory=dict)
    opening_quote_anchors: dict[str, Any] = Field(default_factory=dict)
    hard_forbidden_rules: dict[str, Any] = Field(default_factory=dict)
    canonical_path: dict[str, Any] = Field(default_factory=dict)
    modularity_policy: dict[str, Any] = Field(default_factory=dict)
    scene_graph: dict[str, Any] = Field(default_factory=dict)
    locations: dict[str, Any] = Field(default_factory=dict)
    objects: dict[str, Any] = Field(default_factory=dict)
    content_access_policy: dict[str, Any] = Field(default_factory=dict)
    character_ids: list[str] = Field(default_factory=list)
    characters: list[dict[str, Any]] = Field(default_factory=list)
    character_documents: dict[str, Any] = Field(default_factory=dict)
    transition_hints: list[dict[str, Any]] = Field(default_factory=list)


class RetrievalChunk(BaseModel):
    chunk_id: str
    kind: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalCorpusSeed(BaseModel):
    compiler_version: str = "m1.v1"
    module_id: str
    module_version: str
    chunks: list[RetrievalChunk] = Field(default_factory=list)


class ReviewExportSeed(BaseModel):
    compiler_version: str = "m1.v1"
    module_id: str
    module_version: str
    # Optional stamp for human review exports; omit/null for deterministic compile digests.
    generated_at: datetime | None = None
    summary: dict[str, Any] = Field(default_factory=dict)
    scenes: list[dict[str, Any]] = Field(default_factory=list)
    triggers: list[dict[str, Any]] = Field(default_factory=list)
    endings: list[dict[str, Any]] = Field(default_factory=list)


class CanonicalCompileOutput(BaseModel):
    canonical_model: str = "content_module.scene_trigger_ending.v1"
    content_version: str
    runtime_projection: RuntimeProjection
    retrieval_corpus_seed: RetrievalCorpusSeed
    review_export_seed: ReviewExportSeed
    authored_facts: list[AuthoredFact] = Field(default_factory=list)
