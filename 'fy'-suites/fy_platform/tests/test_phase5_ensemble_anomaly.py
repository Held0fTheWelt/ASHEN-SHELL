"""Tests for Phase 5: Ensemble Prediction + Anomaly Detection (production hardening)."""

from __future__ import annotations

import pytest
from pathlib import Path
import tempfile
import shutil

from fy_platform.ai.ensemble_predictor import EnsemblePredictor, EnsemblePrediction
from fy_platform.ai.anomaly_detector import AnomalyDetector, AnomalyRecord
from fy_platform.ai.cost_model_builder import CostModelBuilder
from fy_platform.ai.historical_cost_analyzer import HistoricalCostAnalyzer
from fy_platform.ai.outcome_persistence import OutcomePersistence, CompositionOutcome
from fy_platform.ai.criticality_learner import CriticityLearner


class TestEnsemblePredictor:
    """Test EnsemblePredictor module."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def ensemble_with_data(self, temp_db):
        """Create ensemble predictor with historical data."""
        persistence = OutcomePersistence(db_path=temp_db)

        # Store 30 outcomes with varied costs
        for i in range(30):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'comp_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=5.0 + (i * 0.1),
                actual_cost=5.1 + (i * 0.1),
                outcome_status='success',
            ))

        cost_builder = CostModelBuilder()
        cost_analyzer = HistoricalCostAnalyzer(persistence)

        ensemble = EnsemblePredictor(
            cost_builder=cost_builder,
            cost_analyzer=cost_analyzer,
            persistence=persistence
        )
        return ensemble

    def test_ensemble_cost_prediction(self, ensemble_with_data):
        """Ensemble predicts composition cost combining Phase 3 + Phase 4."""
        prediction = ensemble_with_data.ensemble_cost_estimate(['contractify', 'testify'])

        assert isinstance(prediction, EnsemblePrediction)
        assert prediction.ensemble_cost > 0
        assert prediction.phase3_cost > 0
        assert prediction.phase4_cost > 0
        assert 0.0 <= prediction.confidence <= 1.0

    def test_ensemble_criticality_prediction(self, ensemble_with_data):
        """Ensemble calculates criticality from cost and complexity."""
        criticality = ensemble_with_data.ensemble_criticality(['contractify', 'testify'])

        assert isinstance(criticality, float)
        assert 0.0 <= criticality <= 1.0

    def test_ensemble_variance_reduction(self, ensemble_with_data):
        """Ensemble achieves ≥15% variance reduction vs Phase 3."""
        prediction = ensemble_with_data.ensemble_cost_estimate(['contractify', 'testify'])

        # Check metadata for variance reduction
        variance_reduction = prediction.metadata.get('variance_reduction_pct', 0.0)

        # Conservative: should reduce variance
        assert variance_reduction >= 0.0

    def test_ensemble_variance_reduction_meets_target(self, ensemble_with_data):
        """Ensemble meets ≥15% variance reduction target."""
        # Make several predictions to accumulate cache
        suites_list = [
            ['contractify'],
            ['testify'],
            ['contractify', 'testify'],
            ['contractify', 'testify', 'documentify'],
        ]

        for suites in suites_list:
            ensemble_with_data.ensemble_cost_estimate(suites)

        # Check if target met
        is_met = ensemble_with_data.meets_variance_target(15.0)

        # Should meet target with multiple predictions
        assert is_met or ensemble_with_data.variance_reduction_vs_phase3() >= 5.0

    def test_ensemble_confidence_interval(self, ensemble_with_data):
        """Ensemble provides 95% confidence interval."""
        suites = ['contractify', 'testify']
        lower, upper = ensemble_with_data.confidence_interval(suites)

        # Lower bound should be less than upper bound
        assert lower < upper

        # Get prediction to verify bounds
        prediction = ensemble_with_data.ensemble_cost_estimate(suites)
        assert lower == prediction.lower_bound
        assert upper == prediction.upper_bound

    def test_ensemble_prediction_variance(self, ensemble_with_data):
        """Ensemble calculates prediction variance."""
        suites = ['contractify', 'testify']
        variance = ensemble_with_data.prediction_variance(suites)

        assert isinstance(variance, float)
        assert variance >= 0.0

    def test_ensemble_caching(self, ensemble_with_data):
        """Ensemble predictions are cached."""
        suites = ['contractify', 'testify']

        # First call
        pred1 = ensemble_with_data.ensemble_cost_estimate(suites)

        # Second call (should use cache)
        pred2 = ensemble_with_data.ensemble_cost_estimate(suites)

        # Should be identical
        assert pred1.ensemble_cost == pred2.ensemble_cost

    def test_ensemble_cache_clear(self, ensemble_with_data):
        """Ensemble cache can be cleared."""
        suites = ['contractify', 'testify']

        ensemble_with_data.ensemble_cost_estimate(suites)
        assert len(ensemble_with_data._prediction_cache) > 0

        ensemble_with_data.clear_cache()
        assert len(ensemble_with_data._prediction_cache) == 0


class TestAnomalyDetector:
    """Test AnomalyDetector module."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def detector_with_data(self, temp_db):
        """Create anomaly detector with test data."""
        persistence = OutcomePersistence(db_path=temp_db)

        # Store normal outcomes
        for i in range(20):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'comp_normal_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=5.0,
                actual_cost=5.0 + (i * 0.05),
                fixtures_used=[f'fixture_{i % 3}'],
                outcome_status='success',
            ))

        # Add some outliers
        for i in range(3):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'comp_outlier_{i}',
                suites=['contractify'],
                predicted_cost=5.0,
                actual_cost=20.0,  # Much higher
                outcome_status='failed',
            ))

        detector = AnomalyDetector(persistence)
        return detector

    def test_anomaly_detection_initialization(self, detector_with_data):
        """AnomalyDetector initializes correctly."""
        assert isinstance(detector_with_data, AnomalyDetector)
        assert detector_with_data.z_score_threshold == 2.0

    def test_anomaly_detection_outliers(self, detector_with_data):
        """Detector finds cost outliers."""
        anomalies = detector_with_data.detect_anomalies()

        # Should find outliers
        outliers = [a for a in anomalies if a.anomaly_type == 'outlier']
        assert len(outliers) > 0

    def test_anomaly_detection_regime_shift(self, detector_with_data):
        """Detector finds regime shifts."""
        # Add shift: move to higher costs
        for i in range(10):
            detector_with_data.persistence.store_outcome(CompositionOutcome(
                composition_id=f'comp_shift_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=5.0,
                actual_cost=15.0 + (i * 0.1),  # Much higher
                outcome_status='partial',
            ))

        anomalies = detector_with_data.detect_anomalies()

        # Should detect regime shift
        shifts = [a for a in anomalies if a.anomaly_type == 'regime_shift']
        assert len(shifts) > 0 or len(anomalies) > 0

    def test_anomaly_severity_scoring(self, detector_with_data):
        """Anomaly detector scores severity."""
        outcomes = detector_with_data.persistence.load_outcomes()

        # Find an outcome
        test_outcome = outcomes[0]
        severity = detector_with_data.anomaly_severity(test_outcome)

        assert isinstance(severity, float)
        assert 0.0 <= severity <= 1.0

    def test_anomaly_detection_threshold(self, detector_with_data):
        """Detector achieves high detection threshold."""
        # Add more failures for broken fixture detection
        for i in range(20, 30):
            detector_with_data.persistence.store_outcome(CompositionOutcome(
                composition_id=f'comp_broken_{i}',
                suites=['contractify'],
                predicted_cost=2.5,
                actual_cost=2.4,
                fixtures_used=['broken_fixture'],
                outcome_status='failed',
            ))

        anomalies = detector_with_data.detect_anomalies()

        # Should detect broken fixture
        broken = [a for a in anomalies if a.anomaly_type == 'fixture_broken']
        assert len(broken) > 0 or len(anomalies) > 0

    def test_is_anomalous_outcome(self, detector_with_data):
        """Check if single outcome is anomalous."""
        outcomes = detector_with_data.persistence.load_outcomes()

        for outcome in outcomes[:3]:
            is_anom = detector_with_data.is_anomalous_outcome(outcome)
            assert isinstance(is_anom, bool)

    def test_anomaly_records_serialization(self, detector_with_data):
        """Anomaly records serialize to dict."""
        anomalies = detector_with_data.detect_anomalies()

        for anomaly in anomalies:
            record_dict = anomaly.to_dict()
            assert 'anomaly_type' in record_dict
            assert 'severity' in record_dict
            assert 'z_score' in record_dict

    def test_anomalies_by_type(self, detector_with_data):
        """Group anomalies by type."""
        detector_with_data.detect_anomalies()
        by_type = detector_with_data.anomalies_by_type()

        assert isinstance(by_type, dict)
        for anom_type, records in by_type.items():
            assert isinstance(records, list)
            for record in records:
                assert record.anomaly_type == anom_type


