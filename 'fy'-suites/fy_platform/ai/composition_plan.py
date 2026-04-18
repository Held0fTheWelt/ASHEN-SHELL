"""CompositionPlan: Orchestrate suite composition with cost and fixture constraints."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from fy_platform.ai.cost_model_builder import CostModelBuilder, CostEstimate
from fy_platform.ai.adaptive_fixture_resolver import AdaptiveFixtureResolver
from fy_platform.ai.dependency_graph import TypedDependencyGraph
from fy_platform.ai.fixture_resolver import FixtureGap


@dataclass
class CompositionStep:
    """A step in suite composition."""
    suite: str
    order: int
    dependencies_satisfied: list[str] = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_runtime_sec: float = 0.0
    fixture_gaps: list[FixtureGap] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompositionPlanData:
    """Complete plan for suite composition."""
    suites: list[str] = field(default_factory=list)
    steps: list[CompositionStep] = field(default_factory=list)
    cost_estimate: CostEstimate | None = None
    fixture_gaps: list[FixtureGap] = field(default_factory=list)
    estimated_total_runtime_sec: float = 0.0
    is_valid: bool = False
    validation_errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dict for serialization."""
        return {
            'suites': self.suites,
            'step_count': len(self.steps),
            'cost_estimate': self.cost_estimate.to_dict() if self.cost_estimate else None,
            'fixture_gap_count': len(self.fixture_gaps),
            'estimated_total_runtime_sec': self.estimated_total_runtime_sec,
            'is_valid': self.is_valid,
            'validation_errors': self.validation_errors,
            'metadata': self.metadata,
        }


