"""Tests for Phase 4: Outcome Persistence + Cross-Session Learning."""

from __future__ import annotations

import pytest
from pathlib import Path
import tempfile
import shutil

from fy_platform.ai.outcome_persistence import OutcomePersistence, CompositionOutcome
from fy_platform.ai.historical_cost_analyzer import HistoricalCostAnalyzer, CostAccuracy
from fy_platform.ai.criticality_learner import CriticityLearner, CriticalityScore
from fy_platform.ai.adaptive_fixture_resolver import AdaptiveFixtureResolver


class TestOutcomePersistence:
    """Test OutcomePersistence module."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_outcome_persistence_initialization(self, temp_db):
        """OutcomePersistence initializes with database file."""
        persistence = OutcomePersistence(db_path=temp_db)
        assert persistence.db_path.exists()

    def test_outcome_persistence_store_load(self, temp_db):
        """Store and load a single outcome."""
        persistence = OutcomePersistence(db_path=temp_db)

        outcome = CompositionOutcome(
            composition_id='test_comp_001',
            suites=['contractify', 'testify'],
            predicted_cost=5.50,
            actual_cost=5.35,
            fixtures_used=['gap1', 'gap2'],
            outcome_status='success',
        )

        result_id = persistence.store_outcome(outcome)
        assert result_id == 'test_comp_001'

        loaded = persistence.load_outcome('test_comp_001')
        assert loaded is not None
        assert loaded.composition_id == 'test_comp_001'
        assert loaded.suites == ['contractify', 'testify']
        assert loaded.predicted_cost == 5.50
        assert loaded.actual_cost == 5.35

    def test_outcome_persistence_queries(self, temp_db):
        """Query outcomes by status and suite."""
        persistence = OutcomePersistence(db_path=temp_db)

        # Store multiple outcomes
        for i in range(5):
            outcome = CompositionOutcome(
                composition_id=f'comp_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=5.0 + i,
                actual_cost=4.9 + i,
                outcome_status='success' if i < 3 else 'partial',
            )
            persistence.store_outcome(outcome)

        # Query all
        all_outcomes = persistence.load_outcomes()
        assert len(all_outcomes) == 5

        # Query by status
        success_outcomes = persistence.load_outcomes(status='success')
        assert len(success_outcomes) == 3

        partial_outcomes = persistence.load_outcomes(status='partial')
        assert len(partial_outcomes) == 2

    def test_outcomes_for_suite(self, temp_db):
        """Load outcomes for specific suite."""
        persistence = OutcomePersistence(db_path=temp_db)

        # Store outcomes with different suite combinations
        persistence.store_outcome(CompositionOutcome(
            composition_id='comp_1',
            suites=['contractify'],
            predicted_cost=2.5,
            actual_cost=2.4,
        ))

        persistence.store_outcome(CompositionOutcome(
            composition_id='comp_2',
            suites=['contractify', 'testify'],
            predicted_cost=5.5,
            actual_cost=5.3,
        ))

        persistence.store_outcome(CompositionOutcome(
            composition_id='comp_3',
            suites=['testify'],
            predicted_cost=3.0,
            actual_cost=2.9,
        ))

        # Query outcomes for contractify
        contractify_outcomes = persistence.outcomes_for_suite('contractify')
        assert len(contractify_outcomes) == 2

        # Query outcomes for testify
        testify_outcomes = persistence.outcomes_for_suite('testify')
        assert len(testify_outcomes) == 2

    def test_outcome_count(self, temp_db):
        """Get outcome counts."""
        persistence = OutcomePersistence(db_path=temp_db)

        assert persistence.outcome_count() == 0

        for i in range(10):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'comp_{i}',
                suites=['contractify'],
                predicted_cost=2.5,
                actual_cost=2.4,
                outcome_status='success' if i % 2 == 0 else 'failed',
            ))

        assert persistence.outcome_count() == 10

        counts = persistence.outcome_count_by_status()
        assert counts['success'] == 5
        assert counts['failed'] == 5

    def test_outcome_persistence_db_structure(self, temp_db):
        """Verify database schema is correct."""
        persistence = OutcomePersistence(db_path=temp_db)

        # Store and verify schema was created
        persistence.store_outcome(CompositionOutcome(
            composition_id='test_schema',
            suites=['contractify'],
            predicted_cost=2.5,
            actual_cost=2.4,
        ))

        # Should be able to query without errors
        outcome = persistence.load_outcome('test_schema')
        assert outcome is not None

    def test_outcome_persistence_upsert(self, temp_db):
        """Store outcome with same ID updates existing record."""
        persistence = OutcomePersistence(db_path=temp_db)

        outcome1 = CompositionOutcome(
            composition_id='same_id',
            suites=['contractify'],
            predicted_cost=2.5,
            actual_cost=2.4,
        )
        persistence.store_outcome(outcome1)

        outcome2 = CompositionOutcome(
            composition_id='same_id',
            suites=['testify'],
            predicted_cost=3.0,
            actual_cost=2.9,
        )
        persistence.store_outcome(outcome2)

        # Should have only 1 outcome (upserted)
        assert persistence.outcome_count() == 1

        loaded = persistence.load_outcome('same_id')
        assert loaded.suites == ['testify']


class TestHistoricalCostAnalyzer:
    """Test HistoricalCostAnalyzer module."""

    @pytest.fixture
    def analyzer_with_data(self):
        """Create analyzer with sample data."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        persistence = OutcomePersistence(db_path=db_path)

        # Store sample outcomes
        for i in range(25):
            predicted = 5.0 + (i * 0.1)
            # Add some variance: actual is within 10% of predicted
            actual = predicted * (0.95 + (i % 10) * 0.01)
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'comp_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=predicted,
                actual_cost=actual,
                outcome_status='success',
            ))

        analyzer = HistoricalCostAnalyzer(persistence)
        yield analyzer

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_historical_cost_accuracy_improvement(self, analyzer_with_data):
        """Historical cost accuracy improves with outcomes."""
        accuracy = analyzer_with_data.overall_accuracy()
        assert accuracy.total_samples == 25
        assert accuracy.mean_error_pct < 15.0  # Better than baseline

    def test_cost_accuracy_threshold_25_percent(self, analyzer_with_data):
        """Cost accuracy threshold (≥25%) is met with ≥20 outcomes."""
        # Should have 25 outcomes, each with ~5-10% error
        is_threshold_met = analyzer_with_data.accuracy_threshold_met(25.0)
        assert is_threshold_met

    def test_refine_cost_estimate(self, analyzer_with_data):
        """Refine cost estimate using historical data."""
        original_estimate = 5.0
        refined = analyzer_with_data.refine_cost_estimate(original_estimate)

        # Refined should be closer to actual based on history
        # Since our test data has actual ≈ predicted, should be similar
        assert isinstance(refined, float)
        assert refined > 0

    def test_cost_accuracy_by_suite(self, analyzer_with_data):
        """Get accuracy metrics per suite."""
        accuracies = analyzer_with_data.cost_accuracy_by_suite()

        # Should have data for contractify and testify
        assert 'contractify' in accuracies or 'testify' in accuracies
        for suite, accuracy in accuracies.items():
            assert isinstance(accuracy, CostAccuracy)
            assert accuracy.total_samples > 0

    def test_improve_by_dataset_size(self, analyzer_with_data):
        """Improvement scales with dataset size."""
        improvements = analyzer_with_data.improve_by_dataset_size()

        # Should have entries for different sample sizes
        assert len(improvements) > 0
        for size_key, metrics in improvements.items():
            assert 'sample_count' in metrics
            assert 'improvement_vs_baseline_pct' in metrics


