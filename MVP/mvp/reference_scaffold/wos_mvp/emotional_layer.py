from __future__ import annotations

from .records import EmotionalConstraints, EmotionalSignals, EmotionalState

class EmotionalLayer:
    def update(self, state: EmotionalState, signals: EmotionalSignals) -> EmotionalState:
        text = signals.input_text.lower()
        if any(token in text for token in ["stuck", "confused", "don't know", "help", "hilfe"]):
            state.confusion = min(1.0, state.confusion + 0.35)
            state.frustration = min(1.0, state.frustration + 0.25)
            state.support_need = min(1.0, state.support_need + 0.4)
            state.engagement = max(0.0, state.engagement - 0.05)
        if signals.response_time_seconds > 120:
            state.overload = min(1.0, state.overload + 0.25)
            state.pacing_tolerance = max(0.0, state.pacing_tolerance - 0.1)
        if signals.repeated_failure_count >= 2:
            state.agency = max(0.0, state.agency - 0.25)
            state.support_need = min(1.0, state.support_need + 0.2)
        if signals.scene_energy < 0.2:
            state.boredom = min(1.0, state.boredom + 0.15)
        if signals.choice_count > 4:
            state.overload = min(1.0, state.overload + 0.1)
        return state

    def constraints(self, state: EmotionalState) -> EmotionalConstraints:
        support_action = "none"
        pacing = "normal"
        if state.support_need >= 0.6:
            support_action = "offer_hint_and_recap"
        elif state.overload >= 0.5:
            support_action = "simplify"
        elif state.boredom >= 0.5:
            support_action = "re-engage"

        if state.overload >= 0.5:
            pacing = "slow"
        elif state.boredom >= 0.5:
            pacing = "faster"

        return EmotionalConstraints(
            support_action=support_action,
            target_engagement=round(max(0.5, state.engagement), 4),
            max_cognitive_load=round(max(0.35, 1.0 - state.overload), 4),
            pacing_mode=pacing,
        )

    def validate_output(self, output_text: str, constraints: EmotionalConstraints) -> bool:
        cognitive_load = min(1.0, len(output_text.split()) / 120.0)
        return cognitive_load <= constraints.max_cognitive_load + 0.2
