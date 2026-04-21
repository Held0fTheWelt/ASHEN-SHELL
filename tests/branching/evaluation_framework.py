"""
Evaluation framework for branching outcomes.

Measures outcome divergence, determinism, and replayability for Phase 5 scenarios.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum
import json


class EvaluationMetric(Enum):
    """Metrics tracked during evaluation."""
    OUTCOME_DIVERGENCE = "outcome_divergence"  # % difference between paths
    DETERMINISM = "determinism"  # Same input → same output
    REPLAYABILITY = "replayability"  # % evaluators want to replay
    BRANCH_COHERENCE = "branch_coherence"  # Paths feel intentional
    DIALOGUE_CONSISTENCY = "dialogue_consistency"  # Character voice stability
    PRESSURE_TRAJECTORY = "pressure_trajectory"  # Pressure curve shape
    CONSEQUENCE_VISIBILITY = "consequence_visibility"  # Facts carry forward


@dataclass
class SessionTranscript:
    """Complete transcript of a branching session."""
    session_id: str
    scenario_id: str
    evaluator_id: str
    approach_name: str  # e.g., "A1: Escalation", "B2: Divide", "C3: Understanding"
    path_signature: str  # Unique signature of decision path
    turns: List[Dict[str, Any]] = field(default_factory=list)
    decision_sequence: List[Dict[str, Any]] = field(default_factory=list)
    consequence_tags: Set[str] = field(default_factory=set)
    pressure_trajectory: List[float] = field(default_factory=list)
    character_dialogue: Dict[str, List[str]] = field(default_factory=dict)  # char -> lines
    final_state: Optional[Dict[str, Any]] = None


@dataclass
class EvaluatorFeedback:
    """Post-session feedback from evaluator."""
    evaluator_id: str
    session_id: str
    timestamp: str

    # Quantitative (1-10 scales)
    arc_satisfaction: int  # Overall story arc satisfaction
    character_consistency: int  # Did characters sound like themselves
    player_agency: int  # Did moves feel like they mattered
    pressure_coherence: int  # Did pressure feel believable
    consequence_visibility: int  # Could you see how facts affected story
    engagement: int  # How interested were you
    branch_intentionality: int  # Did different path feel intentional or random

    # Qualitative
    what_felt_real: List[str] = field(default_factory=list)  # 2-3 examples
    what_felt_fake: List[str] = field(default_factory=list)  # 2-3 examples
    most_real_character: Optional[str] = None
    least_real_character: Optional[str] = None
    would_replay: bool = False
    replay_reason: Optional[str] = None
    biggest_takeaway: Optional[str] = None


@dataclass
class DivergenceAnalysis:
    """Complete divergence analysis for a session pair."""
    path_a_signature: str
    path_b_signature: str
    approach_a: str
    approach_b: str

    # Metrics
    decision_divergence_percentage: float  # % of decisions different
    consequence_divergence_percentage: float  # % of facts different
    pressure_divergence_percentage: float  # Avg pressure difference
    dialogue_divergence_percentage: float  # % of dialogue different
    ending_divergence_percentage: float  # Final state differences

    # Overall
    overall_divergence_percentage: float  # Weighted average

    # Details
    decision_points_different: List[str] = field(default_factory=list)  # Which turns diverged
    unique_facts_a: Set[str] = field(default_factory=set)  # Only in path A
    unique_facts_b: Set[str] = field(default_factory=set)  # Only in path B
    character_arc_differences: Dict[str, str] = field(default_factory=dict)  # char -> how it differs


class EvaluationProtocol:
    """Protocol for running branching evaluation sessions."""

    @staticmethod
    def create_session_config(scenario_id: str, approach_name: str,
                             decision_registry, evaluator_id: str) -> Dict[str, Any]:
        """
        Create configuration for an evaluation session.

        Args:
            scenario_id: Which scenario to run (e.g., "salon_mediation")
            approach_name: Which approach (e.g., "A1: Escalation")
            decision_registry: Registry of decision points
            evaluator_id: Who is evaluating

        Returns:
            Config dict for session runner
        """
        scenario_decisions = decision_registry.get_for_scenario(scenario_id)

        return {
            "session_id": f"{scenario_id}_{approach_name}_{evaluator_id}",
            "scenario_id": scenario_id,
            "approach_name": approach_name,
            "evaluator_id": evaluator_id,
            "decision_points": [d.to_dict() for d in scenario_decisions],
            "checkpoint_every_n_turns": 5,  # Evaluator notes every 5 turns
            "expected_turns": 20,  # Estimated session length
            "expected_decision_points": len(scenario_decisions),
        }

    @staticmethod
    def create_checkpoint_protocol() -> Dict[str, Any]:
        """Create protocol for evaluator checkpoints every 5 turns."""
        return {
            "frequency": 5,  # Every 5 turns
            "questions": [
                "How is the drama feeling right now? (Building, plateauing, resolving?)",
                "Can you tell the characters apart by voice alone?",
                "Are your choices feeling consequential?",
                "What's the pressure level? (1-10)",
                "Any inconsistencies or weird moments?",
                "Would you want to continue playing?",
            ]
        }

    @staticmethod
    def calculate_overall_divergence(analysis: DivergenceAnalysis) -> float:
        """
        Calculate overall divergence with weighted metrics.

        Returns:
            Divergence percentage (0-100)
        """
        weights = {
            "decision": 0.25,  # Different choices matter
            "consequence": 0.35,  # Different facts matter most
            "pressure": 0.15,  # Pressure curve shape
            "dialogue": 0.15,  # Character lines differ
            "ending": 0.10,  # Final state differs
        }

        weighted_sum = (
            analysis.decision_divergence_percentage * weights["decision"] +
            analysis.consequence_divergence_percentage * weights["consequence"] +
            analysis.pressure_divergence_percentage * weights["pressure"] +
            analysis.dialogue_divergence_percentage * weights["dialogue"] +
            analysis.ending_divergence_percentage * weights["ending"]
        )

        return weighted_sum

    @staticmethod
    def assess_divergence_quality(percentage: float) -> str:
        """Qualitative assessment of divergence percentage."""
        if percentage < 20:
            return "minimal (paths nearly identical)"
        elif percentage < 40:
            return "low (paths mostly aligned)"
        elif percentage < 60:
            return "moderate (paths noticeably different)"
        elif percentage < 80:
            return "high (paths significantly divergent)"
        else:
            return "very_high (paths almost completely different)"


class ReplayabilityEvaluator:
    """Measures replayability (Scenario E: same scenario, different approaches)."""

    def __init__(self):
        self.replay_sessions: Dict[str, List[SessionTranscript]] = {}  # evaluator -> [transcripts]
        self.replay_feedback: Dict[str, List[EvaluatorFeedback]] = {}  # evaluator -> [feedback]

    def register_replay_pair(self, evaluator_id: str, transcript1: SessionTranscript,
                           transcript2: SessionTranscript, feedback: EvaluatorFeedback) -> None:
        """Register a replay pair (same scenario, different approaches)."""
        if evaluator_id not in self.replay_sessions:
            self.replay_sessions[evaluator_id] = []
            self.replay_feedback[evaluator_id] = []

        self.replay_sessions[evaluator_id].extend([transcript1, transcript2])
        self.replay_feedback[evaluator_id].append(feedback)

    def calculate_replayability_likelihood(self) -> float:
        """
        Calculate % of evaluators who want to replay.

        Returns:
            Percentage (0-100) of evaluators marking would_replay=True
        """
        if not self.replay_feedback:
            return 0.0

        total_evaluators = len(self.replay_feedback)
        would_replay = sum(
            1 for feedback_list in self.replay_feedback.values()
            if any(f.would_replay for f in feedback_list)
        )

        return (would_replay / total_evaluators) * 100.0

    def get_replay_analysis(self) -> Dict[str, Any]:
        """Get full replayability analysis."""
        return {
            "replayability_likelihood": self.calculate_replayability_likelihood(),
            "evaluators_sampled": len(self.replay_feedback),
            "total_replay_pairs": sum(len(v) // 2 for v in self.replay_sessions.values()),
            "replay_reasons": self._collect_reasons(),
        }

    def _collect_reasons(self) -> List[str]:
        """Collect why evaluators want (or don't want) to replay."""
        reasons = []
        for feedback_list in self.replay_feedback.values():
            for feedback in feedback_list:
                if feedback.would_replay and feedback.replay_reason:
                    reasons.append(feedback.replay_reason)
        return reasons


class DeterminismVerifier:
    """Verifies determinism: same inputs → same outputs."""

    def __init__(self):
        self.determinism_tests: List[Dict[str, Any]] = []

    def register_test(self, scenario_id: str, decision_sequence: List[str],
                     transcript1: SessionTranscript, transcript2: SessionTranscript) -> None:
        """
        Register a determinism test (same decisions, compare transcripts).

        Args:
            scenario_id: Scenario tested
            decision_sequence: List of decision IDs chosen (same for both)
            transcript1: First run with these decisions
            transcript2: Second run with same decisions
        """
        # Compare transcripts for byte-level or meaningful equality
        identical = self._compare_transcripts(transcript1, transcript2)

        self.determinism_tests.append({
            "scenario_id": scenario_id,
            "decision_sequence": decision_sequence,
            "identical": identical,
            "differences": self._find_differences(transcript1, transcript2) if not identical else [],
        })

    def verify_determinism(self) -> bool:
        """Check if ALL determinism tests passed."""
        if not self.determinism_tests:
            return False
        return all(t["identical"] for t in self.determinism_tests)

    def get_determinism_report(self) -> Dict[str, Any]:
        """Get full determinism report."""
        total = len(self.determinism_tests)
        passed = sum(1 for t in self.determinism_tests if t["identical"])

        return {
            "determinism_verified": self.verify_determinism(),
            "tests_passed": passed,
            "tests_total": total,
            "pass_rate": (passed / total * 100.0) if total > 0 else 0,
            "failures": [t for t in self.determinism_tests if not t["identical"]],
        }

    @staticmethod
    def _compare_transcripts(t1: SessionTranscript, t2: SessionTranscript) -> bool:
        """Compare two transcripts for equivalence."""
        return (
            t1.path_signature == t2.path_signature and
            len(t1.turns) == len(t2.turns) and
            t1.consequence_tags == t2.consequence_tags
        )

    @staticmethod
    def _find_differences(t1: SessionTranscript, t2: SessionTranscript) -> List[str]:
        """Find and describe differences between transcripts."""
        diffs = []

        if t1.path_signature != t2.path_signature:
            diffs.append(f"Path signatures differ: {t1.path_signature} vs {t2.path_signature}")

        if len(t1.turns) != len(t2.turns):
            diffs.append(f"Turn counts differ: {len(t1.turns)} vs {len(t2.turns)}")

        if t1.consequence_tags != t2.consequence_tags:
            diffs.append(f"Consequence tags differ: {t1.consequence_tags} vs {t2.consequence_tags}")

        return diffs


class EvaluationReport:
    """Complete evaluation report for Phase 6."""

    def __init__(self, scenario_id: str):
        self.scenario_id = scenario_id
        self.session_transcripts: List[SessionTranscript] = []
        self.evaluator_feedback: List[EvaluatorFeedback] = []
        self.divergence_analyses: List[DivergenceAnalysis] = []
        self.replayability = ReplayabilityEvaluator()
        self.determinism = DeterminismVerifier()

    def add_session(self, transcript: SessionTranscript, feedback: EvaluatorFeedback) -> None:
        """Add a completed session to the report."""
        self.session_transcripts.append(transcript)
        self.evaluator_feedback.append(feedback)

    def add_divergence(self, analysis: DivergenceAnalysis) -> None:
        """Add divergence analysis for a path pair."""
        self.divergence_analyses.append(analysis)

    def get_summary(self) -> Dict[str, Any]:
        """Get complete evaluation summary."""
        return {
            "scenario": self.scenario_id,
            "sessions_completed": len(self.session_transcripts),
            "evaluators": len(set(f.evaluator_id for f in self.evaluator_feedback)),

            "outcome_divergence": {
                "analyses": len(self.divergence_analyses),
                "average_divergence": self._avg_divergence(),
                "meets_60_percent_target": self._avg_divergence() >= 60.0,
            },

            "determinism": self.determinism.get_determinism_report(),

            "replayability": self.replayability.get_replay_analysis(),

            "evaluator_satisfaction": self._avg_satisfaction(),

            "branch_coherence": self._avg_branch_coherence(),
        }

    def _avg_divergence(self) -> float:
        """Average divergence across all analyses."""
        if not self.divergence_analyses:
            return 0.0
        return sum(a.overall_divergence_percentage for a in self.divergence_analyses) / len(self.divergence_analyses)

    def _avg_satisfaction(self) -> Dict[str, float]:
        """Average evaluator satisfaction metrics."""
        if not self.evaluator_feedback:
            return {}

        metrics = [
            "arc_satisfaction",
            "character_consistency",
            "player_agency",
            "pressure_coherence",
            "consequence_visibility",
            "engagement",
        ]

        averages = {}
        for metric in metrics:
            values = [getattr(f, metric) for f in self.evaluator_feedback]
            averages[metric] = sum(values) / len(values) if values else 0.0

        return averages

    def _avg_branch_coherence(self) -> float:
        """Average branch coherence rating."""
        if not self.evaluator_feedback:
            return 0.0
        values = [f.branch_intentionality for f in self.evaluator_feedback]
        return sum(values) / len(values) if values else 0.0

    def to_json(self) -> str:
        """Serialize report to JSON."""
        return json.dumps(self.get_summary(), indent=2, default=str)
