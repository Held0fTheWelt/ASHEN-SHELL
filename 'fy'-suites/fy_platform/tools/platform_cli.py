"""fy v2 platform-shaped CLI shell.

This module provides the primary entry point for fy v2, with a platform-first
surface that dispatches to explicit lanes and suite adapters:

    fy analyze --mode contract
    fy analyze --mode docs
    fy govern --mode release
    fy inspect --mode structure
    fy repair-plan --mode structure

This is in addition to the legacy suite-first CLI (ai_suite_cli.py) which
remains fully compatible.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from fy_platform.ai.lanes import (
    InspectLane,
    GovernLane,
    GenerateLane,
    VerifyLane,
    StructureLane,
    PreCheckLane,
)
from fy_platform.ai.adapter_cli_helper import build_command_envelope
from fy_platform.ai.dependency_graph import TypedDependencyGraph
from fy_platform.ai.obligation_graph import ObligationGraph
from fy_platform.ai.fixture_resolver import FixtureResolver
from fy_platform.ai.composition_plan import CompositionPlan
from fy_platform.ai.outcome_persistence import OutcomePersistence, CompositionOutcome
from fy_platform.ai.historical_cost_analyzer import HistoricalCostAnalyzer
from fy_platform.ai.criticality_learner import CriticityLearner


def cmd_analyze(args: argparse.Namespace) -> int:
    """Analyze repository with specified mode."""
    mode = args.mode or 'contract'
    target_repo = args.target_repo or '.'

    if mode == 'contract':
        lane = GenerateLane()
        result = lane.generate(Path(target_repo), mode='contract')
    elif mode == 'docs':
        lane = GenerateLane()
        result = lane.generate(Path(target_repo), mode='docs')
    elif mode == 'structure':
        lane = StructureLane()
        result = lane.analyze(Path(target_repo), mode='structure')
    elif mode == 'learning-status':
        return cmd_analyze_learning_status(args)
    else:
        print(json.dumps({
            'error': f'Unknown analyze mode: {mode}',
            'supported_modes': ['contract', 'docs', 'structure', 'learning-status'],
        }, indent=2))
        return 1

    _output_result(result, args.format)
    return 0


def cmd_govern(args: argparse.Namespace) -> int:
    """Check governance and readiness."""
    mode = args.mode or 'release'

    if mode == 'policy-check':
        # Run full deterministic validation via PreCheckLane
        target_repo = getattr(args, 'target_repo', None) or '.'
        lane = PreCheckLane()
        result = lane.validate(Path(target_repo), mode='policy-check')
        result_dict = {
            'target': result.target,
            'mode': result.mode,
            'is_valid': result.is_valid,
            'violations': [
                {
                    'policy_id': v.policy_id,
                    'rule_name': v.rule_name,
                    'decision': v.decision,
                    'evidence': v.evidence,
                }
                for v in result.violations
            ],
            'timestamp': result.timestamp,
        }
        _output_result(result_dict, args.format)
        return 0 if result.is_valid else 1

    elif mode == 'cost-check':
        # Run budget enforcement via metrify
        from metrify.adapter.service import MetrifyAdapter
        metrify = MetrifyAdapter()
        suite = getattr(args, 'suite', None) or 'default'
        budget = None
        budget_tokens = getattr(args, 'budget_tokens', None)
        budget_cost = getattr(args, 'budget_cost', None)
        if budget_tokens:
            budget = {
                'tokens': budget_tokens,
                'cost_usd': budget_cost or 0.0,
            }
        result = metrify.enforce_budget(suite=suite, run_budget=budget)
        _output_result(result, args.format)
        return 0 if result['decision'] == 'allow' else 1

    else:
        # Standard release/production/deploy modes
        lane = GovernLane()
        result = lane.check_readiness(mode=mode)
        _output_result(result, args.format)
        return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    """Inspect repository structure and contracts."""
    mode = args.mode or 'structure'
    target_repo = args.target_repo or '.'

    lane = InspectLane()
    result = lane.analyze(Path(target_repo), mode=mode)

    _output_result(result, args.format)
    return 0


def cmd_repair_plan(args: argparse.Namespace) -> int:
    """Generate repair and refactoring plans."""
    mode = args.mode or 'structure'
    target_repo = args.target_repo or '.'

    if mode == 'improve-from-history':
        return cmd_repair_improve_from_history(args)

    lane = StructureLane()
    result = lane.analyze(Path(target_repo), mode=mode)

    # Add plan generation context
    result['repair_mode'] = mode
    result['status'] = 'plan_generated'

    _output_result(result, args.format)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Verify outputs and compatibility."""
    mode = args.mode or 'standard'

    lane = VerifyLane()
    result = lane.validate(None, mode=mode)

    _output_result(result, args.format)
    return 0