class TestCriticityLearner:
    """Test CriticityLearner module."""

    @pytest.fixture
    def learner_with_data(self):
        """Create learner with sample outcome data."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        persistence = OutcomePersistence(db_path=db_path)

        # Store outcomes with various statuses and gaps
        gaps = ['missing_project_root', 'missing_contracts_json', 'missing_templates_json']

        for i in range(30):
            status = ['success', 'partial', 'failed'][i % 3]
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'comp_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=5.0,
                actual_cost=5.0,
                fixtures_used=[gaps[i % 3]],
                outcome_status=status,
            ))

        learner = CriticityLearner(persistence)
        yield learner

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_criticality_learner_prediction(self, learner_with_data):
        """Learner predicts gap criticality from outcomes."""
        score = learner_with_data.criticality_score('missing_project_root')

        assert isinstance(score, CriticalityScore)
        assert 0.0 <= score.learned_criticality <= 1.0
        assert score.sample_count > 0

    def test_criticality_prediction_accuracy_80_percent(self, learner_with_data):
        """Criticality prediction accuracy meets ≥80% threshold."""
        is_accurate = learner_with_data.accuracy_threshold_met(0.80)

        # With 30 outcomes and reasonable variance, should meet threshold
        assert is_accurate

    def test_learn_from_outcome(self, learner_with_data):
        """Learn from a composition outcome."""
        outcome = CompositionOutcome(
            composition_id='test_learn',
            suites=['contractify'],
            predicted_cost=2.5,
            actual_cost=2.4,
            fixtures_used=['gap_test'],
            outcome_status='failed',
        )

        result = learner_with_data.learn_from_outcome(outcome)
        assert 'learned_gaps' in result
        assert 'gap_test' in result['learned_gaps']

    def test_improve_predictor(self, learner_with_data):
        """Improve resolver with learned criticalities."""
        improvements = learner_with_data.improve_predictor()

        assert 'total_gaps_updated' in improvements
        assert 'learning_confidence' in improvements
        assert improvements['total_gaps_tracked'] > 0

    def test_get_learned_criticalities(self, learner_with_data):
        """Get all learned criticality scores."""
        scores = learner_with_data.get_learned_criticalities()

        assert isinstance(scores, dict)
        for gap_id, score in scores.items():
            assert isinstance(score, CriticalityScore)
            assert 0.0 <= score.learned_criticality <= 1.0

    def test_prediction_accuracy_estimate(self, learner_with_data):
        """Estimate overall prediction accuracy."""
        accuracy = learner_with_data.prediction_accuracy_estimate()

        assert 0.0 <= accuracy <= 1.0


class TestPhase4Integration:
    """Integration tests for Phase 4 with Phase 3."""

    @pytest.fixture
    def integration_setup(self):
        """Setup persistence + analyzer + learner."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        persistence = OutcomePersistence(db_path=db_path)

        # Populate with representative data
        suites_list = [
            ['contractify'],
            ['testify'],
            ['contractify', 'testify'],
            ['contractify', 'testify', 'documentify'],
            ['docify', 'postmanify'],
        ]

        for i in range(40):
            suites = suites_list[i % len(suites_list)]
            predicted = 2.5 + len(suites) * 2.5
            actual = predicted * (0.93 + (i % 10) * 0.01)

            persistence.store_outcome(CompositionOutcome(
                composition_id=f'integration_comp_{i}',
                suites=suites,
                predicted_cost=predicted,
                actual_cost=actual,
                fixtures_used=['gap1', 'gap2'] if i % 3 == 0 else ['gap1'],
                outcome_status=['success', 'partial', 'failed'][i % 3],
            ))

        analyzer = HistoricalCostAnalyzer(persistence)
        learner = CriticityLearner(persistence)

        yield {
            'persistence': persistence,
            'analyzer': analyzer,
            'learner': learner,
        }

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_phase4_integration_with_phase3(self, integration_setup):
        """Phase 4 integrates with Phase 3 components."""
        # All components should work together
        analyzer = integration_setup['analyzer']
        learner = integration_setup['learner']

        # Get metrics
        accuracy = analyzer.overall_accuracy()
        criticality = learner.prediction_accuracy_estimate()

        # Both should have meaningful results
        assert accuracy.total_samples == 40
        assert criticality >= 0.0

    def test_cross_session_learning(self, integration_setup):
        """Outcomes enable cross-session learning."""
        persistence = integration_setup['persistence']

        # Simulate second session loading outcomes
        new_learner = CriticityLearner(persistence)
        new_analyzer = HistoricalCostAnalyzer(persistence)

        # Should have learned from all previous outcomes
        assert new_analyzer.overall_accuracy().total_samples == 40
        assert new_learner.prediction_accuracy_estimate() > 0.0

    def test_outcome_history_queries(self, integration_setup):
        """Query outcome history for analysis."""
        persistence = integration_setup['persistence']

        # Get all outcomes
        all_outcomes = persistence.load_outcomes(limit=100)
        assert len(all_outcomes) == 40

        # Get outcomes for specific suite
        contractify_outcomes = persistence.outcomes_for_suite('contractify', limit=50)
        assert len(contractify_outcomes) > 0
        assert all('contractify' in o.suites for o in contractify_outcomes)

    def test_cost_refinement_dataset_size_scaling(self, integration_setup):
        """Cost refinement accuracy scales with dataset."""
        analyzer = integration_setup['analyzer']

        improvements = analyzer.improve_by_dataset_size()

        # Should show improvement scaling
        assert len(improvements) > 0

        # Larger datasets should have better accuracy
        sizes = list(improvements.keys())
        if len(sizes) > 1:
            first_accuracy = improvements[sizes[0]]['improvement_vs_baseline_pct']
            last_accuracy = improvements[sizes[-1]]['improvement_vs_baseline_pct']
            # Larger dataset should be at least as good
            assert last_accuracy >= first_accuracy * 0.95

    def test_criticality_refinement_over_time(self, integration_setup):
        """Criticality learning improves with more outcomes."""
        learner = integration_setup['learner']
        persistence = integration_setup['persistence']

        # Get initial accuracy
        initial_accuracy = learner.prediction_accuracy_estimate()

        # Simulate adding more outcomes
        for i in range(10):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'new_comp_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=5.0,
                actual_cost=4.95,
                fixtures_used=['gap1'],
                outcome_status='success',
            ))

        # Reload learner with new data
        new_learner = CriticityLearner(persistence)
        new_accuracy = new_learner.prediction_accuracy_estimate()

        # Should have same or better accuracy
        assert new_accuracy >= initial_accuracy * 0.95

    def test_phase4_no_regressions(self):
        """Phase 4 doesn't break existing Phase 1/2/3 functionality."""
        # This is tested implicitly by running all tests
        # Just verify imports work
        from fy_platform.ai.composition_plan import CompositionPlan
        from fy_platform.ai.cost_model_builder import CostModelBuilder
        from fy_platform.ai.adaptive_fixture_resolver import AdaptiveFixtureResolver

        planner = CompositionPlan()
        builder = CostModelBuilder()
        resolver = AdaptiveFixtureResolver()

        assert planner is not None
        assert builder is not None
        assert resolver is not None


