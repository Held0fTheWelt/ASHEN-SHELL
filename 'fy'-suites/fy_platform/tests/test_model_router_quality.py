from fy_platform.ai.model_router.router import ModelRouter


def test_model_router_escalates_on_ambiguity() -> None:
    router = ModelRouter()
    decision = router.route('triage', ambiguity='high', evidence_strength='moderate')
    assert decision.selected_tier == 'llm'
    assert 'ambiguity_escalation' in decision.reason
    assert decision.fallback_chain


def test_model_router_downgrades_when_evidence_is_weak() -> None:
    router = ModelRouter()
    decision = router.route('prepare_fix', ambiguity='low', evidence_strength='weak')
    assert decision.selected_tier == 'slm'
    assert decision.safety_mode == 'abstain-first'