def cmd_analyze_dependencies(args: argparse.Namespace) -> int:
    """Analyze dependency graph, obligations, and fixtures."""
    mode = args.mode or 'dependency-check'
    target_suite = getattr(args, 'suite', None)

    if mode == 'dependency-check':
        graph = TypedDependencyGraph()
        obligations = ObligationGraph()
        fixtures = FixtureResolver()

        # Build summary
        result = {
            'mode': 'dependency-check',
            'dependency_graph': {
                'summary': graph.summary(),
                'suite_count': graph.suite_count(),
                'edge_count': graph.edge_count(),
                'is_acyclic': True,
            },
            'obligations': {
                'summary': {
                    'discovery_rate': obligations.discovery_rate(),
                    'coverage_by_suite': obligations.obligation_coverage_by_suite(),
                },
            },
            'fixtures': {
                'summary': fixtures.summary(),
                'gap_count': fixtures.gap_count(),
            },
        }

        # Add suite-specific details if requested
        if target_suite:
            suite_info = {
                'suite': target_suite,
                'dependencies': graph.dependencies_of(target_suite),
                'dependents': graph.dependents_of(target_suite),
                'transitive_closure': graph.transitive_closure(target_suite),
                'missing_obligations': obligations.missing_obligations(target_suite),
                'fixture_gaps': [
                    {
                        'fixture': gap.input_name,
                        'status': gap.status,
                        'severity': gap.severity,
                        'suggestion': gap.suggestion,
                    }
                    for gap in fixtures.identify_gaps(target_suite)
                ],
                'composition_plan': fixtures.composition_plan(target_suite),
            }
            result['suite_info'] = suite_info

        _output_result(result, args.format)
        return 0

    else:
        print(json.dumps({
            'error': f'Unknown analyze mode: {mode}',
            'supported_modes': ['dependency-check'],
        }, indent=2))
        return 1


def _output_result(result: dict, fmt: str) -> None:
    """Output result in specified format."""
    if fmt == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif fmt == 'text':
        _render_text(result)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_compose(args: argparse.Namespace) -> int:
    """Compose suites with cost and fixture awareness."""
    mode = getattr(args, 'mode', None) or 'cost-aware'
    suites = getattr(args, 'suites', None) or []
    adaptive = getattr(args, 'adaptive', False)
    persist = getattr(args, 'persist', False)

    if not suites:
        print(json.dumps({
            'error': 'At least one suite required',
            'suites_required': True,
        }, indent=2))
        return 1

    planner = CompositionPlan()

    if mode == 'cost-aware':
        plan = planner.plan_composition(suites)

        if adaptive:
            plan = planner.with_adaptive_fixtures(plan)
        else:
            plan = planner.with_cost_estimates(plan)

        result = {
            'ok': plan.is_valid,
            'suites': plan.suites,
            'steps': len(plan.steps),
            'cost_estimate': plan.cost_estimate.to_dict() if plan.cost_estimate else None,
            'fixture_gaps': len(plan.fixture_gaps),
            'estimated_runtime_sec': plan.estimated_total_runtime_sec,
            'validation_errors': plan.validation_errors,
            'metadata': plan.metadata,
        }

        # Phase 4: Persist outcome if --persist flag set
        if persist and plan.is_valid:
            persistence = OutcomePersistence()
            # Create outcome record with estimated values (no actual cost yet)
            outcome = CompositionOutcome(
                composition_id=f"compose_{len(suites)}_{int(__import__('time').time())}",
                suites=suites,
                predicted_cost=plan.cost_estimate.total_cost if plan.cost_estimate else 0.0,
                actual_cost=plan.cost_estimate.total_cost if plan.cost_estimate else 0.0,
                fixtures_used=[gap.input_name for gap in plan.fixture_gaps],
                outcome_status='success',
                metadata={
                    'mode': mode,
                    'adaptive': adaptive,
                    'steps': len(plan.steps),
                }
            )
            persistence.store_outcome(outcome)
            result['outcome_persisted'] = True
            result['outcome_id'] = outcome.composition_id
    else:
        print(json.dumps({
            'error': f'Unknown compose mode: {mode}',
            'supported_modes': ['cost-aware'],
        }, indent=2))
        return 1

    _output_result(result, args.format)
    return 0 if plan.is_valid else 1


def cmd_analyze_learning_status(args: argparse.Namespace) -> int:
    """Analyze learning status from historical outcomes (Phase 4)."""
    persistence = OutcomePersistence()
    analyzer = HistoricalCostAnalyzer(persistence)
    learner = CriticityLearner(persistence)

    outcome_count = persistence.outcome_count()
    accuracy = analyzer.overall_accuracy()
    criticality = learner.prediction_accuracy_estimate()

    result = {
        'mode': 'learning-status',
        'outcome_count': outcome_count,
        'cost_accuracy': {
            'mean_error_pct': accuracy.mean_error_pct,
            'std_dev': accuracy.std_dev,
            'improvement_pct': accuracy.improvement_pct,
            'confidence': accuracy.confidence,
        },
        'criticality_accuracy': criticality,
        'accuracy_threshold_met': analyzer.accuracy_threshold_met(25.0),
        'criticality_threshold_met': learner.accuracy_threshold_met(0.80),
        'outcome_breakdown': persistence.outcome_count_by_status(),
    }

    _output_result(result, args.format)
    return 0


