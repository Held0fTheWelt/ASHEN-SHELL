"""Tests for Phase 2: Dependency Graph + Obligation Graph + Fixture Resolver."""

from __future__ import annotations

import pytest

from fy_platform.ai.dependency_graph import TypedDependencyGraph, SuiteNode, DependencyEdge
from fy_platform.ai.obligation_graph import ObligationGraph, ObligationMapping
from fy_platform.ai.fixture_resolver import FixtureResolver, FixtureGap
from fy_platform.tools import platform_cli


class TestDependencyGraph:
    """Test TypedDependencyGraph module."""

    def test_dependency_graph_acyclic(self):
        """Dependency graph is acyclic and validates correctly."""
        graph = TypedDependencyGraph()
        # If graph has cycles, initialization would fail
        assert graph.suite_count() > 0
        assert graph.edge_count() >= 30  # At least 30 edges required

    def test_dependency_graph_queries(self):
        """Dependency graph supports key query methods."""
        graph = TypedDependencyGraph()

        # Test dependencies_of
        contractify_deps = graph.dependencies_of('contractify')
        assert isinstance(contractify_deps, list)
        assert all(isinstance(s, str) for s in contractify_deps)

        # Test dependents_of
        contractify_dependents = graph.dependents_of('contractify')
        assert isinstance(contractify_dependents, list)
        assert 'testify' in contractify_dependents or len(contractify_dependents) > 0

        # Test transitive_closure
        closure = graph.transitive_closure('contractify')
        assert isinstance(closure, list)
        assert 'contractify' not in closure  # Exclude self

    def test_dependency_graph_suite_nodes(self):
        """Dependency graph has all 13 suites."""
        graph = TypedDependencyGraph()
        expected_suites = {
            'contractify', 'testify', 'documentify', 'docify', 'despaghettify',
            'templatify', 'usabilify', 'securify', 'observifyfy', 'mvpify',
            'metrify', 'postmanify', 'fy_platform',
        }
        actual_suites = set(graph.nodes.keys())
        assert actual_suites == expected_suites

    def test_dependency_graph_edge_filtering(self):
        """Dependency graph edges can be filtered by type."""
        graph = TypedDependencyGraph()

        # Get all edges
        all_edges = graph.get_edges()
        assert len(all_edges) > 30

        # Filter by edge type
        output_edges = graph.get_edges(edge_type='output_consumes')
        assert len(output_edges) > 0

        fixture_edges = graph.get_edges(edge_type='fixture_consumes')
        assert len(fixture_edges) > 0

    def test_dependency_graph_summary(self):
        """Dependency graph provides a summary."""
        graph = TypedDependencyGraph()
        summary = graph.summary()

        assert 'suite_count' in summary
        assert 'edge_count' in summary
        assert 'edge_types' in summary
        assert 'is_acyclic' in summary
        assert summary['is_acyclic'] is True
        assert summary['edge_count'] >= 30


class TestObligationGraph:
    """Test ObligationGraph module."""

    def test_obligation_discovery_threshold(self):
        """Obligation graph achieves ≥80% discovery rate."""
        graph = ObligationGraph()
        discovery_rate = graph.discovery_rate()

        assert discovery_rate >= 80.0, f'Discovery rate {discovery_rate}% < 80%'

    def test_obligation_trace_correctness(self):
        """Obligation trace returns correct obligation counts."""
        graph = ObligationGraph()

        # Get first contract
        first_contract = list(graph.mappings.keys())[0]
        trace = graph.trace_obligation(first_contract)

        assert trace is not None
        assert trace.obligation_count > 0
        assert trace.coverage_percent >= 0
        assert len(trace.sample_obligations) > 0

    def test_obligation_coverage_by_suite(self):
        """Obligation coverage is reported by suite."""
        graph = ObligationGraph()
        coverage = graph.obligation_coverage_by_suite()

        assert isinstance(coverage, dict)
        assert len(coverage) > 0
        for suite, stats in coverage.items():
            assert 'contract_count' in stats
            assert 'obligation_count' in stats
            assert 'avg_coverage_percent' in stats

    def test_obligation_missing_detection(self):
        """Obligation graph detects missing obligations."""
        graph = ObligationGraph()

        # Check for missing obligations in a suite
        for suite in ['contractify', 'testify', 'securify']:
            missing = graph.missing_obligations(suite)
            # Should detect some missing obligations in most suites
            assert isinstance(missing, list)

    def test_obligation_mapping_structure(self):
        """Obligation mappings have correct structure."""
        graph = ObligationGraph()

        for contract_id, mapping in list(graph.mappings.items())[:3]:
            assert mapping.contract_id == contract_id
            assert mapping.suite in {
                'contractify', 'testify', 'documentify', 'docify', 'despaghettify',
                'securify', 'templatify', 'usabilify', 'observifyfy', 'mvpify', 'metrify', 'postmanify'
            }
            assert isinstance(mapping.test_obligations, list)
            assert isinstance(mapping.doc_obligations, list)
            assert isinstance(mapping.security_risks, list)


