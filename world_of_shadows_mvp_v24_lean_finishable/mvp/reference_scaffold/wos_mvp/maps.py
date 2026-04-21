from __future__ import annotations

from .enums import DomainType, EffectSurface

MEMORY_DOMAIN_FRAMEWORK = {
    DomainType.CANONICAL_TRUTH.value: {"carrier_scope": "authoritative_runtime", "authority_class": "hard_authority", "promotion_path": "commit_only"},
    DomainType.BELIEF.value: {"carrier_scope": "actor_bound", "authority_class": "subjective", "promotion_path": "never_direct_to_truth"},
    DomainType.SOCIAL.value: {"carrier_scope": "relationship_network", "authority_class": "socially_effective", "promotion_path": "social_to_cultural_possible"},
    DomainType.INSTITUTIONAL.value: {"carrier_scope": "organization", "authority_class": "official_but_selective", "promotion_path": "report_and_policy"},
    DomainType.RUMOR.value: {"carrier_scope": "community_or_network", "authority_class": "low_veracity_high_propagation", "promotion_path": "threshold_to_legend"},
    DomainType.LEGEND.value: {"carrier_scope": "community_and_symbols", "authority_class": "symbolic", "promotion_path": "threshold_to_ontological"},
    DomainType.SACRED.value: {"carrier_scope": "ritual_or_order", "authority_class": "protected", "promotion_path": "guarded_only"},
    DomainType.TRAUMA.value: {"carrier_scope": "individual_or_collective", "authority_class": "damaged_access", "promotion_path": "suppression_or_reconstruction"},
    DomainType.COUNTER_MEMORY.value: {"carrier_scope": "research_or_underarchive", "authority_class": "contestable", "promotion_path": "governed_promotion"},
    DomainType.ONTOLOGICAL.value: {"carrier_scope": "collective_binding", "authority_class": "world_active", "promotion_path": "feature_gated"},
}

MEMORY_INTERACTION_LAWS = {
    "truth_stays_truth": "non-canonical domains do not overwrite canonical truth directly",
    "effect_not_equal_truth": "a false rumor may still alter behavior and reputation",
    "belief_is_carrier_bound": "belief must always have a carrier",
    "suppression_is_active": "suppression is blocked access, not absence",
    "sacred_memory_protected": "sacred memory uses stronger merge and access rules",
}

MEMORY_TRANSFORMATION_MAP = [
    ("episodic", "belief"),
    ("episodic", "social"),
    ("belief", "rumor"),
    ("rumor", "legend"),
    ("cultural", "sacred"),
    ("legend", "ontological"),
    ("suppression", "counter_memory"),
]

MEMORY_CARRIER_MAP = {
    "individual": ["belief", "trauma", "episodic"],
    "family": ["social", "cultural", "counter_memory"],
    "institution": ["institutional", "suppression", "archive"],
    "community": ["rumor", "legend", "cultural", "sacred"],
    "place": ["spatial", "sacred", "ontological"],
}

MEMORY_EFFECT_SURFACE_MAP = {
    DomainType.BELIEF.value: [EffectSurface.BEHAVIOR.value, EffectSurface.RELATIONAL.value],
    DomainType.RUMOR.value: [EffectSurface.SOCIAL_REPUTATION.value, EffectSurface.BEHAVIOR.value],
    DomainType.LEGEND.value: [EffectSurface.CULTURAL_NORMATIVE.value, EffectSurface.RITUAL_SACRED.value],
    DomainType.ONTOLOGICAL.value: [EffectSurface.ONTOLOGICAL.value, EffectSurface.SPATIAL_ENVIRONMENTAL.value],
}

MEMORY_CONFLICT_MAP = {
    "truth_vs_belief": "carrier believes something canon denies",
    "institution_vs_witness": "official record conflicts with testimony",
    "sacred_vs_evidence": "protected ritual claim conflicts with modern evidence",
    "rumor_vs_containment": "memetic spread resists official correction",
}

MEMORY_THRESHOLD_MAP = {
    "rumor_to_legend": ["repetition", "emotion", "carriers", "symbolic_density"],
    "cultural_to_sacred": ["ritualization", "binding", "repetition", "symbolic_density"],
    "legend_to_ontological": ["ritualization", "binding", "reach", "place_binding"],
}

MEMORY_GOVERNANCE_MAP = {
    "read": ["runtime", "operator", "audit", "research"],
    "write": ["runtime_commit", "authorized_authoring", "governed_research"],
    "promote": ["governance_review", "commit_gate", "research_promotion_gate"],
    "suppress": ["institutional_policy", "safety_policy", "taboo_policy"],
}
