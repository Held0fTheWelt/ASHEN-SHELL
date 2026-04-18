from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from fy_platform.ai.contracts import COMMAND_ENVELOPE_SCHEMA_VERSION


@dataclass(frozen=True)
class SuiteRunRecord:
    run_id: str
    suite: str
    mode: str
    started_at: str
    ended_at: str | None
    workspace_root: str
    target_repo_root: str | None
    target_repo_id: str | None
    status: str


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    suite: str
    run_id: str
    kind: str
    source_uri: str
    ownership_zone: str
    content_hash: str
    mime_type: str
    deterministic: bool
    review_state: str
    created_at: str


@dataclass(frozen=True)
class ArtifactRecord:
    artifact_id: str
    suite: str
    run_id: str
    format: str
    role: str
    path: str
    created_at: str


@dataclass(frozen=True)
class EvidenceLink:
    src_id: str
    dst_id: str
    relation: str


@dataclass(frozen=True)
class RetrievalHit:
    chunk_id: str
    suite: str
    score_lexical: float
    score_semantic: float
    score_hybrid: float
    source_path: str
    excerpt: str
    scope: str = ''
    target_repo_id: str | None = None
    score_recency: float = 0.0
    score_scope: float = 0.0
    score_suite_affinity: float = 0.0
    matched_terms: list[str] = field(default_factory=list)
    confidence: str = 'low'
    rationale: str = ''


@dataclass(frozen=True)
class ContextPack:
    pack_id: str
    query: str
    suite_scope: list[str]
    audience: str
    hits: list[RetrievalHit]
    summary: str
    artifact_paths: list[str] = field(default_factory=list)
    related_suites: list[str] = field(default_factory=list)
    evidence_confidence: str = 'low'
    priorities: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    uncertainty: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ModelRouteDecision:
    task_type: str
    selected_tier: str
    selected_model: str
    reason: str
    budget_class: str
    fallback_chain: list[str]
    reproducibility_mode: str = 'stable'
    safety_mode: str = 'advisory'
    estimated_cost_class: str = 'cheap'


@dataclass(frozen=True)
class CompareRunsDelta:
    left_run_id: str
    right_run_id: str
    left_status: str
    right_status: str
    artifact_delta: int
    added_roles: list[str]
    removed_roles: list[str]
    left_artifact_count: int = 0
    right_artifact_count: int = 0
    left_evidence_count: int = 0
    right_evidence_count: int = 0
    left_review_state_counts: dict[str, int] = field(default_factory=dict)
    right_review_state_counts: dict[str, int] = field(default_factory=dict)
    left_journal_event_count: int = 0
    right_journal_event_count: int = 0
    left_duration_seconds: float | None = None
    right_duration_seconds: float | None = None
    mode_changed: bool = False
    target_repo_changed: bool = False
    target_repo_id_changed: bool = False
    added_formats: list[str] = field(default_factory=list)
    removed_formats: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CommandEnvelope:
    ok: bool
    suite: str
    command: str
    payload: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    recovery_hints: list[str] = field(default_factory=list)
    error_code: str = ''
    exit_code: int = 0
    timestamp: str = ''
    schema_version: str = COMMAND_ENVELOPE_SCHEMA_VERSION
    contract_version: str = '1.0'
    compatibility_mode: str = 'autark-outbound'


@dataclass(frozen=True)
class ReviewTransitionResult:
    ok: bool
    current_state: str
    new_state: str
    reason: str


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {k: to_jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, list):
        return [to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    return value
