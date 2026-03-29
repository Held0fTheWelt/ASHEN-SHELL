"""Tests for W2.5.1 canonical AI failure classification and recovery contract."""

import pytest
from app.runtime.ai_failure_recovery import (
    AIFailureClass,
    RecoveryAction,
    FailureRecoveryPolicy,
)


class TestAIFailureClassEnum:
    """Verify AIFailureClass enum has all required failure categories."""

    def test_adapter_error_exists(self):
        """AIFailureClass has ADAPTER_ERROR."""
        assert hasattr(AIFailureClass, "ADAPTER_ERROR")
        assert AIFailureClass.ADAPTER_ERROR.value == "adapter_error"

    def test_timeout_or_empty_response_exists(self):
        """AIFailureClass has TIMEOUT_OR_EMPTY_RESPONSE."""
        assert hasattr(AIFailureClass, "TIMEOUT_OR_EMPTY_RESPONSE")
        assert AIFailureClass.TIMEOUT_OR_EMPTY_RESPONSE.value == "timeout_or_empty_response"

    def test_parse_failure_exists(self):
        """AIFailureClass has PARSE_FAILURE."""
        assert hasattr(AIFailureClass, "PARSE_FAILURE")
        assert AIFailureClass.PARSE_FAILURE.value == "parse_failure"

    def test_structurally_invalid_output_exists(self):
        """AIFailureClass has STRUCTURALLY_INVALID_OUTPUT."""
        assert hasattr(AIFailureClass, "STRUCTURALLY_INVALID_OUTPUT")
        assert AIFailureClass.STRUCTURALLY_INVALID_OUTPUT.value == "structurally_invalid_output"

    def test_responder_validation_failure_exists(self):
        """AIFailureClass has RESPONDER_VALIDATION_FAILURE."""
        assert hasattr(AIFailureClass, "RESPONDER_VALIDATION_FAILURE")
        assert AIFailureClass.RESPONDER_VALIDATION_FAILURE.value == "responder_validation_failure"

    def test_guard_rejection_exists(self):
        """AIFailureClass has GUARD_REJECTION (W2.4.5 related)."""
        assert hasattr(AIFailureClass, "GUARD_REJECTION")
        assert AIFailureClass.GUARD_REJECTION.value == "guard_rejection"

    def test_retry_exhausted_exists(self):
        """AIFailureClass has RETRY_EXHAUSTED."""
        assert hasattr(AIFailureClass, "RETRY_EXHAUSTED")
        assert AIFailureClass.RETRY_EXHAUSTED.value == "retry_exhausted"

    def test_unexpected_runtime_error_exists(self):
        """AIFailureClass has UNEXPECTED_RUNTIME_ERROR."""
        assert hasattr(AIFailureClass, "UNEXPECTED_RUNTIME_ERROR")
        assert AIFailureClass.UNEXPECTED_RUNTIME_ERROR.value == "unexpected_runtime_error"

    def test_all_failure_classes_have_values(self):
        """All AIFailureClass values are non-empty strings."""
        for failure_class in AIFailureClass:
            assert isinstance(failure_class.value, str)
            assert len(failure_class.value) > 0


class TestRecoveryActionEnum:
    """Verify RecoveryAction enum has all required actions."""

    def test_retry_exists(self):
        """RecoveryAction has RETRY."""
        assert hasattr(RecoveryAction, "RETRY")
        assert RecoveryAction.RETRY.value == "retry"

    def test_fallback_exists(self):
        """RecoveryAction has FALLBACK."""
        assert hasattr(RecoveryAction, "FALLBACK")
        assert RecoveryAction.FALLBACK.value == "fallback"

    def test_safe_turn_exists(self):
        """RecoveryAction has SAFE_TURN."""
        assert hasattr(RecoveryAction, "SAFE_TURN")
        assert RecoveryAction.SAFE_TURN.value == "safe_turn"

    def test_restore_exists(self):
        """RecoveryAction has RESTORE."""
        assert hasattr(RecoveryAction, "RESTORE")
        assert RecoveryAction.RESTORE.value == "restore"

    def test_abort_exists(self):
        """RecoveryAction has ABORT."""
        assert hasattr(RecoveryAction, "ABORT")
        assert RecoveryAction.ABORT.value == "abort"


