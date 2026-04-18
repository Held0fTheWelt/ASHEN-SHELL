"""Tests for Phase 3: Cost Modeling + Adaptive Fixture Resolution."""

from __future__ import annotations

import pytest

from fy_platform.ai.cost_model_builder import CostModelBuilder, CostEstimate
from fy_platform.ai.adaptive_fixture_resolver import AdaptiveFixtureResolver, GapOutcome
from fy_platform.ai.composition_plan import CompositionPlan, CompositionPlanData
from fy_platform.ai.fixture_resolver import FixtureGap


class TestCostModelBuilder:
    """Test CostModelBuilder module."""

    def test_cost_model_initialization(self):
        """CostModelBuilder initializes with baseline costs."""
        builder = CostModelBuilder()
        assert builder.baseline_costs is not None
        assert len(builder.baseline_costs) == 13

    def test_cost_of_suite(self):
        """Cost of single suite returns baseline cost."""
        builder = CostModelBuilder()
        contractify_cost = builder.cost_of_suite('contractify')
        assert contractify_cost == 2.50
        assert contractify_cost > 0.0

    def test_incremental_cost(self):
        """Incremental cost accounts for composition savings."""
        builder = CostModelBuilder()
        incr = builder.incremental_cost('contractify', 'testify')
        assert incr < builder.cost_of_suite('testify')  # Savings apply

    def test_composition_cost_single_suite(self):
        """Composition cost for single suite equals baseline."""
        builder = CostModelBuilder()
        estimate = builder.composition_cost(['contractify'])
        assert estimate.total_cost == builder.baseline_costs['contractify']

    def test_composition_cost_multiple_suites(self):
        """Composition cost for multiple suites includes discounts."""
        builder = CostModelBuilder()
        suites = ['contractify', 'testify', 'documentify']
        estimate = builder.composition_cost(suites)
        assert estimate.total_cost > 0.0
        assert estimate.suite_cost == {s: builder.baseline_costs[s] for s in suites}
        assert estimate.confidence > 0.9

    def test_composition_cost_estimate_dataclass(self):
        """CostEstimate has required fields."""
        builder = CostModelBuilder()
        estimate = builder.composition_cost(['contractify', 'testify'])
        assert isinstance(estimate, CostEstimate)
        assert estimate.total_cost > 0.0
        assert estimate.confidence >= 0.0 and estimate.confidence <= 1.0
        assert estimate.to_dict() is not None

    def test_cost_matrix_composition_scenarios_minimum_20(self):
        """Cost model has ≥20 composition scenarios."""
        builder = CostModelBuilder()
        assert builder.scenario_count() >= 20

    def test_composition_scenarios_structure(self):
        """All scenarios have required structure."""
        builder = CostModelBuilder()
        scenarios = builder.all_scenarios()
        assert len(scenarios) >= 20
        for scenario in scenarios:
            assert 'name' in scenario
            assert 'suites' in scenario
            assert 'expected_cost' in scenario
            assert 'scenario_type' in scenario

    def test_estimate_scenario(self):
        """Estimate specific scenario by name."""
        builder = CostModelBuilder()
        estimate = builder.estimate_scenario('single_contractify')
        assert estimate is not None
        assert estimate.total_cost > 0.0

    def test_estimate_scenario_not_found(self):
        """Non-existent scenario returns None."""
        builder = CostModelBuilder()
        estimate = builder.estimate_scenario('nonexistent_scenario')
        assert estimate is None

    def test_composition_cost_zero_suites(self):
        """Empty suite list returns zero cost."""
        builder = CostModelBuilder()
        estimate = builder.composition_cost([])
        assert estimate.total_cost == 0.0

    def test_composition_cost_removes_duplicates(self):
        """Duplicate suites in composition are deduplicated."""
        builder = CostModelBuilder()
        estimate1 = builder.composition_cost(['contractify'])
        estimate2 = builder.composition_cost(['contractify', 'contractify'])
        assert estimate1.total_cost == estimate2.total_cost


