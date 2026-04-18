"""HistoricalCostAnalyzer: Refine cost estimates using real composition outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, stdev
from typing import Any

from fy_platform.ai.outcome_persistence import OutcomePersistence, CompositionOutcome


@dataclass
class CostAccuracy:
    """Measure of cost prediction accuracy."""
    suite: str | None = None  # None for overall accuracy
    total_samples: int = 0
    mean_error_pct: float = 0.0  # Mean absolute percentage error
    std_dev: float = 0.0
    improvement_pct: float = 0.0  # vs. baseline prediction
    confidence: float = 0.0  # 0.0-1.0, based on sample size
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class HistoricalCostAnalyzer:
    """Refine cost estimates using real composition outcomes.

    Compares phase3_predicted_cost vs. phase4_actual_cost.
    Calculates accuracy improvement %.
    Targets: ≥25% accuracy improvement when ≥20 outcomes exist.
    """

    def __init__(self, persistence: OutcomePersistence | None = None):
        """Initialize historical cost analyzer.

        Parameters
        ----------
        persistence : OutcomePersistence, optional
            Outcome persistence instance. Creates new if not provided.
        """
        self.persistence = persistence or OutcomePersistence()
        self.baseline_accuracy = 0.85  # Phase 3 baseline: 85% accurate
        self.learning_threshold = 20  # Outcomes needed for strong refinement
        self._cache: dict[str, Any] = {}

    def refine_cost_estimate(self, predicted_cost: float, suite: str | None = None) -> float:
        """Refine a cost estimate based on historical outcomes.

        Parameters
        ----------
        predicted_cost : float
            Predicted cost from Phase 3
        suite : str, optional
            Suite name for suite-specific refinement

        Returns
        -------
        float
            Refined cost estimate
        """
        # Load historical outcomes
        if suite:
            outcomes = self.persistence.outcomes_for_suite(suite, limit=100)
        else:
            outcomes = self.persistence.load_outcomes(limit=100)

        if len(outcomes) < 5:
            # Not enough data, return original
            return predicted_cost

        # Calculate average actual/predicted ratio
        ratios = []
        for outcome in outcomes:
            if outcome.predicted_cost > 0:
                ratio = outcome.actual_cost / outcome.predicted_cost
                ratios.append(ratio)

        if not ratios:
            return predicted_cost

        avg_ratio = mean(ratios)
        refined = predicted_cost * avg_ratio

        return refined

    def cost_accuracy_by_suite(self) -> dict[str, CostAccuracy]:
        """Calculate cost accuracy metrics for each suite.

        Returns
        -------
        dict[str, CostAccuracy]
            Accuracy metrics indexed by suite name
        """
        outcomes = self.persistence.load_outcomes(limit=1000)

        # Group by suite
        suite_outcomes: dict[str, list[CompositionOutcome]] = {}
        for outcome in outcomes:
            for suite in outcome.suites:
                if suite not in suite_outcomes:
                    suite_outcomes[suite] = []
                suite_outcomes[suite].append(outcome)

        # Calculate accuracy for each suite
        accuracies = {}
        for suite, suite_outc in suite_outcomes.items():
            acc = self._calculate_accuracy(suite_outc, suite)
            accuracies[suite] = acc

        return accuracies

    def overall_accuracy(self) -> CostAccuracy:
        """Calculate overall cost accuracy across all compositions.

        Returns
        -------
        CostAccuracy
            Overall accuracy metrics
        """
        outcomes = self.persistence.load_outcomes(limit=1000)
        if not outcomes:
            return CostAccuracy(total_samples=0)

        return self._calculate_accuracy(outcomes, None)

    def improve_by_dataset_size(self) -> dict[str, Any]:
        """Analyze improvement vs. dataset size.

        Returns
        -------
        dict[str, Any]
            Improvement metrics at different sample sizes
        """
        outcomes = self.persistence.load_outcomes(limit=1000)

        improvements = {}
        sample_sizes = [5, 10, 20, 50, 100, 200, 500]

        for sample_size in sample_sizes:
            if len(outcomes) < sample_size:
                continue

            sample = outcomes[:sample_size]
            accuracy = self._calculate_accuracy(sample, None)

            # Calculate improvement vs. baseline
            improvement = max(0, (accuracy.mean_error_pct - 15.0) / 15.0) * 100
            if improvement < 0:
                improvement = 0

            improvements[f'n={sample_size}'] = {
                'sample_count': sample_size,
                'mean_error_pct': accuracy.mean_error_pct,
                'improvement_vs_baseline_pct': improvement,
                'confidence': accuracy.confidence,
            }

        return improvements

    def accuracy_threshold_met(self, threshold: float = 25.0) -> bool:
        """Check if accuracy improvement threshold is met.

        Parameters
        ----------
        threshold : float, optional
            Improvement threshold in %. Default 25%.

        Returns
        -------
        bool
            True if ≥threshold outcomes exist and show improvement
        """
        outcome_count = self.persistence.outcome_count()
        if outcome_count < self.learning_threshold:
            return False

        accuracy = self.overall_accuracy()
        # Baseline is 85%, good improvement is 85 - 15 = 70% error
        # So improvement = baseline_error - current_error
        baseline_error = 15.0  # % error
        improvement = baseline_error - accuracy.mean_error_pct
        improvement_pct = (improvement / baseline_error) * 100 if baseline_error > 0 else 0

        return improvement_pct >= threshold

    def _calculate_accuracy(
        self,
        outcomes: list[CompositionOutcome],
        suite: str | None = None
    ) -> CostAccuracy:
        """Calculate accuracy for a set of outcomes.

        Parameters
        ----------
        outcomes : list[CompositionOutcome]
            Outcomes to analyze
        suite : str, optional
            Suite name for context

        Returns
        -------
        CostAccuracy
            Calculated accuracy
        """
        if not outcomes:
            return CostAccuracy(suite=suite, total_samples=0)

        # Calculate percentage errors
        errors = []
        for outcome in outcomes:
            if outcome.predicted_cost > 0:
                # Mean absolute percentage error (MAPE)
                error = abs(outcome.actual_cost - outcome.predicted_cost) / outcome.predicted_cost * 100
                errors.append(error)

        if not errors:
            return CostAccuracy(suite=suite, total_samples=len(outcomes))

        mean_error = mean(errors)
        std_dev = stdev(errors) if len(errors) > 1 else 0.0

        # Calculate confidence based on sample size
        # Grows from 0.0 to 1.0 as samples increase
        confidence = min(1.0, len(outcomes) / self.learning_threshold)

        # Calculate improvement vs. baseline accuracy
        baseline_error = 15.0  # Baseline is 85% accurate, so 15% error
        improvement = max(0, (baseline_error - mean_error) / baseline_error) * 100

        return CostAccuracy(
            suite=suite,
            total_samples=len(outcomes),
            mean_error_pct=mean_error,
            std_dev=std_dev,
            improvement_pct=improvement,
            confidence=confidence,
            metadata={
                'baseline_error_pct': baseline_error,
                'sample_count': len(outcomes),
            }
        )
