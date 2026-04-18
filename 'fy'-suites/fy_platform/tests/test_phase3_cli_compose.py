"""Test Phase 3 CLI integration: compose command."""

from __future__ import annotations

import json
import pytest

from fy_platform.tools import platform_cli


class TestPhase3ComposeCommand:
    """Test fy compose CLI command."""

    def test_compose_command_exists(self):
        """Compose command is registered."""
        try:
            platform_cli.main(['compose', '--help'])
        except SystemExit as e:
            # --help causes sys.exit(0)
            assert e.code == 0

    def test_compose_cost_aware_mode(self):
        """Compose with cost-aware mode."""
        result = platform_cli.main([
            'compose',
            '--mode', 'cost-aware',
            '--suites', 'contractify',
            '--format', 'json',
        ])
        assert result == 0

    def test_compose_multiple_suites(self):
        """Compose multiple suites."""
        result = platform_cli.main([
            'compose',
            '--suites', 'contractify', 'testify',
            '--format', 'json',
        ])
        assert result == 0

    def test_compose_with_adaptive_flag(self):
        """Compose with adaptive fixture resolution."""
        result = platform_cli.main([
            'compose',
            '--suites', 'contractify', 'testify',
            '--adaptive',
            '--format', 'json',
        ])
        assert result == 0

    def test_compose_no_suites_fails(self):
        """Compose without suites fails."""
        try:
            platform_cli.main([
                'compose',
                '--format', 'json',
            ])
            # Should not reach here
            assert False, "Expected SystemExit"
        except SystemExit as e:
            # argparse exits with code 2 for missing required args
            assert e.code == 2

    def test_compose_invalid_suite_fails(self):
        """Compose with invalid suite fails."""
        result = platform_cli.main([
            'compose',
            '--suites', 'nonexistent_suite',
            '--format', 'json',
        ])
        # Should fail validation
        assert result != 0


class TestPhase3IntegrationWithTools:
    """Test Phase 3 integration with tool layers."""

    def test_compose_imports_correctly(self):
        """Compose command imports required modules."""
        from fy_platform.ai.composition_plan import CompositionPlan
        from fy_platform.ai.cost_model_builder import CostModelBuilder
        from fy_platform.ai.adaptive_fixture_resolver import AdaptiveFixtureResolver

        planner = CompositionPlan()
        assert planner.cost_model is not None
        assert planner.fixture_resolver is not None

    def test_platform_cli_with_compose(self):
        """Platform CLI runs with compose command."""
        # Basic test that CLI accepts the command
        import sys
        from io import StringIO

        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            result = platform_cli.main([
                'compose',
                '--suites', 'contractify',
                '--format', 'json',
            ])
            output = sys.stdout.getvalue()
            assert result == 0
        finally:
            sys.stdout = old_stdout
