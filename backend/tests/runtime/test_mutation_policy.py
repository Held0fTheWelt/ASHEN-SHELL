import pytest
from app.runtime.mutation_policy import MutationPolicyDecision

def test_mutation_policy_decision_allowed():
    """MutationPolicyDecision represents allowed mutation."""
    decision = MutationPolicyDecision(allowed=True)
    assert decision.allowed is True
    assert decision.reason_code is None
    assert decision.reason_message is None

def test_mutation_policy_decision_blocked():
    """MutationPolicyDecision represents blocked mutation."""
    decision = MutationPolicyDecision(
        allowed=False,
        reason_code="blocked_root_domain",
        reason_message="Protected domain: session"
    )
    assert decision.allowed is False
    assert decision.reason_code == "blocked_root_domain"
    assert decision.reason_message == "Protected domain: session"