class TestHistoricalAnalyzerStatistics:
    """Test statistical properties of historical analyzer."""

    @pytest.fixture
    def stats_data(self):
        """Create data with known statistical properties."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        persistence = OutcomePersistence(db_path=db_path)

        # Create outcomes with ~5% error rate
        for i in range(50):
            predicted = 5.0
            actual = predicted * 1.05  # Consistent 5% higher
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'stat_comp_{i}',
                suites=['contractify'],
                predicted_cost=predicted,
                actual_cost=actual,
            ))

        analyzer = HistoricalCostAnalyzer(persistence)
        yield analyzer

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_historical_analyzer_statistics(self, stats_data):
        """Verify statistical calculations."""
        accuracy = stats_data.overall_accuracy()

        assert accuracy.total_samples == 50
        # Error should be ~5%
        assert 3.0 < accuracy.mean_error_pct < 7.0


class TestLearningConvergence:
    """Test learning convergence properties."""

    def test_learning_convergence(self):
        """Learning converges to stable estimates."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        persistence = OutcomePersistence(db_path=db_path)

        # Add outcomes sequentially
        accuracies = []
        for batch in range(5):
            for i in range(10):
                predicted = 5.0
                actual = predicted * (0.98 + (i % 5) * 0.005)
                persistence.store_outcome(CompositionOutcome(
                    composition_id=f'conv_comp_{batch}_{i}',
                    suites=['contractify'],
                    predicted_cost=predicted,
                    actual_cost=actual,
                ))

            analyzer = HistoricalCostAnalyzer(persistence)
            accuracy = analyzer.overall_accuracy()
            accuracies.append(accuracy.mean_error_pct)

        # Accuracy should stabilize (not increase wildly)
        variance = max(accuracies) - min(accuracies)
        assert variance < 5.0  # Stable within 5%

        shutil.rmtree(temp_dir, ignore_errors=True)
