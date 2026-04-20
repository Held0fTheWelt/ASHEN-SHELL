from __future__ import annotations

from .records import ConsciousnessDirective, ConsciousnessState

class ConsciousnessLayer:
    def choose_strategy(self, state: ConsciousnessState) -> ConsciousnessDirective:
        vector = state.vector
        if state.degraded_mode_active:
            return ConsciousnessDirective("emergency_stabilize", 0.9, 0.1, "degraded mode active")
        if state.player_support_pressure >= 0.7:
            return ConsciousnessDirective("simplify_and_support", 0.9, 0.2, "support pressure high")
        if vector.story_health < 0.45:
            return ConsciousnessDirective("re_engage_player", 0.5, 0.6, "story health low")
        if vector.callback_debt > 0.7 and vector.mystery_integrity > 0.5:
            return ConsciousnessDirective("prepare_payoff", 0.3, 0.7, "callback debt high")
        if vector.pacing_health < 0.4:
            return ConsciousnessDirective("maintain_tension", 0.2, 0.8, "pacing under pressure")
        return ConsciousnessDirective("establish_mystery", 0.2, 0.5, "healthy baseline")

    def validate(self, state: ConsciousnessState) -> bool:
        return state.vector.story_health >= 0.25 and state.vector.tonal_integrity >= 0.3
