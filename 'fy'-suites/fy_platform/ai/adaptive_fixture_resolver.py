"""AdaptiveFixtureResolver: Learn from composition outcomes to improve fixture resolution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from fy_platform.ai.fixture_resolver import FixtureResolver, FixtureGap


@dataclass
class GapOutcome:
    """Record of a fixture gap and its resolution outcome."""
    gap_id: str
    input_name: str
    required_suite: str
    outcome: str  # 'resolved', 'worked_around', 'failed', 'mitigated'
    confidence_delta: float = 0.0  # change to gap criticality confidence
    metadata: dict[str, Any] = field(default_factory=dict)


class AdaptiveFixtureResolver(FixtureResolver):
    """Extend FixtureResolver with outcome tracking and learning.

    Learns gap criticality from ≥5 composition outcomes.
    Predicts which gaps will cause problems before composition.
    """

    def __init__(self):
        """Initialize the adaptive fixture resolver."""
        super().__init__()
        self.gap_outcomes: list[GapOutcome] = []
        self.criticality_scores: dict[str, float] = {}
        self._initialize_criticality_model()

    def _initialize_criticality_model(self):
        """Initialize criticality scores for known gaps."""
        # Baseline criticality for each known gap
        # Based on gap type and impact on suite execution
        baseline_criticality = {
            'missing_project_root': 0.95,         # Almost always critical
            'missing_contracts_json': 0.85,       # Critical for many suites
            'missing_test_obligations_json': 0.80,  # Important for downstream
            'incompatible_artifact_envelope': 0.75,  # Significant impact
            'missing_templates_json': 0.60,        # Less critical, has workarounds
            'unstable_docstring_audit': 0.50,      # Can be retried
            'missing_security_risks': 0.70,        # Important but recoverable
        }

        for gap_name, score in baseline_criticality.items():
            self.criticality_scores[gap_name] = score

    def learn_gap_outcome(self, gap_id: str, outcome: str, metadata: dict | None = None) -> GapOutcome:
        """Record a gap outcome and update criticality model.

        Parameters
        ----------
        gap_id : str
            Unique gap identifier
        outcome : str
            How gap was resolved: 'resolved', 'worked_around', 'failed', 'mitigated'
        metadata : dict, optional
            Additional context (suite_name, timestamp, etc.)

        Returns
        -------
        GapOutcome
            Recorded outcome
        """
        if metadata is None:
            metadata = {}

        # Find matching gap
        gap = None
        for g in self.gaps:
            if g.input_name == gap_id or gap_id in g.metadata.get('alias', []):
                gap = g
                break

        if gap is None:
            # Create synthetic gap for learning
            gap = FixtureGap(
                input_name=gap_id,
                status='unresolved',
                required_suite=metadata.get('required_suite', 'unknown'),
            )

        # Calculate confidence delta based on outcome
        confidence_delta = {
            'resolved': +0.10,       # Increases confidence that gap is not critical
            'worked_around': +0.05,  # Slight increase (workaround exists)
            'failed': -0.15,         # Decreases confidence (gap is critical)
            'mitigated': +0.08,      # Increases confidence (risk managed)
        }.get(outcome, 0.0)

        # Update criticality score
        current_score = self.criticality_scores.get(gap_id, 0.5)
        new_score = max(0.0, min(1.0, current_score - confidence_delta))
        self.criticality_scores[gap_id] = new_score

        # Record outcome
        gap_outcome = GapOutcome(
            gap_id=gap_id,
            input_name=gap.input_name,
            required_suite=gap.required_suite,
            outcome=outcome,
            confidence_delta=confidence_delta,
            metadata=metadata,
        )
        self.gap_outcomes.append(gap_outcome)

        return gap_outcome

    def predict_gap_criticality(self, gap: FixtureGap) -> float:
        """Predict how critical a gap is likely to be.

        Parameters
        ----------
        gap : FixtureGap
            Fixture gap to evaluate

        Returns
        -------
        float
            Criticality score 0.0-1.0 (higher = more critical)
        """
        # Base criticality from gap status
        status_criticality = {
            'missing': 0.85,
            'incompatible': 0.75,
            'unstable': 0.65,
            'unresolved': 0.55,
        }.get(gap.status, 0.50)

        # Severity multiplier
        severity_multiplier = {
            'critical': 1.0,
            'high': 0.85,
            'medium': 0.65,
            'low': 0.40,
        }.get(gap.severity, 0.50)

        # Look up learned criticality
        learned_score = self.criticality_scores.get(gap.input_name, None)

        if learned_score is not None:
            # Blend baseline with learned score (learned has 60% weight after ≥5 outcomes)
            outcome_count = sum(
                1 for o in self.gap_outcomes
                if o.input_name == gap.input_name
            )
            if outcome_count >= 5:
                learned_weight = 0.6
            elif outcome_count >= 2:
                learned_weight = 0.3
            else:
                learned_weight = 0.0

            final_score = (
                status_criticality * severity_multiplier * (1.0 - learned_weight)
                + learned_score * learned_weight
            )
        else:
            final_score = status_criticality * severity_multiplier

        return round(min(1.0, final_score), 2)

    def adaptive_resolver(self, suite: str) -> list[FixtureGap]:
        """Resolve fixtures for a suite using learned criticality.

        Applies adaptive filtering: deprioritize gaps with low learned criticality.

        Parameters
        ----------
        suite : str
            Suite to resolve fixtures for

        Returns
        -------
        list[FixtureGap]
            Sorted fixture gaps (critical first)
        """
        # Get all gaps for suite
        suite_gaps = [g for g in self.gaps if suite in g.metadata.get('suite_name', '')]

        if not suite_gaps:
            return []

        # Score each gap
        scored_gaps = []
        for gap in suite_gaps:
            criticality = self.predict_gap_criticality(gap)
            scored_gaps.append((gap, criticality))

        # Sort by criticality (descending)
        scored_gaps.sort(key=lambda x: x[1], reverse=True)

        # Return sorted gaps
        return [gap for gap, _ in scored_gaps]

    def learning_confidence(self) -> float:
        """Get confidence in the learned model.

        Returns
        -------
        float
            Confidence 0.0-1.0 based on outcome count
        """
        outcome_count = len(self.gap_outcomes)
        # Confidence increases with more outcomes (saturates at 20)
        return min(1.0, outcome_count / 20.0)

    def outcome_count(self) -> int:
        """Get count of recorded outcomes.

        Returns
        -------
        int
            Number of gap outcomes recorded
        """
        return len(self.gap_outcomes)

    def get_outcomes(self) -> list[GapOutcome]:
        """Get all recorded outcomes.

        Returns
        -------
        list[GapOutcome]
            All gap outcomes
        """
        return self.gap_outcomes

    def update_gap_confidence(self, gap: FixtureGap, new_confidence: float) -> FixtureGap:
        """Update a gap with new confidence score.

        Parameters
        ----------
        gap : FixtureGap
            Gap to update
        new_confidence : float
            New confidence score 0.0-1.0

        Returns
        -------
        FixtureGap
            Updated gap
        """
        gap.metadata['confidence_score'] = max(0.0, min(1.0, new_confidence))
        gap.metadata['last_updated'] = 'adaptive_resolver'
        return gap
