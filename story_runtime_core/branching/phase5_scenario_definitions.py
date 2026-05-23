"""
Decision point definitions for Phase 5 evaluation scenarios.

Scenario C (Branching Architecture): Tests path divergence with 3 approaches
Scenario E (Replayability): Same scenario, different evaluation sessions
"""

from typing import Any, Dict

from .decision_point import (
    DecisionPoint, DecisionPointType, DecisionOption, DecisionPointRegistry
)


def _decision_option(spec: tuple[str, str, str, list[str]]) -> DecisionOption:
    option_id, label, description, consequence_tags = spec
    return DecisionOption(
        id=option_id,
        label=label,
        description=description,
        consequence_tags=consequence_tags,
    )


def _register_decision_point(
    registry: DecisionPointRegistry,
    *,
    point_id: str,
    turn_number: int,
    decision_type: DecisionPointType,
    prompt: str,
    option_specs: list[tuple[str, str, str, list[str]]],
) -> None:
    registry.register(
        DecisionPoint(
            id=point_id,
            turn_number=turn_number,
            scenario_id="salon_mediation",
            decision_type=decision_type,
            prompt=prompt,
            options=[_decision_option(spec) for spec in option_specs],
        )
    )


SCENARIO_C_DECISION_POINT_SPECS: list[dict[str, Any]] = [
    {
        "point_id": "opening_posture",
        "turn_number": 2,
        "decision_type": DecisionPointType.APPROACH,
        "prompt": "How do you open this mediation?",
        "option_specs": [
            (
                "escalate",
                "Confront Power Imbalance",
                "Directly challenge the unequal dynamic that got you here",
                ["escalation_path", "high_pressure_early", "direct_style"],
            ),
            (
                "divide",
                "Separate the Issues",
                "Break the conflict into discrete, manageable pieces",
                ["divide_path", "measured_pressure", "analytical_style"],
            ),
            (
                "understand",
                "Lead with Empathy",
                "First seek to understand what each person really wants",
                ["understanding_path", "low_pressure_early", "relational_style"],
            ),
        ],
    },
    {
        "point_id": "pressure_response_escalation",
        "turn_number": 8,
        "decision_type": DecisionPointType.STRATEGY,
        "prompt": "The conversation is getting heated. What do you do?",
        "option_specs": [
            (
                "esc_hold_firm",
                "Hold Firm on Principle",
                "Maintain that the imbalance must be addressed",
                ["escalation_path", "escalation_intensifies", "confrontational"],
            ),
            (
                "esc_pivot",
                "Pivot to Understanding",
                "Recognize the risk and shift tone",
                ["escalation_path", "late_empathy", "course_correction"],
            ),
        ],
    },
    {
        "point_id": "pressure_response_divide",
        "turn_number": 8,
        "decision_type": DecisionPointType.STRATEGY,
        "prompt": "The details are getting complex. How do you proceed?",
        "option_specs": [
            (
                "div_dig_deeper",
                "Dig Deeper into Details",
                "More analysis, more structure",
                ["divide_path", "analysis_deepens", "methodical"],
            ),
            (
                "div_broaden",
                "Broaden to Bigger Picture",
                "Step back and see connections",
                ["divide_path", "systemic_view", "integrative"],
            ),
        ],
    },
    {
        "point_id": "pressure_response_understanding",
        "turn_number": 8,
        "decision_type": DecisionPointType.STRATEGY,
        "prompt": "You're starting to understand each person's real concern. What now?",
        "option_specs": [
            (
                "und_deepen",
                "Deepen Emotional Connection",
                "Go deeper into feelings and needs",
                ["understanding_path", "intimacy_grows", "vulnerable"],
            ),
            (
                "und_bridge",
                "Bridge to Shared Ground",
                "Show common ground and mutual interests",
                ["understanding_path", "common_ground_found", "collaborative"],
            ),
        ],
    },
    {
        "point_id": "closure_escalation",
        "turn_number": 15,
        "decision_type": DecisionPointType.ALIGNMENT,
        "prompt": "You've both held your ground. What happens now?",
        "option_specs": [
            (
                "esc_forced",
                "Force a Compromise",
                "Use your leverage to get a deal done",
                ["escalation_ending", "hollow_compromise", "power_imposed"],
            ),
            (
                "esc_learned",
                "Hard-Won Respect",
                "The confrontation led to genuine acknowledgment",
                ["escalation_ending", "mutual_respect_earned", "transformation"],
            ),
        ],
    },
    {
        "point_id": "closure_divide",
        "turn_number": 15,
        "decision_type": DecisionPointType.ALIGNMENT,
        "prompt": "You've mapped out the pieces. How do they fit together?",
        "option_specs": [
            (
                "div_structured",
                "Structured Agreement",
                "Clear terms, measurable outcomes",
                ["divide_ending", "clear_contract", "professional"],
            ),
            (
                "div_adaptive",
                "Adaptive Framework",
                "Agreement that can evolve as things change",
                ["divide_ending", "flexible_solution", "forward_looking"],
            ),
        ],
    },
    {
        "point_id": "closure_understanding",
        "turn_number": 15,
        "decision_type": DecisionPointType.ALIGNMENT,
        "prompt": "You both understand each other now. What comes next?",
        "option_specs": [
            (
                "und_connected",
                "Genuine Reconciliation",
                "Real relationship healing",
                ["understanding_ending", "healing_achieved", "reconnected"],
            ),
            (
                "und_grounded",
                "Grounded in Friendship",
                "Return to friendship with new understanding",
                ["understanding_ending", "friendship_renewed", "deepened_bond"],
            ),
        ],
    },
]


def build_scenario_c_registry() -> DecisionPointRegistry:
    """
    Scenario C: Salon Mediation

    Three decision points represent different conflict approaches:
    1. Turn 2: "Opening Posture" (APPROACH)
       - A: Escalation (confront power imbalance)
       - B: Divide (separate issues)
       - C: Understanding (empathize first)

    2. Turn 8: "Pressure Response" (STRATEGY)
       - Escalation path: Hold firm
       - Divide path: Reframe
       - Understanding path: Validate

    3. Turn 15: "Closure Type" (ALIGNMENT)
       - Different endings for each approach
    """
    registry = DecisionPointRegistry()
    for spec in SCENARIO_C_DECISION_POINT_SPECS:
        _register_decision_point(registry, **spec)
    return registry


def build_scenario_e_registry() -> DecisionPointRegistry:
    """
    Scenario E: Replayability Test

    Same as Scenario C, evaluators run it multiple times to measure replayability.
    Returns the same registry (Scenario C), which will be run with different
    decision paths to measure "would you play again?"
    """
    return build_scenario_c_registry()


def get_scenario_paths() -> Dict[str, list]:
    """
    Define the three canonical paths for Scenario C.

    Each path is a sequence of decisions that create a unique outcome.
    """
    return {
        "path_A_escalation": [
            ("opening_posture", "escalate"),
            ("pressure_response_escalation", "esc_hold_firm"),
            ("closure_escalation", "esc_learned"),
        ],
        "path_B_divide": [
            ("opening_posture", "divide"),
            ("pressure_response_divide", "div_dig_deeper"),
            ("closure_divide", "div_structured"),
        ],
        "path_C_understanding": [
            ("opening_posture", "understand"),
            ("pressure_response_understanding", "und_deepen"),
            ("closure_understanding", "und_connected"),
        ],
    }
