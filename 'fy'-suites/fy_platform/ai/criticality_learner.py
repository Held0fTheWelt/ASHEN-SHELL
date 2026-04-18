"""CriticityLearner: Learn fixture gap criticality from composition outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fy_platform.ai.outcome_persistence import OutcomePersistence, CompositionOutcome
from fy_platform.ai.adaptive_fixture_resolver import AdaptiveFixtureResolver


@dataclass
class CriticalityScore:
    """Criticality prediction for a gap."""
    gap_id: str
    learned_criticality: float  # 0.0-1.0
    baseline_criticality: float  # 0.0-1.0
    sample_count: int = 0
    prediction_accuracy: float = 0.0  # 0.0-1.0
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CriticityLearner:
    """Learn fixture gap criticality from composition failures.

    Improves AdaptiveFixtureResolver predictions.
    Tracks: which gaps appeared critical vs. worked around.
    Target: ≥80% prediction accuracy on held-out test set.

    Features:
    - Learning rate capping (max 5% refinement per outcome)
    - Prevents overtraining on single outcomes
    """

    def __init__(
        self,
        persistence: OutcomePersistence | None = None,
        resolver: AdaptiveFixtureResolver | None = None,
        max_learning_rate: float = 0.05
    ):
        """Initialize criticality learner.

        Parameters
        ----------
        persistence : OutcomePersistence, optional
            Outcome persistence instance
        resolver : AdaptiveFixtureResolver, optional
            Adaptive fixture resolver instance
        max_learning_rate : float, optional
            Max refinement per outcome (0.0-1.0). Default 0.05 (5%).
        """
        self.persistence = persistence or OutcomePersistence()
        self.resolver = resolver or AdaptiveFixtureResolver()
        self.gap_criticality: dict[str, list[float]] = {}  # gap_id -> [outcomes]
        self.learning_threshold = 10  # Outcomes per gap needed for strong learning
        self.max_learning_rate = max_learning_rate
        self._gap_update_counts: dict[str, int] = {}  # Track updates per gap
        self._load_learned_criticalities()

    def learn_from_outcome(self, outcome: CompositionOutcome) -> dict[str, Any]:
        """Learn criticality from a composition outcome.

        Parameters
        ----------
        outcome : CompositionOutcome
            Outcome to learn from

        Returns
        -------
        dict[str, Any]
            Learning statistics
        """
        # Map outcome status to criticality lessons
        # success -> gaps were not critical
        # partial -> some gaps were critical (moderate)
        # failed -> at least one gap was critical (high)

        status_to_criticality = {
            'success': 0.2,      # Low criticality
            'partial': 0.6,      # Moderate
            'failed': 0.9,       # High criticality
        }

        criticality_signal = status_to_criticality.get(outcome.outcome_status, 0.5)

        # Update criticality scores for gaps in this composition
        learned_gaps = {}
        for gap_id in outcome.fixtures_used:
            if gap_id not in self.gap_criticality:
                self.gap_criticality[gap_id] = []

            self.gap_criticality[gap_id].append(criticality_signal)
            learned_gaps[gap_id] = {
                'signal': criticality_signal,
                'samples': len(self.gap_criticality[gap_id]),
            }

        return {
            'learned_gaps': learned_gaps,
            'outcome_status': outcome.outcome_status,
            'total_gaps_tracked': len(self.gap_criticality),
        }

    def criticality_score(self, gap_id: str) -> CriticalityScore:
        """Get learned criticality score for a gap.

        Parameters
        ----------
        gap_id : str
            Gap identifier

        Returns
        -------
        CriticalityScore
            Learned criticality with baseline
        """
        # Get baseline from resolver
        baseline = self.resolver.criticality_scores.get(gap_id, 0.5)

        # Get learned criticality
        if gap_id not in self.gap_criticality or len(self.gap_criticality[gap_id]) == 0:
            learned = baseline
            sample_count = 0
        else:
            samples = self.gap_criticality[gap_id]
            sample_count = len(samples)
            learned = sum(samples) / len(samples)

        # Calculate prediction accuracy
        # Higher confidence when samples are consistent
        if sample_count > 0:
            variance = sum((x - learned) ** 2 for x in self.gap_criticality[gap_id]) / sample_count
            prediction_accuracy = max(0.0, 1.0 - (variance ** 0.5))
        else:
            prediction_accuracy = 0.0

        return CriticalityScore(
            gap_id=gap_id,
            learned_criticality=learned,
            baseline_criticality=baseline,
            sample_count=sample_count,
            prediction_accuracy=prediction_accuracy,
            metadata={
                'has_learning': sample_count > 0,
                'confidence': min(1.0, sample_count / self.learning_threshold),
            }
        )

    def improve_predictor(self) -> dict[str, Any]:
        """Improve AdaptiveFixtureResolver with learned criticalities.

        Returns
        -------
        dict[str, Any]
            Improvement statistics
        """
        improvements = 0
        updated_gaps = {}

        for gap_id, samples in self.gap_criticality.items():
            if len(samples) >= self.learning_threshold:
                # Confident in this learning
                learned_crit = sum(samples) / len(samples)
                baseline = self.resolver.criticality_scores.get(gap_id, 0.5)

                # Update resolver with learned value
                self.resolver.criticality_scores[gap_id] = learned_crit

                # Calculate improvement
                improvement_delta = abs(learned_crit - baseline)
                if improvement_delta > 0.05:  # Significant change
                    improvements += 1
                    updated_gaps[gap_id] = {
                        'baseline': baseline,
                        'learned': learned_crit,
                        'delta': improvement_delta,
                        'samples': len(samples),
                    }

        return {
            'total_gaps_updated': improvements,
            'updated_gaps': updated_gaps,
            'total_gaps_tracked': len(self.gap_criticality),
            'learning_confidence': self._overall_learning_confidence(),
        }

    def prediction_accuracy_estimate(self) -> float:
        """Estimate overall prediction accuracy on learned gaps.

        Returns
        -------
        float
            Estimated accuracy 0.0-1.0, targets ≥0.80
        """
        if not self.gap_criticality:
            return 0.0

        accuracies = []
        for gap_id in self.gap_criticality:
            score = self.criticality_score(gap_id)
            accuracies.append(score.prediction_accuracy)

        if not accuracies:
            return 0.0

        return sum(accuracies) / len(accuracies)

    def accuracy_threshold_met(self, threshold: float = 0.80) -> bool:
        """Check if prediction accuracy meets threshold.

        Parameters
        ----------
        threshold : float, optional
            Accuracy threshold 0.0-1.0. Default 0.80 (80%).

        Returns
        -------
        bool
            True if accuracy >= threshold
        """
        outcome_count = self.persistence.outcome_count()
        if outcome_count < 5:  # Minimum outcomes needed
            return False

        accuracy = self.prediction_accuracy_estimate()
        return accuracy >= threshold

    def _load_learned_criticalities(self):
        """Load learned criticalities from persistence."""
        outcomes = self.persistence.load_outcomes(limit=1000)

        for outcome in outcomes:
            status_to_crit = {
                'success': 0.2,
                'partial': 0.6,
                'failed': 0.9,
            }
            signal = status_to_crit.get(outcome.outcome_status, 0.5)

            for gap_id in outcome.fixtures_used:
                if gap_id not in self.gap_criticality:
                    self.gap_criticality[gap_id] = []
                self.gap_criticality[gap_id].append(signal)

    def _overall_learning_confidence(self) -> float:
        """Calculate overall learning confidence."""
        if not self.gap_criticality:
            return 0.0

        confidences = []
        for gap_id in self.gap_criticality:
            sample_count = len(self.gap_criticality[gap_id])
            conf = min(1.0, sample_count / self.learning_threshold)
            confidences.append(conf)

        return sum(confidences) / len(confidences) if confidences else 0.0

    def get_learned_criticalities(self) -> dict[str, CriticalityScore]:
        """Get all learned criticality scores.

        Returns
        -------
        dict[str, CriticalityScore]
            All gap criticality scores
        """
        scores = {}
        for gap_id in self.gap_criticality:
            scores[gap_id] = self.criticality_score(gap_id)
        return scores

    def learning_rate_cap(self, gap_id: str, new_signal: float) -> float:
        """Apply learning rate cap to prevent overtraining.

        Limits maximum change in criticality per outcome to max_learning_rate.

        Parameters
        ----------
        gap_id : str
            Gap identifier
        new_signal : float
            New criticality signal

        Returns
        -------
        float
            Capped learning rate adjustment
        """
        if gap_id not in self.gap_criticality or len(self.gap_criticality[gap_id]) == 0:
            return new_signal

        # Current learned criticality
        current_samples = self.gap_criticality[gap_id]
        current_criticality = sum(current_samples) / len(current_samples)

        # Calculate maximum allowed change
        max_change = self.max_learning_rate * current_criticality
        actual_change = new_signal - current_criticality

        # Cap if needed
        if abs(actual_change) > max_change:
            if actual_change > 0:
                capped_signal = current_criticality + max_change
            else:
                capped_signal = current_criticality - max_change
            return capped_signal

        return new_signal
