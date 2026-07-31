"""Permissive mutation policy for AI / player proposed state paths (Wave 4 / E9).

Default stance: allow unless explicitly forbidden. This deliberately differs from
the dormant backend ``MutationPolicy`` (deny-by-default whitelist), which must
not be copied into live authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MutationPolicyDecision:
    allowed: bool
    reason_code: str | None = None
    reason_message: str | None = None


@dataclass
class MutationPolicy:
    """Allow-by-default policy with an explicit forbid list.

    Switch: ``capability_mutation_policy`` (default on). When the capability is
    off, callers should skip evaluation and treat all paths as allowed.
    """

    # Always forbidden — identity / bookkeeping, never AI-writable.
    forbidden_roots: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "session_id",
                "module_id",
                "revision",
                "runtime",
                "system",
                "metadata",
                "logs",
                "cache",
                "turn.session_id",
            }
        )
    )
    # Extra deny patterns (component match with '*'). Empty by default (E9).
    deny_patterns: tuple[str, ...] = ()

    def evaluate(self, target_path: str) -> MutationPolicyDecision:
        path = str(target_path or "").strip()
        if not path:
            return MutationPolicyDecision(
                allowed=False,
                reason_code="empty_path",
                reason_message="Mutation path is required.",
            )
        root = path.split(".", 1)[0]
        if root in self.forbidden_roots or path in self.forbidden_roots:
            return MutationPolicyDecision(
                allowed=False,
                reason_code="forbidden_root",
                reason_message=f"Path {path!r} is under a forbidden root.",
            )
        for pattern in self.deny_patterns:
            if _pattern_matches(pattern, path):
                return MutationPolicyDecision(
                    allowed=False,
                    reason_code="deny_pattern",
                    reason_message=f"Path {path!r} matched deny pattern {pattern!r}.",
                )
        return MutationPolicyDecision(allowed=True)


def _pattern_matches(pattern: str, path: str) -> bool:
    p_parts = pattern.split(".")
    path_parts = path.split(".")
    if len(p_parts) != len(path_parts):
        return False
    for pp, tp in zip(p_parts, path_parts, strict=True):
        if pp != "*" and pp != tp:
            return False
    return True


DEFAULT_MUTATION_POLICY = MutationPolicy()