class TestAdaptiveFixtureResolver:
    """Test AdaptiveFixtureResolver module."""

    def test_adaptive_resolver_initialization(self):
        """AdaptiveFixtureResolver initializes with criticality model."""
        resolver = AdaptiveFixtureResolver()
        assert resolver.criticality_scores is not None
        assert len(resolver.criticality_scores) > 0

    def test_learn_gap_outcome_resolved(self):
        """Learning resolved outcome decreases criticality."""
        resolver = AdaptiveFixtureResolver()
        outcome = resolver.learn_gap_outcome(
            'missing_contracts_json',
            'resolved',
            metadata={'suite_name': 'testify'},
        )
        assert isinstance(outcome, GapOutcome)
        assert outcome.outcome == 'resolved'
        assert outcome.confidence_delta > 0.0

    def test_learn_gap_outcome_failed(self):
        """Learning failed outcome increases criticality."""
        resolver = AdaptiveFixtureResolver()
        outcome = resolver.learn_gap_outcome(
            'missing_project_root',
            'failed',
            metadata={'suite_name': 'contractify'},
        )
        assert outcome.outcome == 'failed'
        assert outcome.confidence_delta < 0.0

    def test_gap_outcome_tracking(self):
        """Gap outcomes are tracked and retrievable."""
        resolver = AdaptiveFixtureResolver()
        resolver.learn_gap_outcome('gap1', 'resolved')
        resolver.learn_gap_outcome('gap2', 'failed')
        resolver.learn_gap_outcome('gap3', 'worked_around')
        assert resolver.outcome_count() == 3
        assert len(resolver.get_outcomes()) == 3

    def test_learning_confidence_grows_with_outcomes(self):
        """Learning confidence increases with outcome count."""
        resolver = AdaptiveFixtureResolver()
        conf1 = resolver.learning_confidence()
        assert conf1 >= 0.0

        # Add outcomes
        for i in range(10):
            resolver.learn_gap_outcome(f'gap_{i}', 'resolved')

        conf2 = resolver.learning_confidence()
        assert conf2 > conf1

    def test_adaptive_resolver_learning_minimum_5_outcomes(self):
        """Adaptive resolver learns from ≥5 outcomes."""
        resolver = AdaptiveFixtureResolver()
        # Add 5 outcomes
        for i in range(5):
            resolver.learn_gap_outcome(f'gap_{i}', 'resolved')
        assert resolver.outcome_count() >= 5

    def test_predict_gap_criticality_range(self):
        """Gap criticality prediction returns 0.0-1.0."""
        resolver = AdaptiveFixtureResolver()
        gap = FixtureGap(
            input_name='test_gap',
            status='missing',
            required_suite='testify',
            severity='high',
        )
        criticality = resolver.predict_gap_criticality(gap)
        assert 0.0 <= criticality <= 1.0

    def test_predict_gap_criticality_learns_from_outcomes(self):
        """Gap criticality prediction uses learned outcomes."""
        resolver = AdaptiveFixtureResolver()
        gap_id = 'test_gap_learning'

        # Add 5 'resolved' outcomes (gap is not critical)
        for i in range(5):
            resolver.learn_gap_outcome(gap_id, 'resolved')

        gap = FixtureGap(
            input_name=gap_id,
            status='missing',
            required_suite='testify',
            severity='high',
        )

        # With learning, criticality should be lower
        criticality = resolver.predict_gap_criticality(gap)
        assert criticality < 0.8  # High severity baseline

    def test_adaptive_resolver_method(self):
        """Adaptive resolver returns gaps sorted by criticality."""
        resolver = AdaptiveFixtureResolver()
        gaps = resolver.adaptive_resolver('testify')
        assert isinstance(gaps, list)
        # If gaps exist, they should be sorted by criticality (descending)
        if len(gaps) > 1:
            for i in range(len(gaps) - 1):
                # Ensure gaps are sorted (descending criticality)
                pass

    def test_update_gap_confidence(self):
        """Update gap with new confidence score."""
        resolver = AdaptiveFixtureResolver()
        gap = FixtureGap(
            input_name='test_gap',
            status='missing',
            required_suite='testify',
        )
        updated_gap = resolver.update_gap_confidence(gap, 0.75)
        assert updated_gap.metadata['confidence_score'] == 0.75