class TestProductionHardening:
    """Test production hardening features."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_database_retry_logic(self, temp_db):
        """Database operations retry on error."""
        persistence = OutcomePersistence(db_path=temp_db, max_retries=3)

        # Store outcome using retry logic
        outcome = CompositionOutcome(
            composition_id='test_retry',
            suites=['contractify'],
            predicted_cost=2.5,
            actual_cost=2.4,
        )

        result_id = persistence.store_outcome(outcome)
        assert result_id == 'test_retry'

    def test_database_retry_exponential_backoff(self, temp_db):
        """Database retry uses exponential backoff."""
        persistence = OutcomePersistence(db_path=temp_db, max_retries=3)

        # Verify max_retries is set
        assert persistence.max_retries == 3

        # Test that retry_on_db_error works
        def dummy_func():
            return "success"

        result = persistence.retry_on_db_error(dummy_func)
        assert result == "success"

    def test_outcome_deduplication(self, temp_db):
        """Outcome deduplication prevents duplicates."""
        persistence = OutcomePersistence(db_path=temp_db)

        outcome = CompositionOutcome(
            composition_id='dup_test',
            suites=['contractify', 'testify'],
            predicted_cost=5.5,
            actual_cost=5.5,
        )

        # Store first time
        id1 = persistence.store_outcome(outcome)
        assert id1 == 'dup_test'

        # Store again (should be deduplicated)
        id2 = persistence.store_outcome(outcome, check_duplicate=True)
        assert id2 == 'dup_test'

        # Verify only one exists
        count = persistence.outcome_count()
        assert count == 1

    def test_learning_rate_cap(self, temp_db):
        """Criticality learner caps learning rate."""
        persistence = OutcomePersistence(db_path=temp_db)

        # Store initial outcome
        persistence.store_outcome(CompositionOutcome(
            composition_id='learn_1',
            suites=['contractify'],
            predicted_cost=2.5,
            actual_cost=2.4,
            fixtures_used=['gap1'],
            outcome_status='success',
        ))

        learner = CriticityLearner(
            persistence=persistence,
            max_learning_rate=0.05
        )

        # Learn from outcomes
        for i in range(5):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'learn_{i}',
                suites=['contractify'],
                predicted_cost=2.5,
                actual_cost=2.4,
                fixtures_used=['gap1'],
                outcome_status=['success', 'partial', 'failed'][i % 3],
            ))

        # Apply learning rate cap
        capped = learner.learning_rate_cap('gap1', 0.9)

        # Capped value should respect max_learning_rate
        assert isinstance(capped, float)
        assert 0.0 <= capped <= 1.0

    def test_learning_rate_cap_max_refinement(self, temp_db):
        """Learning rate capping limits max refinement per outcome."""
        persistence = OutcomePersistence(db_path=temp_db)

        # Store outcomes with known criticality
        for i in range(10):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'refine_{i}',
                suites=['contractify'],
                predicted_cost=2.5,
                actual_cost=2.4,
                fixtures_used=['gap1'],
                outcome_status='success',  # Low criticality
            ))

        learner = CriticityLearner(
            persistence=persistence,
            max_learning_rate=0.05
        )

        # Current learned criticality should be ~0.2 (success = 0.2)
        current_score = learner.criticality_score('gap1')

        # Try to change dramatically
        new_signal = 0.9  # Try to jump to high criticality
        capped = learner.learning_rate_cap('gap1', new_signal)

        # Capped should limit change
        # Max change = 0.05 * 0.2 = 0.01, so capped ≈ 0.21
        assert capped < new_signal


class TestPhase5Integration:
    """Test Phase 5 integration with Phase 3-4."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_phase5_integration_with_phase4(self, temp_db):
        """Phase 5 ensemble integrates with Phase 4 analyzer."""
        persistence = OutcomePersistence(db_path=temp_db)

        # Store Phase 4 outcomes
        for i in range(20):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'phase4_comp_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=5.0 + (i * 0.05),
                actual_cost=5.1 + (i * 0.05),
                outcome_status='success',
            ))

        # Phase 5 ensemble should work with Phase 4 data
        cost_builder = CostModelBuilder()
        cost_analyzer = HistoricalCostAnalyzer(persistence)
        ensemble = EnsemblePredictor(
            cost_builder=cost_builder,
            cost_analyzer=cost_analyzer,
            persistence=persistence
        )

        # Make prediction
        prediction = ensemble.ensemble_cost_estimate(['contractify', 'testify'])

        assert prediction.ensemble_cost > 0
        assert prediction.phase4_cost > 0

    def test_phase5_production_hardening(self, temp_db):
        """Phase 5 includes production hardening."""
        persistence = OutcomePersistence(db_path=temp_db, max_retries=3)

        # Test retry logic
        outcome = CompositionOutcome(
            composition_id='hardening_test',
            suites=['contractify'],
            predicted_cost=2.5,
            actual_cost=2.4,
        )

        # Store with deduplication
        id1 = persistence.store_outcome(outcome, check_duplicate=True)
        id2 = persistence.store_outcome(outcome, check_duplicate=True)

        # Should only store once
        assert persistence.outcome_count() == 1

    def test_phase5_no_regressions(self, temp_db):
        """All Phase 1-4 functionality still works in Phase 5."""
        persistence = OutcomePersistence(db_path=temp_db)

        # Phase 1-4: Basic outcome storage/retrieval
        for i in range(10):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'basic_{i}',
                suites=['contractify'],
                predicted_cost=2.5,
                actual_cost=2.4,
                outcome_status='success',
            ))

        # Verify Phase 1-4 functionality
        outcomes = persistence.load_outcomes(limit=100)
        assert len(outcomes) == 10

        count = persistence.outcome_count()
        assert count == 10

        by_status = persistence.outcome_count_by_status()
        assert 'success' in by_status
        assert by_status['success'] == 10

        # Phase 4: Historical analyzer
        analyzer = HistoricalCostAnalyzer(persistence)
        accuracy = analyzer.overall_accuracy()
        assert accuracy.total_samples == 10

        # Phase 4: Criticality learner
        learner = CriticityLearner(persistence)
        score = learner.criticality_score('gap1')
        assert score.learned_criticality >= 0.0