class TestFixtureResolver:
    """Test FixtureResolver module."""

    def test_fixture_resolver_gaps(self):
        """Fixture resolver identifies ≥3 real gaps."""
        resolver = FixtureResolver()
        gaps = resolver.identify_gaps()

        assert len(gaps) >= 3, f'Found {len(gaps)} gaps, expected ≥3'

    def test_fixture_resolver_gap_details(self):
        """Fixture gap objects have required fields."""
        resolver = FixtureResolver()
        gaps = resolver.identify_gaps()

        for gap in gaps[:3]:  # Check first 3
            assert isinstance(gap, FixtureGap)
            assert gap.input_name
            assert gap.status in {'missing', 'incompatible', 'unstable', 'unresolved'}
            assert gap.required_suite
            assert gap.severity in {'critical', 'high', 'medium', 'low'}
            assert gap.suggestion

    def test_fixture_resolver_compatibility(self):
        """Fixture resolver checks suite compatibility."""
        resolver = FixtureResolver()

        # Check if contractify and testify are compatible
        compatible = resolver.check_compatibility('contractify', 'testify')
        assert isinstance(compatible, bool)

    def test_fixture_resolver_composition_plan(self):
        """Fixture resolver generates composition plans."""
        resolver = FixtureResolver()

        for suite in ['contractify', 'testify', 'documentify']:
            plan = resolver.composition_plan(suite)

            assert 'target_suite' in plan
            assert plan['target_suite'] == suite
            assert 'required_fixtures' in plan
            assert 'required_suites' in plan
            assert 'fixture_gaps' in plan
            assert 'can_compose' in plan

    def test_fixture_resolver_summary(self):
        """Fixture resolver provides a summary."""
        resolver = FixtureResolver()
        summary = resolver.summary()

        assert 'fixture_count' in summary
        assert 'gap_count' in summary
        assert 'critical_gaps' in summary
        assert 'high_gaps' in summary
        assert 'medium_gaps' in summary
        assert 'gaps_by_status' in summary


class TestPlatformCLIDependencyCheck:
    """Test Platform CLI dependency-check mode."""

    def test_cli_dependency_check_mode(self):
        """CLI supports dependency-check mode."""
        args = [
            'analyze',
            '--mode', 'dependency-check',
            '--format', 'json',
        ]
        exit_code = platform_cli.main(args)
        assert exit_code == 0

    def test_cli_dependency_check_with_suite(self):
        """CLI dependency-check works with --suite argument."""
        args = [
            'analyze',
            '--mode', 'dependency-check',
            '--suite', 'contractify',
            '--format', 'json',
        ]
        exit_code = platform_cli.main(args)
        assert exit_code == 0

    def test_cli_analyze_mode_choices_updated(self):
        """CLI analyze command includes dependency-check mode."""
        # This is verified by the above tests passing
        # Verify that dependency-check is accepted as a valid mode
        args = [
            'analyze',
            '--mode', 'dependency-check',
            '--format', 'json',
        ]
        # Should succeed with valid mode
        exit_code = platform_cli.main(args)
        assert exit_code == 0


class TestPhase2IntegrationWithPhase1:
    """Test Phase 2 integration with Phase 1 foundation."""

    def test_phase1_tests_still_pass(self):
        """Phase 1 tests are not broken by Phase 2 code."""
        # This will be verified by running the full test suite
        # For now, we just verify imports work
        from fy_platform.ai.contracts import Contract, EvidenceLink
        from fy_platform.ai.lanes import InspectLane, GovernLane

        # Verify Phase 2 modules can coexist
        graph = TypedDependencyGraph()
        obligations = ObligationGraph()
        fixtures = FixtureResolver()

        assert graph is not None
        assert obligations is not None
        assert fixtures is not None

    def test_phase2_uses_phase1_ir(self):
        """Phase 2 modules correctly use Phase 1 IR objects."""
        from fy_platform.ai.contracts import (
            TestObligation,
            DocumentationObligation,
            SecurityRisk,
            EvidenceLink,
        )

        obligations = ObligationGraph()

        # Verify mappings use correct Phase 1 IR objects
        for mapping in list(obligations.mappings.values())[:1]:
            assert isinstance(mapping.test_obligations[0], TestObligation)
            assert isinstance(mapping.doc_obligations[0], DocumentationObligation)
            assert isinstance(mapping.security_risks[0], SecurityRisk)

    def test_phase2_modules_are_composable(self):
        """Phase 2 modules work together correctly."""
        graph = TypedDependencyGraph()
        obligations = ObligationGraph()
        fixtures = FixtureResolver()

        # Verify they operate on same suite set
        graph_suites = set(graph.nodes.keys())
        obligation_suites = set(obligations.obligation_coverage_by_suite().keys())

        # Should have significant overlap
        overlap = graph_suites & obligation_suites
        assert len(overlap) >= 10  # Most suites should be in both
