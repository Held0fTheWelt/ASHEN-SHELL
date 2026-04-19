from __future__ import annotations
from dataclasses import dataclass

from .enums import DomainType, EffectSurface
from .records import EffectActivationResult, MemoryEntry

DEFAULT_SURFACES = {
    DomainType.CANONICAL_TRUTH: [EffectSurface.INSTITUTIONAL_POLICY, EffectSurface.ARCHIVE_TRUTH_CONTEST, EffectSurface.OPERATIONAL_TACTICAL],
    DomainType.BELIEF: [EffectSurface.BEHAVIOR, EffectSurface.RELATIONAL, EffectSurface.SOCIAL_REPUTATION],
    DomainType.SOCIAL: [EffectSurface.RELATIONAL, EffectSurface.SOCIAL_REPUTATION, EffectSurface.NARRATIVE_DRAMATIC],
    DomainType.INSTITUTIONAL: [EffectSurface.INSTITUTIONAL_POLICY, EffectSurface.ARCHIVE_TRUTH_CONTEST],
    DomainType.RUMOR: [EffectSurface.SOCIAL_REPUTATION, EffectSurface.BEHAVIOR],
    DomainType.LEGEND: [EffectSurface.CULTURAL_NORMATIVE, EffectSurface.NARRATIVE_DRAMATIC, EffectSurface.RITUAL_SACRED],
    DomainType.SACRED: [EffectSurface.RITUAL_SACRED, EffectSurface.CULTURAL_NORMATIVE, EffectSurface.SPATIAL_ENVIRONMENTAL],
    DomainType.TRAUMA: [EffectSurface.BEHAVIOR, EffectSurface.RELATIONAL, EffectSurface.NARRATIVE_DRAMATIC],
    DomainType.COUNTER_MEMORY: [EffectSurface.ARCHIVE_TRUTH_CONTEST, EffectSurface.CULTURAL_NORMATIVE],
    DomainType.ONTOLOGICAL: [EffectSurface.ONTOLOGICAL, EffectSurface.SPATIAL_ENVIRONMENTAL],
}

@dataclass
class EffectSurfaceActivationEngine:
    def activate(self, entry: MemoryEntry, blockers: list[str] | None = None, escalators: list[str] | None = None) -> EffectActivationResult:
        surfaces = entry.effect_surfaces or DEFAULT_SURFACES.get(entry.domain_type, [EffectSurface.NARRATIVE_DRAMATIC])
        primary = entry.primary_surface or surfaces[0]
        secondary = [s for s in surfaces if s != primary][:2]
        latent = [s for s in DEFAULT_SURFACES.get(entry.domain_type, []) if s not in {primary, *secondary}]
        intensity = {primary: 0.8}
        for s in secondary:
            intensity[s] = 0.5
        for s in latent:
            intensity[s] = 0.2
        used_blockers = []
        used_escalators = []
        for blocker in blockers or []:
            if blocker in {"strong_debunking", "carrier_fragmentation"}:
                used_blockers.append(blocker)
                for key in list(intensity):
                    intensity[key] = round(max(0.0, intensity[key] - 0.25), 4)
        for escalator in escalators or []:
            if escalator in {"martyrdom_frame", "place_binding", "ritual_retelling"}:
                used_escalators.append(escalator)
                intensity[primary] = round(min(1.0, intensity[primary] + 0.15), 4)
        return EffectActivationResult(
            primary_surface=primary,
            secondary_surfaces=secondary,
            latent_surfaces=latent,
            intensity_by_surface=intensity,
            blockers_triggered=used_blockers,
            escalators_triggered=used_escalators,
        )