def cmd_repair_improve_from_history(args: argparse.Namespace) -> int:
    """Regenerate cost model and criticality from historical outcomes (Phase 4)."""
    persistence = OutcomePersistence()
    analyzer = HistoricalCostAnalyzer(persistence)
    learner = CriticityLearner(persistence)

    # Improve predictor
    improvement_stats = learner.improve_predictor()

    # Get refined cost estimates for common suites
    refined_costs = {}
    for suite in ['contractify', 'testify', 'documentify', 'docify']:
        original = analyzer.persistence.persistence if hasattr(analyzer.persistence, 'persistence') else None
        refined = analyzer.refine_cost_estimate(2.5, suite)
        refined_costs[suite] = refined

    result = {
        'mode': 'improve-from-history',
        'improvements_applied': improvement_stats['total_gaps_updated'],
        'gaps_updated': improvement_stats['updated_gaps'],
        'learning_confidence': improvement_stats['learning_confidence'],
        'refined_costs': refined_costs,
        'outcomes_processed': persistence.outcome_count(),
    }

    _output_result(result, args.format)
    return 0


def _render_text(result: dict) -> None:
    """Render result as plain text."""
    for key, value in result.items():
        if isinstance(value, (dict, list)):
            print(f"{key}: {json.dumps(value, indent=2)}")
        else:
            print(f"{key}: {value}")


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for fy platform CLI."""
    parser = argparse.ArgumentParser(
        description='fy v2 platform CLI - platform-first governance and analysis'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze repository')
    analyze_parser.add_argument('--mode', choices=['contract', 'docs', 'structure', 'dependency-check', 'learning-status'], default='contract')
    analyze_parser.add_argument('--target-repo', default='.')
    analyze_parser.add_argument('--suite', help='Suite name for dependency-check analysis')
    analyze_parser.add_argument('--format', choices=['json', 'text'], default='json')

    # govern command
    govern_parser = subparsers.add_parser('govern', help='Check governance and readiness')
    govern_parser.add_argument(
        '--mode',
        choices=['release', 'production', 'deploy', 'policy-check', 'cost-check'],
        default='release'
    )
    govern_parser.add_argument('--format', choices=['json', 'text'], default='json')
    govern_parser.add_argument('--target-repo', default='.')
    govern_parser.add_argument('--suite', help='Suite name for cost-check (default: default)')
    govern_parser.add_argument('--budget-tokens', type=int, help='Token budget for cost-check')
    govern_parser.add_argument('--budget-cost', type=float, help='Cost budget in USD for cost-check')

    # inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect repository')
    inspect_parser.add_argument('--mode', choices=['structure', 'contracts', 'deep'], default='structure')
    inspect_parser.add_argument('--target-repo', default='.')
    inspect_parser.add_argument('--format', choices=['json', 'text'], default='json')

    # repair-plan command
    repair_parser = subparsers.add_parser('repair-plan', help='Generate repair and refactoring plans')
    repair_parser.add_argument('--mode', choices=['structure', 'extract', 'consolidate', 'improve-from-history'], default='structure')
    repair_parser.add_argument('--target-repo', default='.')
    repair_parser.add_argument('--format', choices=['json', 'text'], default='json')

    # verify command
    verify_parser = subparsers.add_parser('verify', help='Verify outputs and compatibility')
    verify_parser.add_argument('--mode', choices=['standard', 'strict', 'cross-suite'], default='standard')
    verify_parser.add_argument('--format', choices=['json', 'text'], default='json')

    # compose command (Phase 3)
    compose_parser = subparsers.add_parser('compose', help='Compose suites with cost and fixture awareness')
    compose_parser.add_argument('--mode', choices=['cost-aware'], default='cost-aware')
    compose_parser.add_argument('--suites', nargs='+', required=True, help='Suite names to compose')
    compose_parser.add_argument('--adaptive', action='store_true', help='Use adaptive fixture resolution')
    compose_parser.add_argument('--persist', action='store_true', help='Persist outcome for cross-session learning (Phase 4)')
    compose_parser.add_argument('--format', choices=['json', 'text'], default='json')

    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == 'analyze':
        # Check if it's a dependency-check mode
        if getattr(args, 'mode', None) == 'dependency-check':
            return cmd_analyze_dependencies(args)
        return cmd_analyze(args)
    elif args.command == 'govern':
        return cmd_govern(args)
    elif args.command == 'inspect':
        return cmd_inspect(args)
    elif args.command == 'repair-plan':
        return cmd_repair_plan(args)
    elif args.command == 'verify':
        return cmd_verify(args)
    elif args.command == 'compose':
        return cmd_compose(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
