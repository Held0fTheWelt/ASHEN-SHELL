"""CLI integration tests for Phase 4."""

from __future__ import annotations

import pytest
import json
import tempfile
import shutil
from pathlib import Path

from fy_platform.tools.platform_cli import (
    cmd_compose,
    cmd_analyze_learning_status,
    cmd_repair_improve_from_history,
    main,
)
from fy_platform.ai.outcome_persistence import OutcomePersistence, CompositionOutcome
import argparse


class TestCLIPersistFlag:
    """Test --persist flag on fy compose command."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_cli_persist_flag(self, temp_db, capsys, monkeypatch):
        """fy compose --persist stores outcome."""
        # Mock OutcomePersistence to use temp db
        import fy_platform.tools.platform_cli as cli_module

        original_persistence = cli_module.OutcomePersistence

        def mock_persistence(*args, **kwargs):
            return original_persistence(db_path=temp_db)

        monkeypatch.setattr(cli_module, 'OutcomePersistence', mock_persistence)

        # Run command with --persist
        args = argparse.Namespace(
            mode='cost-aware',
            suites=['contractify', 'testify'],
            adaptive=False,
            persist=True,
            format='json',
        )

        result = cmd_compose(args)
        assert result == 0

        # Check output
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output['ok'] is True
        assert output['outcome_persisted'] is True
        assert 'outcome_id' in output

    def test_cli_persist_flag_false(self, temp_db, capsys):
        """fy compose without --persist doesn't store."""
        args = argparse.Namespace(
            mode='cost-aware',
            suites=['contractify', 'testify'],
            adaptive=False,
            persist=False,
            format='json',
        )

        result = cmd_compose(args)
        assert result == 0

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output['ok'] is True
        assert 'outcome_persisted' not in output or output.get('outcome_persisted') is False


class TestCLILearningStatusMode:
    """Test 'fy analyze --mode learning-status' command."""

    @pytest.fixture
    def populated_db(self):
        """Create database with outcomes."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        persistence = OutcomePersistence(db_path=db_path)

        # Store some outcomes
        for i in range(25):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'test_comp_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=5.0 + i * 0.1,
                actual_cost=5.0 + i * 0.1 - 0.3,
                outcome_status='success',
            ))

        yield db_path

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_cli_learning_status_mode(self, populated_db, capsys, monkeypatch):
        """fy analyze --mode learning-status shows accuracy metrics."""
        import fy_platform.tools.platform_cli as cli_module

        original_persistence = cli_module.OutcomePersistence

        def mock_persistence(*args, **kwargs):
            return original_persistence(db_path=populated_db)

        monkeypatch.setattr(cli_module, 'OutcomePersistence', mock_persistence)

        args = argparse.Namespace(
            mode='learning-status',
            target_repo='.',
            format='json',
        )

        result = cmd_analyze_learning_status(args)
        assert result == 0

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output['mode'] == 'learning-status'
        assert output['outcome_count'] == 25
        assert 'cost_accuracy' in output
        assert 'criticality_accuracy' in output

    def test_cli_learning_status_with_no_outcomes(self, capsys, monkeypatch):
        """fy analyze --mode learning-status works with no outcomes."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'empty.db'

        import fy_platform.tools.platform_cli as cli_module

        original_persistence = cli_module.OutcomePersistence

        def mock_persistence(*args, **kwargs):
            return original_persistence(db_path=db_path)

        monkeypatch.setattr(cli_module, 'OutcomePersistence', mock_persistence)

        args = argparse.Namespace(
            mode='learning-status',
            target_repo='.',
            format='json',
        )

        result = cmd_analyze_learning_status(args)
        assert result == 0

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output['outcome_count'] == 0

        shutil.rmtree(temp_dir, ignore_errors=True)


class TestCLIImproveFromHistoryMode:
    """Test 'fy repair-plan --mode improve-from-history' command."""

    @pytest.fixture
    def learning_db(self):
        """Create database with enough data for learning."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        persistence = OutcomePersistence(db_path=db_path)

        # Store outcomes with various gaps
        gaps = ['missing_project_root', 'missing_contracts_json']
        for i in range(30):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'learn_comp_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=5.0,
                actual_cost=4.95,
                fixtures_used=[gaps[i % 2]],
                outcome_status='success' if i % 2 == 0 else 'failed',
            ))

        yield db_path

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_cli_improve_from_history_mode(self, learning_db, capsys, monkeypatch):
        """fy repair-plan --mode improve-from-history refines models."""
        import fy_platform.tools.platform_cli as cli_module

        original_persistence = cli_module.OutcomePersistence

        def mock_persistence(*args, **kwargs):
            return original_persistence(db_path=learning_db)

        monkeypatch.setattr(cli_module, 'OutcomePersistence', mock_persistence)

        args = argparse.Namespace(
            mode='improve-from-history',
            target_repo='.',
            format='json',
        )

        result = cmd_repair_improve_from_history(args)
        assert result == 0

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output['mode'] == 'improve-from-history'
        assert 'improvements_applied' in output
        assert 'outcomes_processed' in output


class TestCLIMainIntegration:
    """Test main() CLI entry point."""

    def test_main_compose_with_persist(self, capsys, monkeypatch, tmp_path):
        """Main entry point handles compose --persist."""
        import fy_platform.tools.platform_cli as cli_module

        db_path = tmp_path / 'test.db'
        original_persistence = cli_module.OutcomePersistence

        def mock_persistence(*args, **kwargs):
            return original_persistence(db_path=db_path)

        monkeypatch.setattr(cli_module, 'OutcomePersistence', mock_persistence)

        # Call main with compose command
        argv = [
            'compose',
            '--suites', 'contractify', 'testify',
            '--persist',
            '--format', 'json',
        ]

        result = main(argv)
        assert result == 0

    def test_main_analyze_learning_status(self, capsys, monkeypatch, tmp_path):
        """Main entry point handles analyze --mode learning-status."""
        import fy_platform.tools.platform_cli as cli_module

        db_path = tmp_path / 'test.db'
        original_persistence = cli_module.OutcomePersistence

        def mock_persistence(*args, **kwargs):
            return original_persistence(db_path=db_path)

        monkeypatch.setattr(cli_module, 'OutcomePersistence', mock_persistence)

        argv = [
            'analyze',
            '--mode', 'learning-status',
            '--format', 'json',
        ]

        result = main(argv)
        assert result == 0

    def test_main_repair_improve_from_history(self, capsys, monkeypatch, tmp_path):
        """Main entry point handles repair-plan --mode improve-from-history."""
        import fy_platform.tools.platform_cli as cli_module

        db_path = tmp_path / 'test.db'
        original_persistence = cli_module.OutcomePersistence

        def mock_persistence(*args, **kwargs):
            return original_persistence(db_path=db_path)

        monkeypatch.setattr(cli_module, 'OutcomePersistence', mock_persistence)

        argv = [
            'repair-plan',
            '--mode', 'improve-from-history',
            '--format', 'json',
        ]

        result = main(argv)
        assert result == 0
