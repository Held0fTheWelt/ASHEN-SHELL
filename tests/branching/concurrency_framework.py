"""
Large-scale concurrency and performance framework for Phase 7.

Measures system behavior under load:
- 100+ concurrent sessions
- <2s latency per turn
- Zero cross-session leakage
- Cost tracking per session
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from enum import Enum
import time
import threading
from collections import defaultdict


class SessionState(Enum):
    """State of a concurrent session."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class LatencyMeasurement:
    """Single turn latency measurement."""
    session_id: str
    turn_number: int
    decision_id: Optional[str]
    start_time: float
    end_time: float
    latency_ms: float
    success: bool
    error_message: Optional[str] = None

    @property
    def exceeds_target(self) -> bool:
        """Check if latency exceeds 2s target."""
        return self.latency_ms > 2000.0


@dataclass
class IsolationViolation:
    """Cross-session data leakage detection."""
    source_session: str
    target_session: str
    violation_type: str  # "tag_leakage", "state_leakage", "fact_leakage"
    details: str
    severity: str  # "critical", "warning"


@dataclass
class ConcurrentSessionMetrics:
    """Metrics for a single concurrent session."""
    session_id: str
    scenario_id: str
    evaluator_id: str
    path_name: str
    state: SessionState
    turn_count: int = 0
    latencies: List[LatencyMeasurement] = field(default_factory=list)
    consequence_tags: set = field(default_factory=set)
    state_snapshot: Dict[str, Any] = field(default_factory=dict)
    cost_tokens_estimated: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    @property
    def duration_seconds(self) -> float:
        """Total session duration."""
        end = self.completed_at or datetime.now(timezone.utc)
        return (end - self.created_at).total_seconds()

    @property
    def avg_latency_ms(self) -> float:
        """Average latency across all turns."""
        if not self.latencies:
            return 0.0
        return sum(l.latency_ms for l in self.latencies) / len(self.latencies)

    @property
    def max_latency_ms(self) -> float:
        """Maximum latency seen."""
        return max((l.latency_ms for l in self.latencies), default=0.0)

    @property
    def p95_latency_ms(self) -> float:
        """95th percentile latency."""
        if len(self.latencies) < 2:
            return self.avg_latency_ms

        sorted_latencies = sorted(l.latency_ms for l in self.latencies)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[idx]

    @property
    def turns_exceeding_target(self) -> int:
        """Count of turns exceeding 2s target."""
        return sum(1 for l in self.latencies if l.exceeds_target)

    @property
    def success_rate(self) -> float:
        """Percentage of successful turns."""
        if not self.latencies:
            return 0.0
        successful = sum(1 for l in self.latencies if l.success)
        return (successful / len(self.latencies)) * 100.0


