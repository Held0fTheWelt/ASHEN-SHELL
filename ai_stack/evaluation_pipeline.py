"""MVP4 Phase C: Quality Evaluation Pipeline with Rubric, Baseline, and Self-Tuning."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """Quality rubric dimensions."""
    COHERENCE = "coherence"
    AUTHENTICITY = "authenticity"
    PLAYER_AGENCY = "player_agency"
    IMMERSION = "immersion"


@dataclass
class RubricDimension:
    """Definition of a single quality dimension."""
    name: QualityDimension
    description: str
    score_range: tuple[int, int] = (1, 5)
    automated_eval: Optional[str] = None
    human_eval_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name.value,
            "description": self.description,
            "score_range": self.score_range,
            "automated_eval": self.automated_eval,
            "human_eval_required": self.human_eval_required,
        }


@dataclass
class QualityRubric:
    """Quality rubric for evaluation."""
    rubric_id: str
    version: str
    dimensions: list[RubricDimension] = field(default_factory=list)
    pass_threshold: float = 3.5
    failure_signals: list[str] = field(default_factory=lambda: [
        "coercion", "narrator_invalid_mode", "degradation_marker"
    ])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "rubric_id": self.rubric_id,
            "version": self.version,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "pass_threshold": self.pass_threshold,
            "failure_signals": self.failure_signals,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> QualityRubric:
        dimensions = [
            RubricDimension(
                name=QualityDimension(d["name"]),
                description=d["description"],
                score_range=tuple(d.get("score_range", [1, 5])),
                automated_eval=d.get("automated_eval"),
                human_eval_required=d.get("human_eval_required", True),
            )
            for d in data.get("dimensions", [])
        ]
        return QualityRubric(
            rubric_id=data.get("rubric_id", ""),
            version=data.get("version", "1.0"),
            dimensions=dimensions,
            pass_threshold=data.get("pass_threshold", 3.5),
            failure_signals=data.get("failure_signals", []),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )


@dataclass
class TurnScore:
    """Score for a single turn across all dimensions."""
    turn_id: str
    session_id: str
    scores: dict[str, float] = field(default_factory=dict)  # dimension.value -> score
    average_score: float = 0.0
    passed: bool = True
    annotated_by: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    feedback_tags: list[str] = field(default_factory=list)
    notes: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "session_id": self.session_id,
            "scores": dict(self.scores),
            "average_score": self.average_score,
            "passed": self.passed,
            "annotated_by": self.annotated_by,
            "timestamp": self.timestamp,
            "feedback_tags": self.feedback_tags,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> TurnScore:
        return TurnScore(
            turn_id=data.get("turn_id", ""),
            session_id=data.get("session_id", ""),
            scores=data.get("scores", {}),
            average_score=data.get("average_score", 0.0),
            passed=data.get("passed", True),
            annotated_by=data.get("annotated_by"),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            feedback_tags=data.get("feedback_tags", []),
            notes=data.get("notes"),
        )


@dataclass
class BaselineMetrics:
    """Baseline metrics for quality regression detection."""
    dimension: str
    median_score: float
    p5_score: float
    p95_score: float
    sample_count: int
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "median_score": self.median_score,
            "p5_score": self.p5_score,
            "p95_score": self.p95_score,
            "sample_count": self.sample_count,
            "last_updated": self.last_updated,
        }


@dataclass
class OfflineBaseline:
    """Offline baseline test set for regression detection."""
    baseline_id: str
    version: str
    canonical_turns: list[dict[str, Any]] = field(default_factory=list)
    metrics_per_dimension: dict[str, BaselineMetrics] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_id": self.baseline_id,
            "version": self.version,
            "canonical_turns": self.canonical_turns,
            "metrics_per_dimension": {
                k: v.to_dict() for k, v in self.metrics_per_dimension.items()
            },
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> OfflineBaseline:
        metrics = {}
        for dim, metric_data in data.get("metrics_per_dimension", {}).items():
            metrics[dim] = BaselineMetrics(
                dimension=metric_data.get("dimension", ""),
                median_score=metric_data.get("median_score", 0.0),
                p5_score=metric_data.get("p5_score", 0.0),
                p95_score=metric_data.get("p95_score", 0.0),
                sample_count=metric_data.get("sample_count", 0),
                last_updated=metric_data.get("last_updated", datetime.now(timezone.utc).isoformat()),
            )
        return OfflineBaseline(
            baseline_id=data.get("baseline_id", ""),
            version=data.get("version", "1.0"),
            canonical_turns=data.get("canonical_turns", []),
            metrics_per_dimension=metrics,
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )


@dataclass
class RubricWeights:
    """Learnable weights for rubric dimensions (auto-tuning)."""
    weight_coherence: float = 1.0
    weight_authenticity: float = 1.0
    weight_player_agency: float = 1.0
    weight_immersion: float = 1.0
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_by: Optional[str] = None  # "automatic_weekly" or admin username

    def to_dict(self) -> dict[str, Any]:
        return {
            "weight_coherence": self.weight_coherence,
            "weight_authenticity": self.weight_authenticity,
            "weight_player_agency": self.weight_player_agency,
            "weight_immersion": self.weight_immersion,
            "last_updated": self.last_updated,
            "updated_by": self.updated_by,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> RubricWeights:
        return RubricWeights(
            weight_coherence=data.get("weight_coherence", 1.0),
            weight_authenticity=data.get("weight_authenticity", 1.0),
            weight_player_agency=data.get("weight_player_agency", 1.0),
            weight_immersion=data.get("weight_immersion", 1.0),
            last_updated=data.get("last_updated", datetime.now(timezone.utc).isoformat()),
            updated_by=data.get("updated_by"),
        )


class EvaluationPipeline:
    """Quality evaluation with offline baseline, annotation, and self-tuning."""

    def __init__(self, session_storage: Any):
        self.storage = session_storage

    def get_rubric(self, rubric_id: str = "goc_quality_v1") -> QualityRubric:
        """Get evaluation rubric."""
        storage_key = f"evaluation_rubric:{rubric_id}"
        stored = self.storage.get(storage_key)

        if stored:
            if isinstance(stored, dict):
                return QualityRubric.from_dict(stored)
            return stored

        # Default God of Carnage rubric
        default_rubric = QualityRubric(
            rubric_id=rubric_id,
            version="1.0",
            dimensions=[
                RubricDimension(
                    name=QualityDimension.COHERENCE,
                    description="LDSS output logically follows scene state and responder intent",
                    automated_eval="langfuse_semantic_similarity(output, scene_context)",
                ),
                RubricDimension(
                    name=QualityDimension.AUTHENTICITY,
                    description="Character voice consistent with canonical God of Carnage personality",
                    automated_eval="langfuse_tone_match(output_tone, character_profile)",
                ),
                RubricDimension(
                    name=QualityDimension.PLAYER_AGENCY,
                    description="Output does not coerce or predetermine player choices",
                    automated_eval="langfuse_constraint_violation_check(narrator_voice_rules)",
                ),
                RubricDimension(
                    name=QualityDimension.IMMERSION,
                    description="Dramatic pacing and narrative tension appropriate to scene",
                    automated_eval="langfuse_structural_validation(scene_function, pacing_mode)",
                ),
            ],
            pass_threshold=3.5,
        )
        self.storage.set(storage_key, default_rubric)
        return default_rubric

    def get_baseline(self, baseline_id: str = "goc_evaluation_baseline") -> OfflineBaseline:
        """Get offline baseline test set."""
        storage_key = f"evaluation_baseline:{baseline_id}"
        stored = self.storage.get(storage_key)

        if stored:
            if isinstance(stored, dict):
                return OfflineBaseline.from_dict(stored)
            return stored

        # Default empty baseline (Phase A, will be populated in Phase C)
        baseline = OfflineBaseline(
            baseline_id=baseline_id,
            version="1.0",
            canonical_turns=[],
            metrics_per_dimension={},
        )
        self.storage.set(storage_key, baseline)
        return baseline

    def get_rubric_weights(
        self, session_id: str
    ) -> RubricWeights:
        """Get current rubric weights for session."""
        storage_key = f"rubric_weights:{session_id}"
        stored = self.storage.get(storage_key)

        if stored:
            if isinstance(stored, dict):
                return RubricWeights.from_dict(stored)
            return stored

        weights = RubricWeights()
        self.storage.set(storage_key, weights)
        return weights

    def record_turn_score(
        self,
        turn_score: TurnScore,
        session_id: str,
    ) -> None:
        """Record annotation for a turn."""
        storage_key = f"turn_score:{session_id}:{turn_score.turn_id}"
        self.storage.set(storage_key, turn_score)

        # Add to evaluation dataset for self-tuning
        dataset_key = f"eval_dataset:{session_id}"
        dataset = self.storage.get(dataset_key) or []
        if not isinstance(dataset, list):
            dataset = []
        dataset.append(turn_score.to_dict())
        self.storage.set(dataset_key, dataset)

        logger.info(
            f"Recorded turn score: {turn_score.turn_id}, avg={turn_score.average_score:.2f}"
        )

    def auto_tune_weights(
        self,
        session_id: str,
        trigger: str = "automatic_weekly",
    ) -> RubricWeights:
        """Auto-tune rubric weights based on production failures.

        Examines failed turns (quality_class=failed or degradation_critical) to identify
        which dimension issues correlate most with failures. Adjusts weights accordingly.
        """
        dataset_key = f"eval_dataset:{session_id}"
        dataset = self.storage.get(dataset_key) or []

        if not dataset:
            logger.info("No evaluation data available for auto-tuning")
            return self.get_rubric_weights(session_id)

        # Count failure correlations per dimension
        dimension_failure_counts = {
            QualityDimension.COHERENCE.value: 0,
            QualityDimension.AUTHENTICITY.value: 0,
            QualityDimension.PLAYER_AGENCY.value: 0,
            QualityDimension.IMMERSION.value: 0,
        }

        failed_turns = [t for t in dataset if not t.get("passed", True)]

        for turn in failed_turns:
            for dim, score in turn.get("scores", {}).items():
                if score < 3.0:  # Low score indicates this dimension likely caused failure
                    dimension_failure_counts[dim] = dimension_failure_counts.get(dim, 0) + 1

        # Adjust weights: lower weight for dimensions that fail frequently
        total_failures = sum(dimension_failure_counts.values()) or 1
        new_weights = RubricWeights()

        for dim, count in dimension_failure_counts.items():
            failure_rate = count / total_failures
            # Lower weight if failure rate > 25% (above average)
            adjustment = 0.8 if failure_rate > 0.25 else 1.0
            setattr(new_weights, f"weight_{dim}", adjustment)

        new_weights.last_updated = datetime.now(timezone.utc).isoformat()
        new_weights.updated_by = trigger

        self.storage.set(f"rubric_weights:{session_id}", new_weights)

        logger.info(
            f"Auto-tuned rubric weights for {session_id}: {new_weights.to_dict()}"
        )

        return new_weights

    def manual_tune_weights(
        self,
        session_id: str,
        turn_count: int = 10,
        admin_user: str = "admin",
    ) -> RubricWeights:
        """Manually trigger rubric weight tuning from recent turns."""
        dataset_key = f"eval_dataset:{session_id}"
        dataset = self.storage.get(dataset_key) or []

        if not dataset:
            logger.warning("No evaluation data for manual tuning")
            return self.get_rubric_weights(session_id)

        # Use last N turns for tuning
        recent_turns = dataset[-turn_count:] if turn_count > 0 else dataset

        logger.info(
            f"Manual tune triggered by {admin_user} on {len(recent_turns)} recent turns"
        )

        return self.auto_tune_weights(session_id, trigger=f"manual_{admin_user}")

    def check_baseline_regression(
        self,
        baseline_id: str = "goc_evaluation_baseline",
    ) -> dict[str, Any]:
        """Check if current production metrics show regression vs baseline."""
        baseline = self.get_baseline(baseline_id)

        if not baseline.metrics_per_dimension:
            logger.info("No baseline metrics available for regression check")
            return {"regression_detected": False, "details": []}

        # Phase A: Placeholder (Phase B will integrate real Langfuse data)
        regression_report = {
            "regression_detected": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": [],
            "dimensions_below_p5": [],
        }

        # In Phase B, would fetch production metrics and compare to baseline
        # For now, return clean structure ready for Phase B

        return regression_report
