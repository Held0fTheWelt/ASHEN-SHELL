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
    else:
        print(json.dumps({
            'error': f'Unknown analyze mode: {mode}',
            'supported_modes': ['contract', 'docs', 'structure'],
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


def _output_result(result: dict, fmt: str) -> None:
    """Output result in specified format."""
    if fmt == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif fmt == 'text':
        _render_text(result)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


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
    analyze_parser.add_argument('--mode', choices=['contract', 'docs', 'structure'], default='contract')
    analyze_parser.add_argument('--target-repo', default='.')
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
    repair_parser.add_argument('--mode', choices=['structure', 'extract', 'consolidate'], default='structure')
    repair_parser.add_argument('--target-repo', default='.')
    repair_parser.add_argument('--format', choices=['json', 'text'], default='json')

    # verify command
    verify_parser = subparsers.add_parser('verify', help='Verify outputs and compatibility')
    verify_parser.add_argument('--mode', choices=['standard', 'strict', 'cross-suite'], default='standard')
    verify_parser.add_argument('--format', choices=['json', 'text'], default='json')

    args = parser.parse_args(list(argv) if argv is not None else None)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == 'analyze':
        return cmd_analyze(args)
    elif args.command == 'govern':
        return cmd_govern(args)
    elif args.command == 'inspect':
        return cmd_inspect(args)
    elif args.command == 'repair-plan':
        return cmd_repair_plan(args)
    elif args.command == 'verify':
        return cmd_verify(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