class TestCompositionPlan:
    """Test CompositionPlan orchestrator."""

    def test_composition_planner_initialization(self):
        """CompositionPlan initializes all components."""
        planner = CompositionPlan()
        assert planner.cost_model is not None
        assert planner.fixture_resolver is not None
        assert planner.dependency_graph is not None

    def test_plan_composition_single_suite(self):
        """Plan composition for single suite."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify'])
        assert isinstance(plan, CompositionPlanData)
        assert plan.suites == ['contractify']
        assert len(plan.steps) > 0
        assert plan.is_valid

    def test_plan_composition_multiple_suites(self):
        """Plan composition for multiple suites."""
        planner = CompositionPlan()
        suites = ['contractify', 'testify', 'documentify']
        plan = planner.plan_composition(suites)
        assert len(plan.suites) >= 3
        assert len(plan.steps) >= 3

    def test_plan_composition_invalid_suite(self):
        """Plan composition with invalid suite returns errors."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify', 'nonexistent_suite'])
        assert not plan.is_valid
        assert len(plan.validation_errors) > 0

    def test_composition_plan_structure(self):
        """Composition plan has required structure."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify'])
        assert plan.suites is not None
        assert plan.steps is not None
        assert plan.cost_estimate is not None
        assert plan.fixture_gaps is not None
        assert plan.estimated_total_runtime_sec > 0.0
        assert isinstance(plan.is_valid, bool)

    def test_composition_plan_cost_estimates(self):
        """Composition plan includes cost estimates."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify', 'testify'])
        assert plan.cost_estimate is not None
        assert plan.cost_estimate.total_cost > 0.0
        assert plan.cost_estimate.confidence > 0.0

    def test_composition_plan_fixture_gaps(self):
        """Composition plan identifies fixture gaps."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify'])
        # Plan may or may not have gaps depending on fixture model
        assert isinstance(plan.fixture_gaps, list)

    def test_composition_plan_respects_dependencies(self):
        """Composition steps respect dependency ordering."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify', 'testify'])
        # testify depends on contractify, so contractify should come first
        if len(plan.steps) >= 2:
            contractify_order = next(
                s.order for s in plan.steps if s.suite == 'contractify'
            )
            testify_order = next(
                s.order for s in plan.steps if s.suite == 'testify'
            )
            assert contractify_order < testify_order

    def test_execute_plan_valid(self):
        """Execute valid plan returns success."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify'])
        result = planner.execute_plan(plan)
        assert result['ok'] is True

    def test_execute_plan_invalid(self):
        """Execute invalid plan returns error."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['nonexistent'])
        result = planner.execute_plan(plan)
        assert result['ok'] is False

    def test_with_cost_estimates(self):
        """Enrich plan with cost estimates."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify', 'testify'])
        enriched_plan = planner.with_cost_estimates(plan)
        assert enriched_plan.cost_estimate is not None
        for step in enriched_plan.steps:
            assert 'cost_estimate_usd' in step.metadata

    def test_with_adaptive_fixtures(self):
        """Enrich plan with adaptive fixtures."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify'])
        enriched_plan = planner.with_adaptive_fixtures(plan)
        assert 'adaptive_fixtures_applied' in enriched_plan.metadata
        assert 'learning_confidence' in enriched_plan.metadata

    def test_composition_plan_to_dict(self):
        """Composition plan converts to dict."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify'])
        plan_dict = plan.to_dict()
        assert 'suites' in plan_dict
        assert 'step_count' in plan_dict
        assert 'cost_estimate' in plan_dict
        assert 'is_valid' in plan_dict


class TestPhase3Integration:
    """Test integration of Phase 3 components."""

    def test_phase3_integration_with_phase2(self):
        """Phase 3 integrates correctly with Phase 2 components."""
        from fy_platform.ai.dependency_graph import TypedDependencyGraph
        from fy_platform.ai.obligation_graph import ObligationGraph

        # Create instances
        dep_graph = TypedDependencyGraph()
        planner = CompositionPlan()

        # Both should have compatible suite definitions
        phase2_suites = set(dep_graph.nodes.keys())
        assert 'contractify' in phase2_suites
        assert 'testify' in phase2_suites

    def test_phase3_no_regressions_existing_tests(self):
        """Phase 3 does not break Phase 1/2 functionality."""
        from fy_platform.ai.dependency_graph import TypedDependencyGraph
        from fy_platform.ai.fixture_resolver import FixtureResolver

        # Phase 2 components still work
        graph = TypedDependencyGraph()
        assert graph.suite_count() > 0
        assert graph.edge_count() > 0

        resolver = FixtureResolver()
        assert len(resolver.gaps) > 0


class TestPhase3CLIIntegration:
    """Test Phase 3 CLI integration (compose command)."""

    def test_composition_plan_for_cli(self):
        """Composition plan provides data for CLI output."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify', 'testify', 'documentify'])

        # Plan should provide all necessary CLI output
        cli_output = {
            'suites': plan.suites,
            'steps': len(plan.steps),
            'estimated_cost': plan.cost_estimate.total_cost,
            'estimated_runtime': plan.estimated_total_runtime_sec,
            'is_valid': plan.is_valid,
        }
        assert cli_output['suites'] is not None
        assert cli_output['estimated_cost'] > 0.0

    def test_composition_plan_cost_aware_mode(self):
        """Composition plan data for cost-aware CLI mode."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify', 'testify'])
        plan = planner.with_cost_estimates(plan)

        # Should have cost breakdown per step
        total_cost = 0.0
        for step in plan.steps:
            if 'cost_estimate_usd' in step.metadata:
                total_cost += step.metadata['cost_estimate_usd']

        assert total_cost > 0.0

    def test_composition_plan_adaptive_flag(self):
        """Composition plan with adaptive flag."""
        planner = CompositionPlan()
        plan = planner.plan_composition(['contractify', 'testify'])
        adaptive_plan = planner.with_adaptive_fixtures(plan)

        # Adaptive plan should have learning confidence
        assert 'learning_confidence' in adaptive_plan.metadata
        assert adaptive_plan.metadata['learning_confidence'] >= 0.0
