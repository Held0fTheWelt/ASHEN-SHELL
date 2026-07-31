"""Apply mutation policy + source gate to proposed deltas (Wave 4 production path)."""

from __future__ import annotations

from typing import Iterable

from app.story_runtime.mutation_policy import DEFAULT_MUTATION_POLICY, MutationPolicy
from app.story_runtime.source_gate import evaluate_source_gate
from app.story_runtime.state_deltas import DeltaPartition, StateDelta, partition_deltas


def evaluate_proposed_deltas(
    candidates: Iterable[StateDelta],
    *,
    mutation_policy: MutationPolicy | None = None,
    source_gate_enabled: bool = True,
) -> DeltaPartition:
    """Run source gate then mutation policy; return accepted/rejected partition.

    Permissive default: paths are allowed unless forbidden (E9).
    """
    deltas = list(candidates)
    if source_gate_enabled:
        gate = evaluate_source_gate(deltas)
        if not gate.allowed:
            return partition_deltas(
                candidates=deltas,
                accept=[False] * len(deltas),
            )
    policy = mutation_policy or DEFAULT_MUTATION_POLICY
    flags = [policy.evaluate(d.target_path).allowed for d in deltas]
    return partition_deltas(candidates=deltas, accept=flags)
