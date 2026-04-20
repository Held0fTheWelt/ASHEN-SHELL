from __future__ import annotations
from dataclasses import dataclass

from .records import ThresholdInput

@dataclass
class ThresholdEngine:
    def rumor_to_legend(self, info: ThresholdInput) -> tuple[str, float]:
        score = (
            0.25 * min(info.repetition_count / 5.0, 1.0)
            + 0.2 * info.emotional_charge
            + 0.2 * min(info.carrier_count / 5.0, 1.0)
            + 0.15 * info.symbolic_density
            + 0.2 * info.collective_binding
            - 0.1 * info.debunking_pressure
            - 0.1 * info.fragmentation_pressure
        )
        return self._bucket(score)

    def cultural_to_sacred(self, info: ThresholdInput) -> tuple[str, float]:
        score = (
            0.25 * min(info.repetition_count / 5.0, 1.0)
            + 0.25 * min(info.ritualization_count / 4.0, 1.0)
            + 0.2 * info.collective_binding
            + 0.2 * info.symbolic_density
            - 0.1 * info.fragmentation_pressure
        )
        return self._bucket(score)

    def legend_to_ontological(self, info: ThresholdInput) -> tuple[str, float]:
        score = (
            0.2 * min(info.repetition_count / 6.0, 1.0)
            + 0.25 * min(info.ritualization_count / 5.0, 1.0)
            + 0.25 * info.collective_binding
            + 0.2 * info.symbolic_density
            + 0.1 * info.emotional_charge
            - 0.15 * info.debunking_pressure
        )
        return self._bucket(score)

    def _bucket(self, score: float) -> tuple[str, float]:
        score = round(max(0.0, min(1.0, score)), 6)
        if score >= 0.75:
            return "active_threshold_met", score
        if score >= 0.55:
            return "candidate", score
        return "blocked", score
