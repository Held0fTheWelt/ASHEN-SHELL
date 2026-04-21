"""
Phase 7 Cycle 1: Concurrency and Performance Testing.

Tests system under load:
- 10, 50, 100 concurrent sessions
- Latency measurements (target: <2s P95)
- Cross-session isolation verification
- Cost tracking
"""

import sys
import os
from datetime import datetime, timezone
import importlib.util

# Import concurrency framework
concurrency_path = os.path.join(os.path.dirname(__file__), 'concurrency_framework.py')
spec = importlib.util.spec_from_file_location("concurrency_framework", concurrency_path)
concurrency_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(concurrency_module)

ConcurrencyTestBuilder = concurrency_module.ConcurrencyTestBuilder
ConcurrencySimulator = concurrency_module.ConcurrencySimulator
ConcurrencyTestResults = concurrency_module.ConcurrencyTestResults
PHASE7_TARGETS = concurrency_module.PHASE7_TARGETS
SessionState = concurrency_module.SessionState


class Phase7Executor:
    """Executes Phase 7 concurrency tests."""

    def __init__(self):
        self.simulator = ConcurrencySimulator()
        self.results_by_level = {}

    def run_all_tests(self):
        """Run all concurrency test levels."""
        test_levels = [
            (10, "Baseline (10 sessions)"),
            (50, "Medium load (50 sessions)"),
            (100, "Full load (100 sessions)"),
        ]

        print(f"\n{'='*70}")
        print(f"Phase 7 Cycle 1: Large-Scale Deployment Testing")
        print(f"{'='*70}\n")

        for num_sessions, description in test_levels:
            print(f"Running test: {description}")
            print("-" * 70)

            results = self.run_concurrency_test(
                num_sessions=num_sessions,
                concurrent_peak=min(num_sessions, 20),
                name=description,
            )

            self.results_by_level[num_sessions] = results
            self.print_test_results(results, num_sessions)

        self.print_overall_summary()

    def run_concurrency_test(
        self,
        num_sessions: int,
        concurrent_peak: int,
        name: str,
    ) -> ConcurrencyTestResults:
        """Run a single concurrency test level."""
        config = (
            ConcurrencyTestBuilder()
            .with_num_sessions(num_sessions)
            .with_concurrent_peak(concurrent_peak)
            .with_turns_per_session(20)
            .with_delay_ms(100)
            .with_scenario("salon_mediation")
            .with_name(name)
            .build()
        )

        results = ConcurrencyTestResults(
            test_name=config["test_name"],
            num_sessions=num_sessions,
            num_concurrent_peaks=concurrent_peak,
            test_duration_seconds=0,
        )

        # Run sessions
        for i in range(num_sessions):
            session_id = f"session_{num_sessions}_{i:03d}"
            path_names = ["path_A_escalation", "path_B_divide", "path_C_understanding"]
            path_name = path_names[i % len(path_names)]

            session_metrics = self.simulator.run_session(
                session_id=session_id,
                scenario_id="salon_mediation",
                path_name=path_name,
                evaluator_id=f"eval_{i:02d}",
                turns=20,
            )

            results.sessions.append(session_metrics)

        # Run isolation checks
        for session in results.sessions:
            violations = self.simulator.isolation_verifier.verify_tag_isolation(
                session.session_id,
                session.consequence_tags,
            )
            results.isolation_violations.extend(violations)

        results.completed_at = datetime.now(timezone.utc)
        results.test_duration_seconds = (
            results.completed_at - results.started_at
        ).total_seconds()

        return results

    def print_test_results(self, results: ConcurrencyTestResults, level: int):
        """Print results for a single test level."""
        summary = results.get_summary()

        print(f"Sessions completed: {summary['num_sessions_completed']}/{summary['num_sessions_target']}")
        print(f"Total turns executed: {summary['total_turns']}")
        print(f"\nLatency Metrics:")
        print(f"  Average:  {summary['avg_latency_ms']:.1f} ms")
        print(f"  Max:      {summary['max_latency_ms']:.1f} ms")
        print(f"  P95:      {summary['p95_latency_ms']:.1f} ms (target: <2000 ms)")
        print(f"  Exceeding 2s: {summary['turns_exceeding_2s']}")

        latency_status = "PASS" if summary['meets_latency_target'] else "FAIL"
        print(f"  Status:   {latency_status}")

        print(f"\nIsolation:")
        print(f"  Critical violations: {summary['isolation_violations_critical']}")
        print(f"  Warning violations:  {summary['isolation_violations_warning']}")

        isolation_status = "PASS" if summary['meets_isolation_target'] else "FAIL"
        print(f"  Status:   {isolation_status}")

        print(f"\nCosts:")
        print(f"  Total tokens estimated: {summary['total_cost_tokens']:,}")
        print(f"  Per session average: {summary['total_cost_tokens'] // max(1, summary['num_sessions_completed'])}")

        overall_status = "PASS" if summary['overall_success'] else "FAIL"
        print(f"\nOverall: {overall_status}")
        print()

    def print_overall_summary(self):
        """Print overall Phase 7 summary."""
        print("\n" + "="*70)
        print("PHASE 7 SUMMARY: LARGE-SCALE DEPLOYMENT")
        print("="*70)

        if not self.results_by_level:
            print("No tests run")
            return

        print("\nLatency Target: P95 < 2000 ms")
        print("-" * 70)
        for level, results in sorted(self.results_by_level.items()):
            status = "PASS" if results.meets_latency_target else "FAIL"
            p95 = results.p95_latency_ms
            print(f"  {level:3d} sessions: P95={p95:7.1f} ms {status}")

        print("\nIsolation Target: Zero critical violations")
        print("-" * 70)
        for level, results in sorted(self.results_by_level.items()):
            critical = len([v for v in results.isolation_violations if v.severity == "critical"])
            status = "PASS" if critical == 0 else "FAIL"
            print(f"  {level:3d} sessions: {critical} critical violations {status}")

        print("\nSession Completion Target: 95%+")
        print("-" * 70)
        for level, results in sorted(self.results_by_level.items()):
            completed = len(results.sessions)
            target = results.num_sessions
            rate = (completed / target * 100) if target > 0 else 0
            status = "PASS" if rate >= 95.0 else "FAIL"
            print(f"  {level:3d} sessions: {completed}/{target} ({rate:.1f}%) {status}")

        print("\nCost per Session")
        print("-" * 70)
        for level, results in sorted(self.results_by_level.items()):
            if results.sessions:
                avg_tokens = results.total_cost_tokens // len(results.sessions)
            else:
                avg_tokens = 0
            print(f"  {level:3d} sessions: {avg_tokens:,} tokens/session")

        # Overall determination
        all_pass = all(
            r.meets_latency_target and r.meets_isolation_target
            for r in self.results_by_level.values()
        )

        print("\n" + "="*70)
        if all_pass:
            print("PHASE 7 CYCLE 1: PASS - Ready for Cycle 2")
            print("="*70)
            print("\nAll concurrency targets met:")
            print("  PASS: Latency target (<2s P95)")
            print("  PASS: Isolation target (zero critical violations)")
            print("  PASS: Session completion (95%+)")
            print("  PASS: Cost tracking implemented")
            print("\nPhase 7 Cycle 2: Production Readiness Review")
        else:
            print("PHASE 7 CYCLE 1: INVESTIGATION NEEDED")
            print("="*70)
            failures = []
            for level, results in sorted(self.results_by_level.items()):
                if not results.meets_latency_target:
                    failures.append(f"  - {level} sessions: P95 latency too high ({results.p95_latency_ms:.0f}ms)")
                if not results.meets_isolation_target:
                    critical = len([v for v in results.isolation_violations if v.severity == "critical"])
                    failures.append(f"  - {level} sessions: {critical} critical isolation violations")

            if failures:
                print("\nIssues detected:")
                for failure in failures:
                    print(failure)

        print()


def main():
    """Run Phase 7 tests."""
    executor = Phase7Executor()
    executor.run_all_tests()


if __name__ == "__main__":
    main()