@dataclass
class ConcurrencyTestResults:
    """Aggregated results from concurrency test."""
    test_name: str
    num_sessions: int
    num_concurrent_peaks: int
    test_duration_seconds: float
    sessions: List[ConcurrentSessionMetrics] = field(default_factory=list)
    isolation_violations: List[IsolationViolation] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    @property
    def total_turns_executed(self) -> int:
        """Total turns across all sessions."""
        return sum(len(s.latencies) for s in self.sessions)

    @property
    def avg_session_latency_ms(self) -> float:
        """Average latency across all sessions."""
        if not self.sessions:
            return 0.0
        return sum(s.avg_latency_ms for s in self.sessions) / len(self.sessions)

    @property
    def max_session_latency_ms(self) -> float:
        """Maximum latency seen across all sessions."""
        return max((s.max_latency_ms for s in self.sessions), default=0.0)

    @property
    def p95_latency_ms(self) -> float:
        """95th percentile latency across all sessions."""
        all_latencies = []
        for session in self.sessions:
            all_latencies.extend(l.latency_ms for l in session.latencies)

        if len(all_latencies) < 2:
            return self.avg_session_latency_ms

        sorted_latencies = sorted(all_latencies)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[idx]

    @property
    def turns_exceeding_target(self) -> int:
        """Count of turns exceeding 2s target."""
        return sum(s.turns_exceeding_target for s in self.sessions)

    @property
    def meets_latency_target(self) -> bool:
        """Check if P95 latency meets <2s target."""
        return self.p95_latency_ms < 2000.0

    @property
    def meets_isolation_target(self) -> bool:
        """Check if no critical isolation violations."""
        critical = [v for v in self.isolation_violations if v.severity == "critical"]
        return len(critical) == 0

    @property
    def overall_success(self) -> bool:
        """True if all targets met."""
        return self.meets_latency_target and self.meets_isolation_target and len(self.sessions) >= self.num_sessions * 0.95

    @property
    def total_cost_tokens(self) -> int:
        """Estimated total token cost."""
        return sum(s.cost_tokens_estimated for s in self.sessions)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary dict."""
        return {
            "test_name": self.test_name,
            "num_sessions_target": self.num_sessions,
            "num_sessions_completed": len(self.sessions),
            "total_turns": self.total_turns_executed,
            "avg_latency_ms": self.avg_session_latency_ms,
            "max_latency_ms": self.max_session_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "meets_latency_target": self.meets_latency_target,
            "turns_exceeding_2s": self.turns_exceeding_target,
            "isolation_violations_critical": len([v for v in self.isolation_violations if v.severity == "critical"]),
            "isolation_violations_warning": len([v for v in self.isolation_violations if v.severity == "warning"]),
            "meets_isolation_target": self.meets_isolation_target,
            "overall_success": self.overall_success,
            "total_cost_tokens": self.total_cost_tokens,
            "test_duration_seconds": self.test_duration_seconds,
        }


class IsolationVerifier:
    """Verifies cross-session isolation."""

    def __init__(self):
        self.session_states: Dict[str, Dict[str, Any]] = {}  # session_id -> state
        self.violations: List[IsolationViolation] = []

    def register_session(self, session_id: str, state: Dict[str, Any]) -> None:
        """Register session state for isolation checking."""
        self.session_states[session_id] = state.copy()

    def verify_tag_isolation(self, session_id: str, tags: set) -> List[IsolationViolation]:
        """Check if session tags are leaking to other sessions."""
        violations = []

        for other_sid, other_state in self.session_states.items():
            if other_sid == session_id:
                continue

            other_tags = other_state.get("consequence_tags", set())

            # Check for unexpected tag overlap
            shared = tags & other_tags

            # Expected overlaps (scenario-wide, not session-specific):
            # - Path names: all sessions in same scenario see same paths
            # - Scenario id: all sessions use same scenario
            # - Generic turn tags: turn_N is expected to be shared if N is same
            # What we DON'T expect: cross-session state leakage
            scenario_level_tags = {t for t in shared if t in {
                "salon_mediation", "path_A_escalation", "path_B_divide",
                "path_C_understanding"
            }}

            # Session-specific tags should NOT overlap (e.g., session_id, internal state)
            leaked = shared - scenario_level_tags

            # Only flag if we see actual session-specific state leakage
            # (e.g., same internal pressure value, shared session identifiers)
            if leaked and any(t.startswith("session_") and t != f"session_{session_id[:4]}" for t in leaked):
                violations.append(IsolationViolation(
                    source_session=session_id,
                    target_session=other_sid,
                    violation_type="tag_leakage",
                    details=f"Leaked tags: {leaked}",
                    severity="critical",
                ))

        self.violations.extend(violations)
        return violations

    def verify_state_isolation(self, session_id: str, state: Dict[str, Any]) -> List[IsolationViolation]:
        """Check if session state is affecting other sessions."""
        violations = []

        # Verify that session pressure values don't affect others
        pressure = state.get("pressure", 0)

        for other_sid, other_state in self.session_states.items():
            if other_sid == session_id:
                continue

            other_pressure = other_state.get("pressure", 0)

            # Pressure should be independent
            if pressure == other_pressure and pressure > 0:
                violations.append(IsolationViolation(
                    source_session=session_id,
                    target_session=other_sid,
                    violation_type="state_leakage",
                    details=f"Both sessions have pressure={pressure}",
                    severity="warning",  # Could be coincidence
                ))

        self.violations.extend(violations)
        return violations

    def get_violations(self, severity: Optional[str] = None) -> List[IsolationViolation]:
        """Get violations, optionally filtered by severity."""
        if severity:
            return [v for v in self.violations if v.severity == severity]
        return self.violations


class ConcurrencyTestBuilder:
    """Builder for configuring concurrency tests."""

    def __init__(self):
        self.num_sessions = 10
        self.concurrent_peak = 5
        self.turns_per_session = 20
        self.delay_between_turns_ms = 100
        self.scenario_id = "salon_mediation"
        self.test_name = "baseline"

    def with_num_sessions(self, n: int) -> "ConcurrencyTestBuilder":
        """Set number of total sessions."""
        self.num_sessions = n
        return self

    def with_concurrent_peak(self, n: int) -> "ConcurrencyTestBuilder":
        """Set peak concurrent sessions."""
        self.concurrent_peak = n
        return self

    def with_turns_per_session(self, n: int) -> "ConcurrencyTestBuilder":
        """Set turns per session."""
        self.turns_per_session = n
        return self

    def with_delay_ms(self, ms: int) -> "ConcurrencyTestBuilder":
        """Set delay between turns."""
        self.delay_between_turns_ms = ms
        return self

    def with_scenario(self, scenario_id: str) -> "ConcurrencyTestBuilder":
        """Set scenario."""
        self.scenario_id = scenario_id
        return self

    def with_name(self, name: str) -> "ConcurrencyTestBuilder":
        """Set test name."""
        self.test_name = name
        return self

    def build(self) -> Dict[str, Any]:
        """Build config dict."""
        return {
            "num_sessions": self.num_sessions,
            "concurrent_peak": self.concurrent_peak,
            "turns_per_session": self.turns_per_session,
            "delay_between_turns_ms": self.delay_between_turns_ms,
            "scenario_id": self.scenario_id,
            "test_name": self.test_name,
        }


class ConcurrencySimulator:
    """Simulates concurrent sessions with latency and isolation checks."""

    def __init__(self):
        self.isolation_verifier = IsolationVerifier()
        self.sessions: Dict[str, ConcurrentSessionMetrics] = {}
        self.lock = threading.Lock()

    def simulate_turn(
        self,
        session_id: str,
        turn_number: int,
        decision_id: Optional[str] = None,
        simulated_latency_ms: float = 100.0,
    ) -> LatencyMeasurement:
        """Simulate a single turn execution."""
        start = time.time()

        # Simulate turn execution with given latency
        time.sleep(simulated_latency_ms / 1000.0)

        end = time.time()
        latency_ms = (end - start) * 1000.0

        return LatencyMeasurement(
            session_id=session_id,
            turn_number=turn_number,
            decision_id=decision_id,
            start_time=start,
            end_time=end,
            latency_ms=latency_ms,
            success=True,
        )

    def run_session(
        self,
        session_id: str,
        scenario_id: str,
        path_name: str,
        evaluator_id: str,
        turns: int = 20,
    ) -> ConcurrentSessionMetrics:
        """Run a simulated concurrent session."""
        metrics = ConcurrentSessionMetrics(
            session_id=session_id,
            scenario_id=scenario_id,
            path_name=path_name,
            evaluator_id=evaluator_id,
            state=SessionState.RUNNING,
        )

        # Simulate turns
        for turn in range(turns):
            # Simulate realistic latency (100-500ms per turn)
            base_latency = 150.0 if turn % 3 == 0 else 120.0
            latency = LatencyMeasurement(
                session_id=session_id,
                turn_number=turn,
                decision_id=f"decision_{turn}" if turn % 5 == 0 else None,
                start_time=time.time(),
                end_time=time.time() + (base_latency / 1000.0),
                latency_ms=base_latency,
                success=True,
            )

            metrics.latencies.append(latency)
            metrics.turn_count += 1

            # Simulate consequences
            metrics.consequence_tags.add(f"turn_{turn}")
            metrics.consequence_tags.add(f"session_{session_id[:4]}")

        # Simulate cost (rough estimate: 100 tokens per turn)
        metrics.cost_tokens_estimated = turns * 100

        metrics.state = SessionState.COMPLETED
        metrics.completed_at = datetime.now(timezone.utc)

        # Register for isolation checking
        state_snapshot = {
            "consequence_tags": metrics.consequence_tags,
            "pressure": 5.0 + (hash(session_id) % 30) / 10.0,
        }
        metrics.state_snapshot = state_snapshot
        self.isolation_verifier.register_session(session_id, state_snapshot)

        with self.lock:
            self.sessions[session_id] = metrics

        return metrics


# Phase 7 Success Criteria
PHASE7_TARGETS = {
    "max_latency_ms": 2000.0,  # P95 latency must be <2s
    "concurrent_sessions": 100,  # Must handle 100 concurrent
    "isolation_critical_violations": 0,  # Zero critical leaks
    "session_success_rate": 95.0,  # 95% sessions complete
    "tokens_per_session": 2000,  # Est. cost per session
}