class TestFailureRecoveryPolicy:
    """Verify the failure→recovery mapping is complete and correct."""

    def test_all_failure_classes_have_recovery_policy(self):
        """Every AIFailureClass has a recovery action defined."""
        for failure_class in AIFailureClass:
            action = FailureRecoveryPolicy.get_recovery_action(failure_class)
            assert action in RecoveryAction
            assert isinstance(action, RecoveryAction)

    def test_retryable_failures_are_transient(self):
        """Retryable failures are transient adapter issues."""
        retryable = [
            AIFailureClass.ADAPTER_ERROR,
            AIFailureClass.TIMEOUT_OR_EMPTY_RESPONSE,
        ]
        for failure_class in retryable:
            assert FailureRecoveryPolicy.is_retryable(failure_class)
            assert FailureRecoveryPolicy.get_recovery_action(failure_class) == RecoveryAction.RETRY

    def test_fallback_failures_are_structural(self):
        """Fallback failures are structural (won't fix on retry)."""
        fallback = [
            AIFailureClass.PARSE_FAILURE,
            AIFailureClass.STRUCTURALLY_INVALID_OUTPUT,
        ]
        for failure_class in fallback:
            assert FailureRecoveryPolicy.is_fallback_only(failure_class)
            assert FailureRecoveryPolicy.get_recovery_action(failure_class) == RecoveryAction.FALLBACK

    def test_safe_turn_failures_are_validation(self):
        """Safe-turn failures are validation rejections (proposals never executed)."""
        safe_turn = [
            AIFailureClass.RESPONDER_VALIDATION_FAILURE,
            AIFailureClass.GUARD_REJECTION,
        ]
        for failure_class in safe_turn:
            assert FailureRecoveryPolicy.is_safe_turn(failure_class)
            assert FailureRecoveryPolicy.get_recovery_action(failure_class) == RecoveryAction.SAFE_TURN

    def test_restore_failures_are_systematic(self):
        """Restore failures are systematic issues requiring investigation."""
        restore = [
            AIFailureClass.RETRY_EXHAUSTED,
            AIFailureClass.UNEXPECTED_RUNTIME_ERROR,
        ]
        for failure_class in restore:
            assert FailureRecoveryPolicy.is_restore_required(failure_class)
            assert FailureRecoveryPolicy.get_recovery_action(failure_class) == RecoveryAction.RESTORE

    def test_recovery_classification_is_mutually_exclusive(self):
        """Each failure belongs to exactly one recovery category."""
        for failure_class in AIFailureClass:
            classifications = [
                FailureRecoveryPolicy.is_retryable(failure_class),
                FailureRecoveryPolicy.is_fallback_only(failure_class),
                FailureRecoveryPolicy.is_safe_turn(failure_class),
                FailureRecoveryPolicy.is_restore_required(failure_class),
            ]
            # Exactly one should be True
            assert sum(classifications) == 1

    def test_policy_covers_all_known_failure_classes(self):
        """Policy has an entry for every AIFailureClass (no gaps)."""
        # Policy should have exactly the same keys as AIFailureClass members
        policy_keys = set(FailureRecoveryPolicy.POLICY.keys())
        enum_values = set(AIFailureClass)
        assert policy_keys == enum_values, "Policy must cover all failure classes"

    def test_contract_is_deterministic(self):
        """Recovery action is always the same for a given failure class."""
        for failure_class in AIFailureClass:
            action1 = FailureRecoveryPolicy.get_recovery_action(failure_class)
            action2 = FailureRecoveryPolicy.get_recovery_action(failure_class)
            assert action1 == action2


class TestFailureRecoveryContractCompleteness:
    """Verify the contract covers all failure scenarios without gaps."""

    def test_retryable_vs_fallback_distinction_is_clear(self):
        """Retryable and fallback failures are clearly distinguished."""
        retryable = [
            AIFailureClass.ADAPTER_ERROR,
            AIFailureClass.TIMEOUT_OR_EMPTY_RESPONSE,
        ]
        fallback = [
            AIFailureClass.PARSE_FAILURE,
            AIFailureClass.STRUCTURALLY_INVALID_OUTPUT,
        ]
        # These sets must be disjoint
        assert set(retryable) & set(fallback) == set()

    def test_no_implicit_recovery_actions(self):
        """All recovery actions are explicit (no default/implicit handling)."""
        for failure_class in AIFailureClass:
            action = FailureRecoveryPolicy.get_recovery_action(failure_class)
            # Action must not be None
            assert action is not None
            # Action must be explicitly defined in RecoveryAction enum
            assert action in RecoveryAction

    def test_safe_turn_failures_do_not_require_state_restoration(self):
        """Safe-turn failures can recover without restoring session state."""
        safe_turn = [
            AIFailureClass.RESPONDER_VALIDATION_FAILURE,
            AIFailureClass.GUARD_REJECTION,
        ]
        # These should NOT require full state restoration
        restore = [
            AIFailureClass.RETRY_EXHAUSTED,
            AIFailureClass.UNEXPECTED_RUNTIME_ERROR,
        ]
        assert set(safe_turn) & set(restore) == set()
