from wos_mvp.effects import EffectSurfaceActivationEngine
from wos_mvp.enums import DomainType, EffectSurface
from wos_mvp.records import ThresholdInput, TransformationRule
from wos_mvp.thresholds import ThresholdEngine
from wos_mvp.transformations import TransformationRuntime

def test_effect_activation(base_entry) -> None:
    base_entry.domain_type = DomainType.BELIEF
    engine = EffectSurfaceActivationEngine()
    result = engine.activate(base_entry, escalators=["martyrdom_frame"])
    assert result.primary_surface in {EffectSurface.BEHAVIOR, EffectSurface.RELATIONAL, EffectSurface.SOCIAL_REPUTATION}
    assert result.intensity_by_surface[result.primary_surface] >= 0.8

def test_transformation_runtime(base_entry) -> None:
    base_entry.domain_type = DomainType.RUMOR
    rule = TransformationRule(
        from_domain=DomainType.RUMOR,
        to_domain=DomainType.LEGEND,
        required_carriers=["community"],
        trigger_conditions=["repetition"],
        amplifiers=["martyrdom_frame"],
        blockers=["strong_debunking"],
        min_score=0.7,
        effect_surfaces=[EffectSurface.CULTURAL_NORMATIVE],
    )
    runtime = TransformationRuntime(ThresholdEngine())
    result = runtime.apply(base_entry, rule, ThresholdInput(repetition_count=6, emotional_charge=0.8, carrier_count=5, symbolic_density=0.8, collective_binding=0.8), ["community"])
    assert result.status in {"candidate", "active_threshold_met"}