class CompositionPlan:
    """Orchestrate suite composition with cost estimates and adaptive fixtures.

    Integrates Phase 2 dependency graph with Phase 3 cost and learning.
    """

    def __init__(self):
        """Initialize composition planner."""
        self.cost_model = CostModelBuilder()
        self.fixture_resolver = AdaptiveFixtureResolver()
        self.dependency_graph = TypedDependencyGraph()

    def plan_composition(self, suites: list[str]) -> CompositionPlanData:
        """Create a composition plan for a list of suites.

        Parameters
        ----------
        suites : list[str]
            Suites to compose

        Returns
        -------
        CompositionPlanData
            Composition plan with steps, costs, and gaps
        """
        suites = list(set(suites))  # Remove duplicates

        plan = CompositionPlanData()
        plan.suites = suites

        # Validate suites against dependency graph
        plan.validation_errors = self._validate_suites(suites)

        if plan.validation_errors:
            plan.is_valid = False
            return plan

        # Topological sort: determine composition order
        steps = self._create_composition_steps(suites)
        plan.steps = steps

        # Estimate costs
        plan.cost_estimate = self.cost_model.composition_cost(suites)

        # Identify fixture gaps
        plan.fixture_gaps = self._identify_gaps(suites)

        # Estimate runtime
        plan.estimated_total_runtime_sec = self._estimate_runtime(suites)

        # Mark as valid if no critical gaps
        critical_gaps = [g for g in plan.fixture_gaps if g.severity == 'critical']
        plan.is_valid = len(critical_gaps) == 0

        plan.metadata = {
            'created_by': 'composition_planner',
            'version': '1.0',
        }

        return plan

    def _validate_suites(self, suites: list[str]) -> list[str]:
        """Validate suites exist in dependency graph.

        Parameters
        ----------
        suites : list[str]
            Suites to validate

        Returns
        -------
        list[str]
            List of validation errors
        """
        errors = []
        valid_suites = set(self.dependency_graph.nodes.keys())

        for suite in suites:
            if suite not in valid_suites:
                errors.append(f"Suite '{suite}' not found in dependency graph")

        return errors

    def _create_composition_steps(self, suites: list[str]) -> list[CompositionStep]:
        """Create ordered composition steps respecting dependencies.

        Parameters
        ----------
        suites : list[str]
            Suites to compose

        Returns
        -------
        list[CompositionStep]
            Ordered composition steps
        """
        steps = []
        completed = set()
        order = 0

        # Simple topological sort
        remaining = set(suites)

        while remaining:
            # Find suites with all dependencies satisfied
            ready = []
            for suite in remaining:
                deps = self.dependency_graph.dependencies_of(suite)
                if all(d in completed or d not in suites for d in deps):
                    ready.append(suite)

            if not ready:
                # Fallback: add remaining in any order
                ready = list(remaining)

            for suite in ready:
                cost = self.cost_model.cost_of_suite(suite)
                step = CompositionStep(
                    suite=suite,
                    order=order,
                    dependencies_satisfied=list(completed),
                    estimated_cost=cost,
                    estimated_runtime_sec=self._estimate_suite_runtime(suite),
                )
                steps.append(step)
                completed.add(suite)
                remaining.remove(suite)
                order += 1

        return steps

    def _identify_gaps(self, suites: list[str]) -> list[FixtureGap]:
        """Identify fixture gaps in suite composition.

        Parameters
        ----------
        suites : list[str]
            Suites being composed

        Returns
        -------
        list[FixtureGap]
            Fixture gaps found
        """
        gaps = []
        available_outputs = set()

        # Build set of available outputs
        for suite in suites:
            if suite in self.fixture_resolver.fixtures:
                # Add outputs from this suite
                for fixture_name, fixture in self.fixture_resolver.fixtures.items():
                    if suite in fixture.provided_by:
                        available_outputs.add(fixture_name)

        # Check for missing inputs
        for suite in suites:
            # Get expected inputs for this suite
            suite_fixtures = self.fixture_resolver.fixtures
            for fixture_name, fixture in suite_fixtures.items():
                if suite in fixture.consumed_by:
                    if fixture_name not in available_outputs:
                        # Missing input
                        gap = FixtureGap(
                            input_name=fixture_name,
                            status='missing',
                            required_suite=suite,
                            provided_by=fixture.provided_by,
                            severity='medium',
                            metadata={'suite_name': suite},
                        )
                        gaps.append(gap)

        return gaps

    def _estimate_suite_runtime(self, suite: str) -> float:
        """Estimate runtime for a single suite.

        Parameters
        ----------
        suite : str
            Suite name

        Returns
        -------
        float
            Estimated runtime in seconds
        """
        # Baseline runtimes
        baseline_runtimes = {
            'fy_platform': 5.0,
            'contractify': 45.0,
            'testify': 60.0,
            'documentify': 50.0,
            'docify': 30.0,
            'despaghettify': 40.0,
            'securify': 50.0,
            'templatify': 25.0,
            'usabilify': 35.0,
            'observifyfy': 40.0,
            'metrify': 30.0,
            'postmanify': 25.0,
            'mvpify': 70.0,
        }
        return baseline_runtimes.get(suite, 45.0)

    def _estimate_runtime(self, suites: list[str]) -> float:
        """Estimate total runtime for suite composition.

        Parameters
        ----------
        suites : list[str]
            Suites being composed

        Returns
        -------
        float
            Estimated total runtime in seconds
        """
        total = 0.0
        for suite in suites:
            total += self._estimate_suite_runtime(suite)

        # Apply parallelization factor (assume ~60% parallelization)
        return total * 0.6

    def execute_plan(self, plan: CompositionPlanData) -> dict:
        """Execute a composition plan.

        Parameters
        ----------
        plan : CompositionPlan
            Plan to execute

        Returns
        -------
        dict
            Execution result
        """
        if not plan.is_valid:
            return {
                'ok': False,
                'error': 'Plan contains validation errors',
                'errors': plan.validation_errors,
            }

        return {
            'ok': True,
            'suite_count': len(plan.suites),
            'step_count': len(plan.steps),
            'estimated_cost': plan.cost_estimate.total_cost if plan.cost_estimate else 0.0,
            'estimated_runtime_sec': plan.estimated_total_runtime_sec,
            'fixture_gap_count': len(plan.fixture_gaps),
        }

    def with_cost_estimates(self, plan: CompositionPlanData) -> CompositionPlanData:
        """Enrich plan with detailed cost estimates.

        Parameters
        ----------
        plan : CompositionPlan
            Plan to enrich

        Returns
        -------
        CompositionPlan
            Enriched plan
        """
        if not plan.cost_estimate:
            plan.cost_estimate = self.cost_model.composition_cost(plan.suites)

        # Add cost estimates to each step
        for i, step in enumerate(plan.steps):
            suite_cost = self.cost_model.cost_of_suite(step.suite)
            step.estimated_cost = suite_cost
            step.metadata['cost_estimate_usd'] = round(suite_cost, 2)

        plan.metadata['cost_estimates_added'] = True
        return plan

    def with_adaptive_fixtures(self, plan: CompositionPlanData) -> CompositionPlanData:
        """Enrich plan with adaptive fixture recommendations.

        Parameters
        ----------
        plan : CompositionPlan
            Plan to enrich

        Returns
        -------
        CompositionPlan
            Enriched plan
        """
        # Apply adaptive fixture resolver to each suite
        adaptive_gaps = []
        for suite in plan.suites:
            suite_adaptive_gaps = self.fixture_resolver.adaptive_resolver(suite)
            adaptive_gaps.extend(suite_adaptive_gaps)

        plan.fixture_gaps = adaptive_gaps
        plan.metadata['adaptive_fixtures_applied'] = True
        plan.metadata['learning_confidence'] = self.fixture_resolver.learning_confidence()

        return plan
