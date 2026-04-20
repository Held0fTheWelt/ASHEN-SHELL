from wos_mvp.consciousness_layer import ConsciousnessLayer
from wos_mvp.emotional_layer import EmotionalLayer
from wos_mvp.records import ConsciousnessState, EmotionalSignals, EmotionalState, StoryHealthVector

def test_emotional_layer_support_request() -> None:
    layer = EmotionalLayer()
    state = layer.update(EmotionalState(), EmotionalSignals("I am stuck and confused", 30, repeated_failure_count=2))
    constraints = layer.constraints(state)
    assert constraints.support_action in {"offer_hint_and_recap", "simplify"}

def test_consciousness_layer_strategy() -> None:
    layer = ConsciousnessLayer()
    state = ConsciousnessState(vector=StoryHealthVector(story_health=0.4, mystery_integrity=0.7, pacing_health=0.7), player_support_pressure=0.2)
    directive = layer.choose_strategy(state)
    assert directive.strategy in {"re_engage_player", "establish_mystery", "maintain_tension"}