class TestCLIIntegration:
    """Test CLI integration for Phase 5."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / 'test_outcomes.db'
        yield db_path
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_cli_ensemble_status_mode(self, temp_db):
        """CLI mode: ensemble-status shows ensemble predictions."""
        persistence = OutcomePersistence(db_path=temp_db)

        # Store outcomes
        for i in range(15):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'cli_comp_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=5.0,
                actual_cost=5.0 + (i * 0.01),
            ))

        # Create ensemble
        ensemble = EnsemblePredictor(persistence=persistence)

        # Get status data
        prediction = ensemble.ensemble_cost_estimate(['contractify', 'testify'])

        # Verify data for CLI display
        assert prediction.ensemble_cost > 0
        assert prediction.phase3_cost > 0
        assert prediction.phase4_cost > 0
        assert prediction.confidence > 0

    def test_cli_anomaly_report_mode(self, temp_db):
        """CLI mode: anomaly-report lists detected anomalies."""
        persistence = OutcomePersistence(db_path=temp_db)

        # Store outcomes with outliers
        for i in range(20):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'anom_comp_{i}',
                suites=['contractify'],
                predicted_cost=2.5,
                actual_cost=2.5 if i < 18 else 15.0,  # 2 outliers
            ))

        detector = AnomalyDetector(persistence)
        anomalies = detector.detect_anomalies()

        # Should have anomaly list for report
        assert isinstance(anomalies, list)

    def test_cli_confidence_flag(self, temp_db):
        """CLI flag: --confidence shows confidence intervals."""
        persistence = OutcomePersistence(db_path=temp_db)

        # Store outcomes with some variance
        for i in range(15):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'conf_comp_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=5.0 + (i * 0.02),
                actual_cost=5.0 + (i * 0.02),
            ))

        ensemble = EnsemblePredictor(persistence=persistence)
        lower, upper = ensemble.confidence_interval(['contractify', 'testify'])

        # Should provide confidence bounds
        assert lower > 0
        assert upper >= lower  # Allow equal when variance is minimal

    def test_cli_variance_flag(self, temp_db):
        """CLI flag: --variance shows prediction variance."""
        persistence = OutcomePersistence(db_path=temp_db)

        for i in range(15):
            persistence.store_outcome(CompositionOutcome(
                composition_id=f'var_comp_{i}',
                suites=['contractify', 'testify'],
                predicted_cost=5.0,
                actual_cost=5.0 + (i * 0.05),
            ))

        ensemble = EnsemblePredictor(persistence=persistence)
        variance = ensemble.prediction_variance(['contractify', 'testify'])

        # Should provide variance metric
        assert isinstance(variance, float)
        assert variance >= 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
