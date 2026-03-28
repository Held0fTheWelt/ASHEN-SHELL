import pytest
from app.runtime.mutation_policy import MutationPolicyDecision, MutationPolicy

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


class TestMutationPolicyStructure:
    """Test the policy structure and domain definitions."""

    def test_allowed_domains_defined(self):
        """Allowed domains are explicitly defined."""
        assert hasattr(MutationPolicy, 'ALLOWED_DOMAINS')
        assert MutationPolicy.ALLOWED_DOMAINS == {
            "characters", "relationships", "scene_state", "conflict_state"
        }

    def test_protected_domains_defined(self):
        """Protected domains are explicitly defined."""
        assert hasattr(MutationPolicy, 'PROTECTED_DOMAINS')
        assert MutationPolicy.PROTECTED_DOMAINS == {
            "metadata", "runtime", "system", "logs", "decision", "session", "turn", "cache"
        }

    def test_whitelist_patterns_defined(self):
        """Whitelist patterns are defined for allowed domains."""
        assert hasattr(MutationPolicy, 'WHITELIST_PATTERNS')
        assert len(MutationPolicy.WHITELIST_PATTERNS) == 8
        assert "characters.*.emotional_state" in MutationPolicy.WHITELIST_PATTERNS
        assert "conflict_state.escalation" in MutationPolicy.WHITELIST_PATTERNS

    def test_blocked_patterns_defined(self):
        """Blocked patterns prevent mutations of protected/technical fields."""
        assert hasattr(MutationPolicy, 'BLOCKED_PATTERNS')
        assert len(MutationPolicy.BLOCKED_PATTERNS) > 0
        assert "session.*" in MutationPolicy.BLOCKED_PATTERNS
        assert "*._*" in MutationPolicy.BLOCKED_PATTERNS


class TestMutationPolicyEvaluation:
    """Test the core policy evaluation logic."""

    def test_whitelisted_character_emotional_state_allowed(self):
        """characters.*.emotional_state is whitelisted."""
        decision = MutationPolicy.evaluate("characters.veronique.emotional_state")
        assert decision.allowed is True
        assert decision.reason_code is None

    def test_whitelisted_relationship_value_allowed(self):
        """relationships.*.value is whitelisted."""
        decision = MutationPolicy.evaluate("relationships.veronique_alain.value")
        assert decision.allowed is True

    def test_whitelisted_conflict_escalation_allowed(self):
        """conflict_state.escalation (global) is whitelisted."""
        decision = MutationPolicy.evaluate("conflict_state.escalation")
        assert decision.allowed is True

    def test_blocked_session_domain(self):
        """session.* is blocked."""
        decision = MutationPolicy.evaluate("session.id")
        assert decision.allowed is False
        assert decision.reason_code == "blocked_root_domain"
        assert "session" in decision.reason_message.lower()

    def test_blocked_internal_field(self):
        """*._* pattern blocks internal fields."""
        decision = MutationPolicy.evaluate("characters.veronique._cache")
        assert decision.allowed is False
        assert decision.reason_code == "blocked_internal_field"

    def test_valid_path_but_blocked_mutation(self):
        """Path exists but mutation is blocked (valid path ≠ allowed mutation)."""
        # characters is allowed domain, but secret_backstory is not whitelisted
        decision = MutationPolicy.evaluate("characters.veronique.secret_backstory")
        assert decision.allowed is False
        assert decision.reason_code == "not_whitelisted"

    def test_unknown_root_denied_by_default(self):
        """Unknown root domain denied by default."""
        decision = MutationPolicy.evaluate("unknown_domain.field")
        assert decision.allowed is False
        assert decision.reason_code == "out_of_scope_root"

    def test_conflict_state_nested_rejected(self):
        """conflict_state is global, not per-scene (conflict_state.kitchen.escalation rejected)."""
        decision = MutationPolicy.evaluate("conflict_state.kitchen.escalation")
        assert decision.allowed is False
        # Either blocked by pattern mismatch or not whitelisted
        assert decision.reason_code in ["not_whitelisted", "blocked_root_domain"]
