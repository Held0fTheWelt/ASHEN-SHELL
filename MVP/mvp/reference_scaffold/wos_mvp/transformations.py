from __future__ import annotations

from .records import MemoryEntry, ThresholdInput, TransformationResult, TransformationRule
from .thresholds import ThresholdEngine

class TransformationRuntime:
    def __init__(self, threshold_engine: ThresholdEngine) -> None:
        self.threshold_engine = threshold_engine

    def apply(self, entry: MemoryEntry, rule: TransformationRule, info: ThresholdInput, available_carriers: list[str]) -> TransformationResult:
        notes: list[str] = []
        if entry.domain_type != rule.from_domain:
            return TransformationResult(status="blocked", score=0.0, rule_name=f"{rule.from_domain}->{rule.to_domain}", notes=["wrong_source_domain"])
        if not all(carrier in available_carriers for carrier in rule.required_carriers):
            return TransformationResult(status="blocked", score=0.0, rule_name=f"{rule.from_domain}->{rule.to_domain}", notes=["missing_required_carrier"])
        if rule.to_domain.value.endswith("legend_mythic_memory"):
            status, score = self.threshold_engine.rumor_to_legend(info)
        elif rule.to_domain.value.endswith("sacred_ritual_memory"):
            status, score = self.threshold_engine.cultural_to_sacred(info)
        elif rule.to_domain.value.endswith("ontological_reality_bearing_memory"):
            status, score = self.threshold_engine.legend_to_ontological(info)
        else:
            status, score = ("candidate", rule.min_score)
        if status != "blocked":
            notes.append(f"effect_surfaces={','.join(s.value for s in rule.effect_surfaces)}")
        return TransformationResult(status=status, score=score, rule_name=f"{rule.from_domain.value}->{rule.to_domain.value}", notes=notes)
