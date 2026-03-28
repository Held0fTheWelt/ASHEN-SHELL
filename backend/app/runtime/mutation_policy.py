"""Field-level mutation permission policy for AI proposals.

Enforces deny-by-default whitelist of mutable story-state fields.
Protects engine-owned, runtime-owned, and internal technical state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class MutationPolicyDecision:
    """Result of evaluating a path against the mutation policy.

    Attributes:
        allowed: Whether the path is allowed to be mutated by AI
        reason_code: Machine-readable reason code if blocked (e.g., "blocked_root_domain")
        reason_message: Human-readable reason message if blocked
    """

    allowed: bool
    reason_code: Optional[str] = None
    reason_message: Optional[str] = None
