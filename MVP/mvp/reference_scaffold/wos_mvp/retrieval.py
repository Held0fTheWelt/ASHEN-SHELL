from __future__ import annotations
from dataclasses import dataclass

from .enums import IndexState, RetrievalTaskProfile
from .index_lifecycle import IndexLifecycleManager
from .records import MemoryEntry, QueryContext, RetrievalCandidate
from .relevance import RelevanceScorer

def _chargram_similarity(left: str, right: str) -> float:
    def grams(s: str) -> set[str]:
        s = f"  {s.lower()}  "
        return {s[i:i+3] for i in range(max(len(s) - 2, 1))}
    lg = grams(left)
    rg = grams(right)
    inter = len(lg & rg)
    union = len(lg | rg) or 1
    return inter / union

@dataclass
class RetrievalPlanner:
    entries: list[MemoryEntry]
    scorer: RelevanceScorer
    index_manager: IndexLifecycleManager

    def retrieve(self, query: str, context: QueryContext, top_k: int = 5) -> list[RetrievalCandidate]:
        state = self.index_manager.state_for(context.partition_key)
        if state == IndexState.FAILED and context.task_profile in {RetrievalTaskProfile.AUDIT}:
            raise RuntimeError("audit profile requires a usable index snapshot")
        lexical_hits = self.index_manager.search(query, context.partition_key)
        candidates: list[RetrievalCandidate] = []
        for entry, lexical_score in lexical_hits:
            if not self._include_for_profile(entry, context):
                continue
            semantic = _chargram_similarity(query, entry.normalized_value)
            relevance = self.scorer.compute_relevance(entry, context)
            final = 0.42 * lexical_score + 0.28 * semantic + 0.30 * relevance
            candidates.append(RetrievalCandidate(entry=entry, lexical_score=round(lexical_score, 6), semantic_score=round(semantic, 6), relevance_score=relevance, final_score=round(final, 6)))
        candidates.sort(key=lambda item: item.final_score, reverse=True)
        return candidates[:top_k]

    def _include_for_profile(self, entry: MemoryEntry, context: QueryContext) -> bool:
        if entry.partition_key.world_module() != context.partition_key.world_module():
            return False
        if context.task_profile == RetrievalTaskProfile.RUNTIME_QUESTION:
            return entry.metadata.get("fresh", True)
        if context.task_profile == RetrievalTaskProfile.DIAGNOSIS:
            return True
        if context.task_profile == RetrievalTaskProfile.AUDIT:
            return True
        if context.task_profile == RetrievalTaskProfile.RESEARCH:
            return True
        if context.task_profile == RetrievalTaskProfile.AUTHORING:
            return True
        return True

    def retrieve_for_runtime_question(self, query: str, context: QueryContext) -> list[RetrievalCandidate]:
        context.task_profile = RetrievalTaskProfile.RUNTIME_QUESTION
        return self.retrieve(query, context, top_k=5)

    def retrieve_for_diagnosis(self, query: str, context: QueryContext) -> list[RetrievalCandidate]:
        context.task_profile = RetrievalTaskProfile.DIAGNOSIS
        return self.retrieve(query, context, top_k=10)

    def retrieve_for_audit(self, query: str, context: QueryContext) -> list[RetrievalCandidate]:
        context.task_profile = RetrievalTaskProfile.AUDIT
        return self.retrieve(query, context, top_k=20)
