"""
Decision point definitions for Phase 5 evaluation scenarios.

Scenario C (Branching Architecture): Tests path divergence with 3 approaches
Scenario E (Replayability): Same scenario, different evaluation sessions
"""

from typing import Dict

from .decision_point import (
    DecisionPoint, DecisionPointType, DecisionOption, DecisionPointRegistry
)


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

    # ========== Decision Point 1: Opening Posture (Turn 2) ==========
    dp1_options = [
        DecisionOption(
            id="escalate",
            label="Confront Power Imbalance",
            description="Directly challenge the unequal dynamic that got you here",
            consequence_tags=["escalation_path", "high_pressure_early", "direct_style"]
        ),
        DecisionOption(
            id="divide",
            label="Separate the Issues",
            description="Break the conflict into discrete, manageable pieces",
            consequence_tags=["divide_path", "measured_pressure", "analytical_style"]
        ),
        DecisionOption(
            id="understand",
            label="Lead with Empathy",
            description="First seek to understand what each person really wants",
            consequence_tags=["understanding_path", "low_pressure_early", "relational_style"]
        ),
    ]

    dp1 = DecisionPoint(
        id="opening_posture",
        turn_number=2,
        scenario_id="salon_mediation",
        decision_type=DecisionPointType.APPROACH,
        prompt="How do you open this mediation?",
        options=dp1_options
    )
    registry.register(dp1)

    # ========== Decision Point 2: Pressure Response (Turn 8) ==========
    # Different options depending on which approach was taken

    # Escalation path: Response options
    escalation_response_options = [
        DecisionOption(
            id="esc_hold_firm",
            label="Hold Firm on Principle",
            description="Maintain that the imbalance must be addressed",
            consequence_tags=["escalation_path", "escalation_intensifies", "confrontational"]
        ),
        DecisionOption(
            id="esc_pivot",
            label="Pivot to Understanding",
            description="Recognize the risk and shift tone",
            consequence_tags=["escalation_path", "late_empathy", "course_correction"]
        ),
    ]

    # Divide path: Response options
    divide_response_options = [
        DecisionOption(
            id="div_dig_deeper",
            label="Dig Deeper into Details",
            description="More analysis, more structure",
            consequence_tags=["divide_path", "analysis_deepens", "methodical"]
        ),
        DecisionOption(
            id="div_broaden",
            label="Broaden to Bigger Picture",
            description="Step back and see connections",
            consequence_tags=["divide_path", "systemic_view", "integrative"]
        ),
    ]

    # Understanding path: Response options
    understanding_response_options = [
        DecisionOption(
            id="und_deepen",
            label="Deepen Emotional Connection",
            description="Go deeper into feelings and needs",
            consequence_tags=["understanding_path", "intimacy_grows", "vulnerable"]
        ),
        DecisionOption(
            id="und_bridge",
            label="Bridge to Shared Ground",
            description="Show common ground and mutual interests",
            consequence_tags=["understanding_path", "common_ground_found", "collaborative"]
        ),
    ]

    # Register all three path variants at Turn 8
    dp2_esc = DecisionPoint(
        id="pressure_response_escalation",
        turn_number=8,
        scenario_id="salon_mediation",
        decision_type=DecisionPointType.STRATEGY,
        prompt="The conversation is getting heated. What do you do?",
        options=escalation_response_options
    )
    registry.register(dp2_esc)

    dp2_div = DecisionPoint(
        id="pressure_response_divide",
        turn_number=8,
        scenario_id="salon_mediation",
        decision_type=DecisionPointType.STRATEGY,
        prompt="The details are getting complex. How do you proceed?",
        options=divide_response_options
    )
    registry.register(dp2_div)

    dp2_und = DecisionPoint(
        id="pressure_response_understanding",
        turn_number=8,
        scenario_id="salon_mediation",
        decision_type=DecisionPointType.STRATEGY,
        prompt="You're starting to understand each person's real concern. What now?",
        options=understanding_response_options
    )
    registry.register(dp2_und)

    # ========== Decision Point 3: Closure Type (Turn 15) ==========
    # Different closure options for each path

    escalation_closure_options = [
        DecisionOption(
            id="esc_forced",
            label="Force a Compromise",
            description="Use your leverage to get a deal done",
            consequence_tags=["escalation_ending", "hollow_compromise", "power_imposed"]
        ),
        DecisionOption(
            id="esc_learned",
            label="Hard-Won Respect",
            description="The confrontation led to genuine acknowledgment",
            consequence_tags=["escalation_ending", "mutual_respect_earned", "transformation"]
        ),
    ]

    divide_closure_options = [
        DecisionOption(
            id="div_structured",
            label="Structured Agreement",
            description="Clear terms, measurable outcomes",
            consequence_tags=["divide_ending", "clear_contract", "professional"]
        ),
        DecisionOption(
            id="div_adaptive",
            label="Adaptive Framework",
            description="Agreement that can evolve as things change",
            consequence_tags=["divide_ending", "flexible_solution", "forward_looking"]
        ),
    ]

    understanding_closure_options = [
        DecisionOption(
            id="und_connected",
            label="Genuine Reconciliation",
            description="Real relationship healing",
            consequence_tags=["understanding_ending", "healing_achieved", "reconnected"]
        ),
        DecisionOption(
            id="und_grounded",
            label="Grounded in Friendship",
            description="Return to friendship with new understanding",
            consequence_tags=["understanding_ending", "friendship_renewed", "deepened_bond"]
        ),
    ]

    dp3_esc = DecisionPoint(
        id="closure_escalation",
        turn_number=15,
        scenario_id="salon_mediation",
        decision_type=DecisionPointType.ALIGNMENT,
        prompt="You've both held your ground. What happens now?",
        options=escalation_closure_options
    )
    registry.register(dp3_esc)

    dp3_div = DecisionPoint(
        id="closure_divide",
        turn_number=15,
        scenario_id="salon_mediation",
        decision_type=DecisionPointType.ALIGNMENT,
        prompt="You've mapped out the pieces. How do they fit together?",
        options=divide_closure_options
    )
    registry.register(dp3_div)

    dp3_und = DecisionPoint(
        id="closure_understanding",
        turn_number=15,
        scenario_id="salon_mediation",
        decision_type=DecisionPointType.ALIGNMENT,
        prompt="You both understand each other now. What comes next?",
        options=understanding_closure_options
    )
    registry.register(dp3_und)

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
