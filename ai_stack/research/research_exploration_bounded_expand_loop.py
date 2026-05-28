"""Bounded exploration BFS expand phase — DS-048."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from ai_stack.contracts.research_contract import (
    ExplorationAbortReason,
    ExplorationBudget,
    ExplorationEdgeRecord,
    ExplorationNodeRecord,
    ExplorationOutcome,
    ExplorationRelationType,
    Perspective,
    ResearchStatus,
)
from ai_stack.research.research_exploration_bounded_primitives import (
    RELATION_ORDER,
    branch_hypothesis,
    candidate_eligible,
    deterministic_edge_id,
    deterministic_node_id,
    novelty_score,
    normalize_text,
    speculative_level_for_relation,
)


@dataclass
class _ExplorationExpandCounters:
    """``_ExplorationExpandCounters`` groups related behaviour; callers should read members for contracts and threading assumptions.
    """
    llm_calls: int = 0
    token_use: int = 0
    branch_count: int = 0
    low_evidence_expansions: int = 0
    rejected_count: int = 0
    unresolved_count: int = 0
    pruned_count: int = 0
    promoted_count: int = 0


_TERMINAL_ABORTS = frozenset(
    {
        ExplorationAbortReason.REDUNDANCY_ABORT.value,
        ExplorationAbortReason.SPECULATIVE_DRIFT_ABORT.value,
        ExplorationAbortReason.LLM_BUDGET_EXHAUSTED.value,
        ExplorationAbortReason.TOKEN_BUDGET_EXHAUSTED.value,
        ExplorationAbortReason.NODE_BUDGET_EXHAUSTED.value,
        ExplorationAbortReason.TIME_BUDGET_EXHAUSTED.value,
        ExplorationAbortReason.LOW_EVIDENCE_LIMIT_REACHED.value,
    }
)


def _budget_abort_reason(
    *,
    budget: ExplorationBudget,
    start: float,
    nodes: list[dict[str, Any]],
    counters: _ExplorationExpandCounters,
) -> str | None:
    if int((time.time() - start) * 1000) >= budget.time_budget_ms:
        return ExplorationAbortReason.TIME_BUDGET_EXHAUSTED.value
    if len(nodes) >= budget.max_total_nodes:
        return ExplorationAbortReason.NODE_BUDGET_EXHAUSTED.value
    if counters.llm_calls >= budget.llm_call_budget:
        return ExplorationAbortReason.LLM_BUDGET_EXHAUSTED.value
    if counters.token_use >= budget.token_budget:
        return ExplorationAbortReason.TOKEN_BUDGET_EXHAUSTED.value
    return None


def _child_evidence_ids(
    *,
    current: dict[str, Any],
    relation: ExplorationRelationType,
) -> list[str]:
    evidence_ids = list(current.get("evidence_anchor_ids", []))
    if relation in (ExplorationRelationType.CONTRAST, ExplorationRelationType.COUNTERREAD):
        return evidence_ids[:1]
    return evidence_ids


def _record_low_evidence_abort(
    *,
    evidence_ids: list[str],
    budget: ExplorationBudget,
    counters: _ExplorationExpandCounters,
) -> str | None:
    if evidence_ids:
        return None
    counters.low_evidence_expansions += 1
    if counters.low_evidence_expansions > budget.max_low_evidence_expansions:
        return ExplorationAbortReason.LOW_EVIDENCE_LIMIT_REACHED.value
    return None


def _exploration_outcome(
    *,
    novelty: float,
    counters: _ExplorationExpandCounters,
) -> ExplorationOutcome:
    if novelty < 0.18:
        counters.rejected_count += 1
        return ExplorationOutcome.REJECTED
    if novelty < 0.24:
        counters.unresolved_count += 1
        return ExplorationOutcome.UNRESOLVED
    return ExplorationOutcome.KEPT_FOR_VALIDATION


def _exploration_child_records(
    *,
    current: dict[str, Any],
    relation: ExplorationRelationType,
    depth: int,
    used_child: int,
    child_hypothesis: str,
    speculative_level: float,
    evidence_ids: list[str],
    outcome: ExplorationOutcome,
) -> tuple[dict[str, Any], dict[str, Any]]:
    child_id = deterministic_node_id(current["node_id"], relation, depth + 1, used_child)
    child = ExplorationNodeRecord(
        node_id=child_id,
        parent_node_id=current["node_id"],
        seed_aspect_id=str(current.get("seed_aspect_id", "")),
        perspective=Perspective(str(current.get("perspective", Perspective.PLAYWRIGHT.value))),
        hypothesis=child_hypothesis,
        rationale=f"derived_via:{relation.value}",
        speculative_level=speculative_level,
        evidence_anchor_ids=evidence_ids,
        novelty_score=novelty_score(child_hypothesis),
        status=ResearchStatus.EXPLORATORY,
        outcome=outcome,
    ).to_dict()
    edge = ExplorationEdgeRecord(
        edge_id=deterministic_edge_id(current["node_id"], child_id, relation),
        from_node_id=current["node_id"],
        to_node_id=child_id,
        relation_type=relation,
    ).to_dict()
    return child, edge


def _append_exploration_child(
    *,
    child: dict[str, Any],
    edge: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    seen_hypothesis: set[str],
    normalized: str,
    counters: _ExplorationExpandCounters,
    queue: deque[tuple[dict[str, Any], int]],
    depth: int,
    outcome: ExplorationOutcome,
) -> None:
    nodes.append(child)
    edges.append(edge)
    seen_hypothesis.add(normalized)
    if outcome == ExplorationOutcome.KEPT_FOR_VALIDATION:
        queue.append((child, depth + 1))
        if candidate_eligible(child):
            counters.promoted_count += 1


def run_bounded_exploration_expand_loop(
    *,
    budget: ExplorationBudget,
    start: float,
    queue: deque[tuple[dict[str, Any], int]],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    seen_hypothesis: set[str],
    counters: _ExplorationExpandCounters,
    abort_reason: str,
) -> str:
    """Expand queued research hypotheses breadth-first until a budget gate stops."""
    ar = abort_reason
    while queue:
        current, depth = queue.popleft()
        ar = _budget_abort_reason(
            budget=budget,
            start=start,
            nodes=nodes,
            counters=counters,
        ) or ar
        if ar in _TERMINAL_ABORTS:
            break
        if depth >= budget.max_depth:
            if ar == ExplorationAbortReason.COMPLETED_WITHIN_BUDGET.value:
                ar = ExplorationAbortReason.DEPTH_LIMIT_REACHED.value
            continue

        child_budget = min(budget.max_branches_per_node, len(RELATION_ORDER))
        used_child = 0
        for relation in RELATION_ORDER:
            if used_child >= child_budget:
                if ar == ExplorationAbortReason.COMPLETED_WITHIN_BUDGET.value:
                    ar = ExplorationAbortReason.BRANCH_BUDGET_EXHAUSTED.value
                break
            ar = _budget_abort_reason(
                budget=budget,
                start=start,
                nodes=nodes,
                counters=counters,
            ) or ar
            if ar in _TERMINAL_ABORTS:
                break

            parent_hyp = str(current.get("hypothesis", ""))
            child_hyp = branch_hypothesis(parent_hyp, relation)
            normalized = normalize_text(child_hyp)
            if normalized in seen_hypothesis:
                counters.pruned_count += 1
                if budget.abort_on_redundancy:
                    ar = ExplorationAbortReason.REDUNDANCY_ABORT.value
                    break
                continue

            speculative_level = speculative_level_for_relation(relation, depth + 1)
            if budget.abort_on_speculative_drift and speculative_level >= 0.9:
                counters.pruned_count += 1
                ar = ExplorationAbortReason.SPECULATIVE_DRIFT_ABORT.value
                break

            evidence_ids = _child_evidence_ids(current=current, relation=relation)
            ar = _record_low_evidence_abort(
                evidence_ids=evidence_ids,
                budget=budget,
                counters=counters,
            ) or ar
            if ar in _TERMINAL_ABORTS:
                break

            counters.llm_calls += 1
            counters.token_use += max(10, len(child_hyp.split()))
            counters.branch_count += 1
            novelty = novelty_score(child_hyp)
            outcome = _exploration_outcome(novelty=novelty, counters=counters)
            child, edge = _exploration_child_records(
                current=current,
                relation=relation,
                depth=depth,
                used_child=used_child,
                child_hypothesis=child_hyp,
                speculative_level=speculative_level,
                evidence_ids=evidence_ids,
                outcome=outcome,
            )
            used_child += 1
            _append_exploration_child(
                child=child,
                edge=edge,
                nodes=nodes,
                edges=edges,
                seen_hypothesis=seen_hypothesis,
                normalized=normalized,
                counters=counters,
                queue=queue,
                depth=depth,
                outcome=outcome,
            )

        if ar in _TERMINAL_ABORTS:
            break

    return ar


def exploration_expand_counters_factory() -> _ExplorationExpandCounters:
    """Describe what ``exploration_expand_counters_factory`` does in one
    line (verb-led summary for this function).
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Returns:
        _ExplorationExpandCounters:
            Returns a value of type ``_ExplorationExpandCounters``; see the function body for structure, error paths, and sentinels.
    """
    return _ExplorationExpandCounters()
