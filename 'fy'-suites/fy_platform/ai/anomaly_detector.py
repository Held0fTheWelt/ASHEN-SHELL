"""AnomalyDetector: Detect outcome outliers and regime shifts in suite composition data."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, stdev
from typing import Any

from fy_platform.ai.outcome_persistence import OutcomePersistence, CompositionOutcome


@dataclass
class AnomalyRecord:
    """Record of detected anomaly."""
    anomaly_type: str  # 'outlier', 'regime_shift', 'fixture_broken', 'suite_update'
    severity: float  # 0.0-1.0, higher is more severe
    z_score: float  # Z-score for statistical significance
    affected_suites: list[str] = field(default_factory=list)
    description: str = ""
    timestamp: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dict for serialization."""
        return {
            'anomaly_type': self.anomaly_type,
            'severity': self.severity,
            'z_score': self.z_score,
            'affected_suites': self.affected_suites,
            'description': self.description,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
        }


class AnomalyDetector:
    """Detect anomalies in suite composition outcomes.

    Identifies:
    - Cost/criticality outliers (Z-score > 2.0)
    - Regime shifts (distribution changes)
    - Broken fixtures (fixture failures causing divergence)
    - Suite updates (performance changes after updates)

    Target: Catch ≥90% of known regime shifts.
    """

    def __init__(self, persistence: OutcomePersistence | None = None):
        """Initialize anomaly detector.

        Parameters
        ----------
        persistence : OutcomePersistence, optional
            Outcome persistence instance. Creates new if not provided.
        """
        self.persistence = persistence or OutcomePersistence()
        self.z_score_threshold = 2.0  # Standard deviation threshold for outliers
        self.regime_shift_threshold = 0.5  # Change in mean as fraction of baseline std dev
        self.min_samples_for_detection = 10  # Minimum outcomes needed
        self._detected_anomalies: list[AnomalyRecord] = []

    def detect_anomalies(self) -> list[AnomalyRecord]:
        """Detect all anomalies in outcome history.

        Returns
        -------
        list[AnomalyRecord]
            List of detected anomalies
        """
        outcomes = self.persistence.load_outcomes(limit=1000)

        if len(outcomes) < self.min_samples_for_detection:
            return []

        self._detected_anomalies = []

        # Detect cost outliers
        cost_outliers = self._detect_cost_outliers(outcomes)
        self._detected_anomalies.extend(cost_outliers)

        # Detect criticality outliers
        criticality_outliers = self._detect_criticality_outliers(outcomes)
        self._detected_anomalies.extend(criticality_outliers)

        # Detect regime shifts
        regime_shifts = self._detect_regime_shifts(outcomes)
        self._detected_anomalies.extend(regime_shifts)

        # Detect broken fixtures
        broken_fixtures = self._detect_broken_fixtures(outcomes)
        self._detected_anomalies.extend(broken_fixtures)

        return self._detected_anomalies

    def is_anomalous_outcome(self, outcome: CompositionOutcome) -> bool:
        """Check if a single outcome is anomalous.

        Parameters
        ----------
        outcome : CompositionOutcome
            Outcome to check

        Returns
        -------
        bool
            True if anomalous
        """
        outcomes = self.persistence.load_outcomes(limit=1000)

        if len(outcomes) < self.min_samples_for_detection:
            return False

        # Calculate statistics
        actual_costs = [o.actual_cost for o in outcomes if o.actual_cost > 0]
        if not actual_costs or len(actual_costs) < 5:
            return False

        mean_cost = mean(actual_costs)
        std_cost = stdev(actual_costs) if len(actual_costs) > 1 else 0.0

        # Check if outcome is outlier
        if std_cost > 0:
            z_score = abs(outcome.actual_cost - mean_cost) / std_cost
            return z_score > self.z_score_threshold

        return False

    def regime_shift_detected(self) -> bool:
        """Check if regime shift has been detected in recent outcomes.

        Returns
        -------
        bool
            True if regime shift detected
        """
        shifts = [a for a in self._detected_anomalies if a.anomaly_type == 'regime_shift']
        return len(shifts) > 0

    def anomaly_severity(self, outcome: CompositionOutcome) -> float:
        """Calculate anomaly severity for an outcome.

        Parameters
        ----------
        outcome : CompositionOutcome
            Outcome to evaluate

        Returns
        -------
        float
            Severity 0.0-1.0
        """
        outcomes = self.persistence.load_outcomes(limit=1000)

        if len(outcomes) < self.min_samples_for_detection:
            return 0.0

        actual_costs = [o.actual_cost for o in outcomes if o.actual_cost > 0]
        if not actual_costs or len(actual_costs) < 5:
            return 0.0

        mean_cost = mean(actual_costs)
        std_cost = stdev(actual_costs) if len(actual_costs) > 1 else 0.0

        # Z-score based severity
        if std_cost > 0:
            z_score = abs(outcome.actual_cost - mean_cost) / std_cost
            severity = min(1.0, (z_score - self.z_score_threshold) / 3.0)
            return max(0.0, severity)

        return 0.0

    def get_detected_anomalies(self) -> list[AnomalyRecord]:
        """Get all detected anomalies.

        Returns
        -------
        list[AnomalyRecord]
            List of anomalies
        """
        return self._detected_anomalies

    def anomaly_count(self) -> int:
        """Get count of detected anomalies.

        Returns
        -------
        int
            Number of anomalies
        """
        return len(self._detected_anomalies)

    def anomalies_by_type(self) -> dict[str, list[AnomalyRecord]]:
        """Get anomalies grouped by type.

        Returns
        -------
        dict[str, list[AnomalyRecord]]
            Anomalies indexed by type
        """
        by_type = {}
        for anomaly in self._detected_anomalies:
            if anomaly.anomaly_type not in by_type:
                by_type[anomaly.anomaly_type] = []
            by_type[anomaly.anomaly_type].append(anomaly)
        return by_type

    def _detect_cost_outliers(self, outcomes: list[CompositionOutcome]) -> list[AnomalyRecord]:
        """Detect cost outliers using Z-score.

        Parameters
        ----------
        outcomes : list[CompositionOutcome]
            Outcomes to analyze

        Returns
        -------
        list[AnomalyRecord]
            Detected cost outliers
        """
        actual_costs = [o.actual_cost for o in outcomes if o.actual_cost > 0]

        if len(actual_costs) < 5:
            return []

        mean_cost = mean(actual_costs)
        std_cost = stdev(actual_costs) if len(actual_costs) > 1 else 0.0

        if std_cost == 0:
            return []

        anomalies = []
        for outcome in outcomes:
            z_score = abs(outcome.actual_cost - mean_cost) / std_cost

            if z_score > self.z_score_threshold:
                severity = min(1.0, (z_score - self.z_score_threshold) / 3.0)
                anomaly = AnomalyRecord(
                    anomaly_type='outlier',
                    severity=severity,
                    z_score=z_score,
                    affected_suites=outcome.suites,
                    description=f'Cost outlier: {outcome.actual_cost:.2f} USD (Z={z_score:.2f})',
                    timestamp=outcome.timestamp,
                    metadata={
                        'mean_cost': mean_cost,
                        'std_dev': std_cost,
                        'actual_cost': outcome.actual_cost,
                    }
                )
                anomalies.append(anomaly)

        return anomalies

    def _detect_criticality_outliers(self, outcomes: list[CompositionOutcome]) -> list[AnomalyRecord]:
        """Detect criticality outliers based on outcome status patterns.

        Parameters
        ----------
        outcomes : list[CompositionOutcome]
            Outcomes to analyze

        Returns
        -------
        list[AnomalyRecord]
            Detected criticality anomalies
        """
        # Map outcome status to criticality
        criticality_map = {
            'success': 0.1,
            'partial': 0.6,
            'failed': 0.9,
        }

        criticalities = [
            criticality_map.get(o.outcome_status, 0.5) for o in outcomes
        ]

        if len(criticalities) < 5:
            return []

        mean_crit = mean(criticalities)
        std_crit = stdev(criticalities) if len(criticalities) > 1 else 0.0

        if std_crit == 0:
            return []

        anomalies = []
        for outcome in outcomes:
            crit = criticality_map.get(outcome.outcome_status, 0.5)
            z_score = abs(crit - mean_crit) / std_crit

            if z_score > self.z_score_threshold:
                severity = min(1.0, (z_score - self.z_score_threshold) / 3.0)
                anomaly = AnomalyRecord(
                    anomaly_type='outlier',
                    severity=severity,
                    z_score=z_score,
                    affected_suites=outcome.suites,
                    description=f'Criticality outlier: {outcome.outcome_status} (Z={z_score:.2f})',
                    timestamp=outcome.timestamp,
                    metadata={
                        'outcome_status': outcome.outcome_status,
                        'mean_criticality': mean_crit,
                        'std_dev': std_crit,
                    }
                )
                anomalies.append(anomaly)

        return anomalies

    def _detect_regime_shifts(self, outcomes: list[CompositionOutcome]) -> list[AnomalyRecord]:
        """Detect regime shifts in cost distribution.

        Parameters
        ----------
        outcomes : list[CompositionOutcome]
            Outcomes to analyze

        Returns
        -------
        list[AnomalyRecord]
            Detected regime shifts
        """
        if len(outcomes) < self.min_samples_for_detection:
            return []

        # Split outcomes into early and recent
        split_point = len(outcomes) // 2
        early = outcomes[split_point:]  # Oldest
        recent = outcomes[:split_point]  # Newest

        early_costs = [o.actual_cost for o in early if o.actual_cost > 0]
        recent_costs = [o.actual_cost for o in recent if o.actual_cost > 0]

        if len(early_costs) < 5 or len(recent_costs) < 5:
            return []

        early_mean = mean(early_costs)
        early_std = stdev(early_costs) if len(early_costs) > 1 else 0.0

        recent_mean = mean(recent_costs)

        if early_std == 0:
            return []

        # Detect shift: change in mean as multiple of baseline std dev
        shift = abs(recent_mean - early_mean)
        shift_score = shift / early_std if early_std > 0 else 0.0

        anomalies = []
        if shift_score > self.regime_shift_threshold:
            severity = min(1.0, shift_score / 1.5)  # Normalize to 0-1
            anomaly = AnomalyRecord(
                anomaly_type='regime_shift',
                severity=severity,
                z_score=shift_score,
                affected_suites=list(set(o.suites[0] for o in recent if o.suites)),
                description=f'Regime shift detected: mean {early_mean:.2f} -> {recent_mean:.2f} USD',
                timestamp=recent[0].timestamp if recent else "",
                metadata={
                    'early_mean': early_mean,
                    'recent_mean': recent_mean,
                    'shift_magnitude': shift,
                    'early_sample_count': len(early_costs),
                    'recent_sample_count': len(recent_costs),
                }
            )
            anomalies.append(anomaly)

        return anomalies

    def _detect_broken_fixtures(self, outcomes: list[CompositionOutcome]) -> list[AnomalyRecord]:
        """Detect broken fixtures causing failures.

        Parameters
        ----------
        outcomes : list[CompositionOutcome]
            Outcomes to analyze

        Returns
        -------
        list[AnomalyRecord]
            Detected broken fixtures
        """
        # Group by fixture
        fixture_outcomes: dict[str, list[CompositionOutcome]] = {}
        for outcome in outcomes:
            for fixture in outcome.fixtures_used:
                if fixture not in fixture_outcomes:
                    fixture_outcomes[fixture] = []
                fixture_outcomes[fixture].append(outcome)

        anomalies = []
        for fixture, fixture_outc in fixture_outcomes.items():
            if len(fixture_outc) < 5:
                continue

            # Calculate failure rate
            failures = len([o for o in fixture_outc if o.outcome_status == 'failed'])
            failure_rate = failures / len(fixture_outc) if len(fixture_outc) > 0 else 0.0

            # Flag if failure rate > 50%
            if failure_rate > 0.5:
                severity = min(1.0, failure_rate)
                anomaly = AnomalyRecord(
                    anomaly_type='fixture_broken',
                    severity=severity,
                    z_score=failure_rate,
                    affected_suites=[o.suites[0] for o in fixture_outc if o.suites],
                    description=f'Fixture {fixture} broken: {failure_rate*100:.0f}% failure rate',
                    timestamp=fixture_outc[0].timestamp,
                    metadata={
                        'fixture_id': fixture,
                        'failure_rate': failure_rate,
                        'total_uses': len(fixture_outc),
                        'failure_count': failures,
                    }
                )
                anomalies.append(anomaly)

        return anomalies
