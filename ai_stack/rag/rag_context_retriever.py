"""
Hybrid retrieval orchestration: scoring, pool phase, and hit assembly
(DS-003 stage 8).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ai_stack.rag.rag_embedding_index import CorpusEmbeddingIndex
from ai_stack.rag.rag_governance import governance_view_for_chunk
from ai_stack.rag.rag_retrieval_hybrid_encoding import _resolve_retrieval_hybrid_encoding_state
from ai_stack.rag.rag_retrieval_lexical import _cosine_similarity, _hybrid_core_initial
from ai_stack.rag.rag_retrieval_policy_pool import (
    _dedup_select,
    _hit_policy_note,
    _pack_role_for_hit,
    _profile_policy_influence,
)
from ai_stack.rag.rag_retrieval_support import (
    _RetrievalEncodeScorePoolPhase,
    _append_dedup_suppression_quality_notes,
    _build_retrieval_prefix_notes,
    _build_retrieval_quality_seed_notes,
    _build_retrieval_query_profile_context,
    _rerank_retrieval_candidate_pool,
    _retrieval_result_degraded_empty_corpus,
    _retrieval_result_fallback_empty_hits,
    _retrieval_result_ok_with_hits,
    _sorted_candidates_to_hard_filtered_pool,
)
from ai_stack.rag.rag_constants import (
    DOMAIN_CONTENT_ACCESS,
    HYBRID_CORE_SCALE,
    INITIAL_MODULE_MATCH_BOOST,
    INITIAL_SCENE_HINT_BOOST,
    RETRIEVAL_POLICY_VERSION,
)
from ai_stack.rag.rag_types import RetrievalDomainError
from ai_stack.rag.semantic_embedding import EMBEDDING_INDEX_VERSION
from ai_stack.rag.retrieval_runtime_planner import build_retrieval_authority_metadata

from ai_stack.rag.rag_corpus import InMemoryRetrievalCorpus, _ScoredCandidate
from ai_stack.rag.rag_retrieval_dtos import RetrievalHit, RetrievalRequest, RetrievalResult


class ContextRetriever:
    """``ContextRetriever`` groups related behaviour; callers should read members for contracts and threading assumptions.
    """
    def __init__(
        self,
        corpus: InMemoryRetrievalCorpus,
        *,
        embedding_index: CorpusEmbeddingIndex | None = None,
        embedding_model_id: str = "",
    ) -> None:
        """``__init__`` — see implementation for behaviour and contracts.
        
        Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
        
        Args:
            corpus: ``corpus`` (InMemoryRetrievalCorpus); meaning follows the type and call sites.
            embedding_index: ``embedding_index`` (CorpusEmbeddingIndex | None); meaning follows the type and call sites.
            embedding_model_id: ``embedding_model_id`` (str); meaning follows the type and call sites.
        """
        self.corpus = corpus
        self._embedding_index = embedding_index
        self._embedding_model_id = embedding_model_id or (embedding_index.model_id if embedding_index else "")
        # Last-observed turn stats — written on every retrieve() call, read by diagnostics surfaces.
        self.last_retrieval_route: str = ""
        self.last_embedding_model_id: str = ""
        self.last_retrieval_corpus_fingerprint: str = ""

    def _corpus_trace(self) -> tuple[str, str, str]:
        """``_corpus_trace`` — see implementation for behaviour and contracts.
        
        Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
        
        Returns:
            tuple[str, str, str]:
                Returns a value of type ``tuple[str, str,
                str]``; see the function body for structure, error paths, and sentinels.
        """
        corpus = self.corpus
        return corpus.index_version, corpus.corpus_fingerprint, corpus.storage_path or ""

    def _embedding_ready(self) -> bool:
        """``_embedding_ready`` — see implementation for behaviour and contracts.
        
        Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
        
        Returns:
            bool:
                Returns a value of type ``bool``; see the function body for structure, error paths, and sentinels.
        """
        if self._embedding_index is None:
            return False
        return self._embedding_index.vectors.shape[0] == len(self.corpus.chunks)

    def _score_initial_candidates(
        self,
        request: RetrievalRequest,
        *,
        allowed_classes: set[Any],
        query_terms: dict[str, float],
        query_norm: float,
        use_hybrid: bool,
        query_vec: np.ndarray | None,
        profile_name: str,
        profile_boosts: dict[Any, float],
        canonical_weight: float,
        w_dense: float,
        w_sparse: float,
    ) -> list[_ScoredCandidate]:
        """Dense/sparse hybrid scoring over corpus chunks (initial pool,
        pre-policy rerank).
        
        Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
        
        Args:
            request: ``request`` (RetrievalRequest); meaning follows the type and call sites.
            allowed_classes: ``allowed_classes`` (set[Any]); meaning follows the type and call sites.
            query_terms: ``query_terms`` (dict[str,
                float]); meaning follows the type and call sites.
            query_norm: ``query_norm`` (float); meaning follows the type and call sites.
            use_hybrid: ``use_hybrid`` (bool); meaning follows the type and call sites.
            query_vec: ``query_vec`` (np.ndarray | None); meaning follows the type and call sites.
            profile_name: ``profile_name`` (str); meaning follows the type and call sites.
            profile_boosts: ``profile_boosts`` (dict[Any,
                float]); meaning follows the type and call sites.
            canonical_weight: ``canonical_weight`` (float); meaning follows the type and call sites.
            w_dense: ``w_dense`` (float); meaning follows the type and call sites.
            w_sparse: ``w_sparse`` (float); meaning follows the type and call sites.
        
        Returns:
            list[_ScoredCandidate]:
                Returns a value of type ``list[_ScoredCandidate]``; see the function body for structure, error paths, and sentinels.
        """
        candidates: list[_ScoredCandidate] = []
        for chunk_index, chunk in enumerate(self.corpus.chunks):
            if chunk.content_class not in allowed_classes:
                continue
            sparse_sim = _cosine_similarity(query_terms, query_norm, chunk)
            dense_sim = 0.0
            if use_hybrid and query_vec is not None:
                dense_sim = float(np.dot(query_vec, self._embedding_index.vectors[chunk_index]))
                dense_sim = max(0.0, min(1.0, dense_sim))
            hybrid_core = _hybrid_core_initial(
                dense_sim,
                sparse_sim,
                use_hybrid=use_hybrid,
                w_dense=w_dense,
                w_sparse=w_sparse,
            )
            score = hybrid_core * HYBRID_CORE_SCALE
            reasons: list[str] = []
            if use_hybrid and query_vec is not None:
                reasons.append(
                    f"hybrid_core={hybrid_core:.3f}; dense_cos={dense_sim:.3f}; sparse_cos={sparse_sim:.3f}"
                )
            elif sparse_sim > 0:
                reasons.append(f"semantic_similarity={sparse_sim:.3f}")
            profile_boost = profile_boosts.get(chunk.content_class, 0.0)
            if profile_boost:
                score += profile_boost
                reasons.append(f"profile_boost={profile_boost:.2f}")
            canonical_boost = canonical_weight * float(chunk.canonical_priority)
            if canonical_boost:
                score += canonical_boost
                reasons.append(f"canonical_boost={canonical_boost:.2f}")
            module_match = bool(
                request.module_id and chunk.module_id and request.module_id == chunk.module_id
            )
            scene_match = bool(request.scene_id and request.scene_id in chunk.text)
            if module_match:
                score += INITIAL_MODULE_MATCH_BOOST
                reasons.append(f"module_match_boost={INITIAL_MODULE_MATCH_BOOST:.2f}")
            if scene_match:
                score += INITIAL_SCENE_HINT_BOOST
                reasons.append(f"scene_hint_boost={INITIAL_SCENE_HINT_BOOST:.2f}")
            if score <= 0:
                continue
            candidates.append(
                _ScoredCandidate(
                    chunk_index=chunk_index,
                    chunk=chunk,
                    dense_sim=dense_sim,
                    sparse_sim=sparse_sim,
                    hybrid_core=hybrid_core,
                    initial_score=score,
                    initial_reason="; ".join(reasons) or "semantic_match",
                    module_match=module_match,
                    scene_match=scene_match,
                )
            )
        return candidates

    def _build_retrieval_hits_from_selection(
        self,
        selected_tuples: list[tuple[float, _ScoredCandidate, list[str]]],
        *,
        profile_name: str,
        published_canonical_in_pool: bool,
        audience_scope: str,
    ) -> list[RetrievalHit]:
        """Map reranked/scored candidates to ``RetrievalHit`` rows
        (governance + policy notes).
        
        Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
        
        Args:
            selected_tuples: ``selected_tuples`` (list[tuple[float, _ScoredCandidate, list[str]]]); meaning follows the type and call sites.
            profile_name: ``profile_name`` (str); meaning follows the type and call sites.
            published_canonical_in_pool: ``published_canonical_in_pool`` (bool); meaning follows the type and call sites.
        
        Returns:
            list[RetrievalHit]:
                Returns a value of type ``list[RetrievalHit]``; see the function body for structure, error paths, and sentinels.
        """
        hits: list[RetrievalHit] = []
        for rerank_score, cand, rparts in selected_tuples:
            reason_core = cand.initial_reason
            if rparts:
                reason_core = reason_core + " | " + "; ".join(rparts)
            gov = governance_view_for_chunk(cand.chunk)
            pack_role = _pack_role_for_hit(profile=profile_name, chunk=cand.chunk, gov=gov)
            policy_note = _hit_policy_note(
                profile_name,
                gov,
                published_canonical_in_pool=published_canonical_in_pool,
                chunk=cand.chunk,
            )
            rule = _profile_policy_influence(profile_name, gov)
            why = (
                f"score={rerank_score:.2f}; lane={gov.evidence_lane.value}; pack_role={pack_role}; policy={policy_note}"
            )
            hits.append(
                RetrievalHit(
                    chunk_id=cand.chunk.chunk_id,
                    source_path=cand.chunk.source_path,
                    source_name=cand.chunk.source_name,
                    content_class=cand.chunk.content_class.value,
                    source_version=cand.chunk.source_version,
                    score=rerank_score,
                    snippet=cand.chunk.text[:400],
                    selection_reason=reason_core,
                    pack_role=pack_role,
                    why_selected=why,
                    source_evidence_lane=gov.evidence_lane.value,
                    source_visibility_class=gov.visibility_class.value,
                    policy_note=policy_note,
                    profile_policy_influence=rule,
                    authority_level="retrieved_unverified",
                    provenance_scope="retrieval_hit",
                    audience_scope=audience_scope or "",
                )
            )
        return hits

    def _dense_retrieval_metadata(self) -> dict[str, Any]:
        trace = self._corpus_trace()
        corpus = self.corpus
        return {
            "index_version": trace[0],
            "corpus_fingerprint": trace[1],
            "storage_path": trace[2],
            "dense_index_build_action": corpus.rag_dense_index_build_action,
            "dense_rebuild_reason": corpus.rag_dense_rebuild_reason,
            "dense_artifact_validity": corpus.rag_dense_artifact_validity,
            "embedding_index_version": corpus.rag_embedding_index_version or EMBEDDING_INDEX_VERSION,
            "embedding_cache_dir_identity": corpus.rag_embedding_cache_dir_identity,
        }

    def _remember_retrieval_result(self, result: RetrievalResult) -> RetrievalResult:
        self.last_retrieval_route = result.retrieval_route
        self.last_embedding_model_id = result.embedding_model_id
        self.last_retrieval_corpus_fingerprint = result.corpus_fingerprint
        return result

    def _empty_corpus_result(
        self,
        request: RetrievalRequest,
        metadata: dict[str, Any],
    ) -> RetrievalResult:
        return _retrieval_result_degraded_empty_corpus(
            request=request,
            **metadata,
            embedding_reason_codes=self.corpus.rag_dense_load_reason_codes,
        )

    def _selected_retrieval_hits(
        self,
        request: RetrievalRequest,
        phase: _RetrievalEncodeScorePoolPhase,
    ) -> tuple[list[RetrievalHit], list[str]]:
        reranked = _rerank_retrieval_candidate_pool(
            phase.pool,
            profile_name=phase.qpc.profile_name,
            request=request,
            use_hybrid=phase.hybrid_state.use_hybrid,
            strong_authored_for_module=phase.strong_authored,
        )
        selected_tuples, dup_notes = _dedup_select(
            reranked,
            max_chunks=request.max_chunks,
            profile_name=phase.qpc.profile_name,
        )
        hits = self._build_retrieval_hits_from_selection(
            selected_tuples,
            profile_name=phase.qpc.profile_name,
            published_canonical_in_pool=phase.published_canonical_in_pool,
            audience_scope=request.audience_scope or "",
        )
        return hits, dup_notes

    def _retrieval_result_from_hits(
        self,
        *,
        request: RetrievalRequest,
        phase: _RetrievalEncodeScorePoolPhase,
        hits: list[RetrievalHit],
        metadata: dict[str, Any],
        policy_notes: list[str],
    ) -> RetrievalResult:
        hybrid_state = phase.hybrid_state
        embedding_codes = (
            hybrid_state.query_enc_codes
            if hybrid_state.query_encode_failed
            else self.corpus.rag_dense_load_reason_codes
        )
        if hits:
            return _retrieval_result_ok_with_hits(
                request=request,
                **metadata,
                hits=hits,
                prefix_notes=phase.prefix_notes,
                quality_notes=phase.quality_notes,
                policy_notes=policy_notes,
                retrieval_route=hybrid_state.retrieval_route,
                embedding_model_id=hybrid_state.embedding_mid,
                degradation_mode=hybrid_state.degradation_mode,
                embedding_reason_codes=hybrid_state.query_enc_codes if hybrid_state.query_encode_failed else (),
            )
        return _retrieval_result_fallback_empty_hits(
            request=request,
            **metadata,
            prefix_notes=phase.prefix_notes,
            quality_notes=phase.quality_notes,
            policy_notes=policy_notes,
            retrieval_route=hybrid_state.retrieval_route,
            embedding_model_id=hybrid_state.embedding_mid,
            degradation_mode=hybrid_state.degradation_mode,
            embedding_reason_codes=embedding_codes,
        )

    def _attach_retrieval_authority(
        self,
        result: RetrievalResult,
        request: RetrievalRequest,
    ) -> None:
        result.retrieval_authority = build_retrieval_authority_metadata(
            plan=type(
                "_P",
                (),
                {
                    "authority_scope": "runtime_generation",
                    "audience_scope": request.audience_scope or "runtime",
                    "turn_class": request.turn_class or "unknown",
                    "active_actor": "unknown",
                    "selected_capabilities": tuple(request.selected_capabilities or ()),
                },
            )(),
            retrieval_policy_version=RETRIEVAL_POLICY_VERSION,
            corpus_fingerprint=result.corpus_fingerprint,
            authority_level="retrieved_unverified",
        )

    def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        """``retrieve`` — see implementation for behaviour and contracts.

        Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.

        Args:
            request: ``request`` (RetrievalRequest); meaning follows the type and call sites.

        Returns:
            RetrievalResult:
                Returns a value of type ``RetrievalResult``; see the function body for structure, error paths, and sentinels.
        """
        if request.domain not in DOMAIN_CONTENT_ACCESS:
            raise RetrievalDomainError(f"Unknown retrieval domain: {request.domain}")
        metadata = self._dense_retrieval_metadata()

        if not self.corpus.chunks:
            return self._remember_retrieval_result(
                self._empty_corpus_result(request, metadata)
            )

        phase = _run_retrieval_encode_score_pool_phase(self, request)
        policy_notes: list[str] = [f"retrieval_policy_version={RETRIEVAL_POLICY_VERSION}"]
        policy_notes.extend(phase.hard_policy_notes)
        hits, dup_notes = self._selected_retrieval_hits(request, phase)
        _append_dedup_suppression_quality_notes(phase.quality_notes, dup_notes)
        result = self._retrieval_result_from_hits(
            request=request,
            phase=phase,
            hits=hits,
            metadata=metadata,
            policy_notes=policy_notes,
        )
        self._attach_retrieval_authority(result, request)
        return self._remember_retrieval_result(result)


def _run_retrieval_encode_score_pool_phase(
    retriever: ContextRetriever,
    request: RetrievalRequest,
) -> _RetrievalEncodeScorePoolPhase:
    """Describe what ``_run_retrieval_encode_score_pool_phase`` does in one
    line (verb-led summary for this function).
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        retriever: ``retriever`` (ContextRetriever); meaning follows the type and call sites.
        request: ``request`` (RetrievalRequest); meaning follows the type and call sites.
    
    Returns:
        _RetrievalEncodeScorePoolPhase:
            Returns a value of type ``_RetrievalEncodeScorePoolPhase``; see the function body for structure, error paths, and sentinels.
    """
    c = retriever.corpus
    hybrid_state = _resolve_retrieval_hybrid_encoding_state(
        c,
        request,
        embedding_index_ready=retriever._embedding_ready(),
        embedding_model_id=retriever._embedding_model_id,
    )
    qpc = _build_retrieval_query_profile_context(request)
    prefix_notes = _build_retrieval_prefix_notes(c, hybrid_state=hybrid_state)
    quality_notes = _build_retrieval_quality_seed_notes(w_dense=qpc.w_dense, w_sparse=qpc.w_sparse)
    candidates = retriever._score_initial_candidates(
        request,
        allowed_classes=qpc.allowed_classes,
        query_terms=qpc.query_terms,
        query_norm=qpc.query_norm,
        use_hybrid=hybrid_state.use_hybrid,
        query_vec=hybrid_state.query_vec,
        profile_name=qpc.profile_name,
        profile_boosts=qpc.profile_boosts,
        canonical_weight=qpc.canonical_weight,
        w_dense=qpc.w_dense,
        w_sparse=qpc.w_sparse,
    )
    pool, hard_policy_notes, strong_authored, published_canonical_in_pool, pool_sz_note = (
        _sorted_candidates_to_hard_filtered_pool(
            candidates,
            request=request,
            profile_name=qpc.profile_name,
        )
    )
    quality_notes.append(pool_sz_note)
    return _RetrievalEncodeScorePoolPhase(
        qpc=qpc,
        hybrid_state=hybrid_state,
        prefix_notes=prefix_notes,
        quality_notes=quality_notes,
        pool=pool,
        hard_policy_notes=hard_policy_notes,
        strong_authored=strong_authored,
        published_canonical_in_pool=published_canonical_in_pool,
    )
