from __future__ import annotations

from fy_platform.ai.schemas.common import ModelRouteDecision


class ModelRouter:
    TASK_POLICIES = {
        'classify': {'tier': 'slm', 'model': 'local-slim-classifier', 'budget': 'cheap', 'repro': 'strict', 'safety': 'advisory'},
        'extract': {'tier': 'slm', 'model': 'local-slim-extractor', 'budget': 'cheap', 'repro': 'strict', 'safety': 'advisory'},
        'cluster': {'tier': 'slm', 'model': 'local-slim-cluster', 'budget': 'cheap', 'repro': 'stable', 'safety': 'advisory'},
        'summarize': {'tier': 'slm', 'model': 'local-slim-summarizer', 'budget': 'cheap', 'repro': 'stable', 'safety': 'advisory'},
        'explain': {'tier': 'llm', 'model': 'local-general-llm', 'budget': 'moderate', 'repro': 'stable', 'safety': 'advisory'},
        'triage': {'tier': 'llm', 'model': 'local-general-llm', 'budget': 'moderate', 'repro': 'stable', 'safety': 'review-first'},
        'compare': {'tier': 'llm', 'model': 'local-general-llm', 'budget': 'moderate', 'repro': 'stable', 'safety': 'advisory'},
        'prepare_fix': {'tier': 'llm', 'model': 'local-code-llm', 'budget': 'expensive', 'repro': 'stable', 'safety': 'review-first'},
        'prepare_context_pack': {'tier': 'slm', 'model': 'local-slim-retrieval-helper', 'budget': 'cheap', 'repro': 'strict', 'safety': 'advisory'},
        'decision': {'tier': 'slm', 'model': 'local-slim-policy-helper', 'budget': 'cheap', 'repro': 'strict', 'safety': 'advisory'},
        'cross_suite_synthesis': {'tier': 'llm', 'model': 'local-general-llm', 'budget': 'moderate', 'repro': 'stable', 'safety': 'advisory'},
    }

    def route(
        self,
        task_type: str,
        *,
        ambiguity: str = 'low',
        evidence_strength: str = 'moderate',
        audience: str = 'developer',
        reproducibility: str = 'stable',
    ) -> ModelRouteDecision:
        policy = dict(self.TASK_POLICIES.get(task_type, {'tier': 'slm', 'model': 'local-slim-default', 'budget': 'cheap', 'repro': 'strict', 'safety': 'advisory'}))
        reasons = [f'policy_route:{task_type}']

        if ambiguity in {'high', 'user-input'} and task_type in {'triage', 'explain', 'decision'}:
            policy['tier'] = 'llm'
            policy['model'] = 'local-general-llm'
            policy['budget'] = 'moderate'
            reasons.append('ambiguity_escalation')
        if evidence_strength == 'weak' and task_type in {'prepare_fix', 'decision'}:
            policy['tier'] = 'slm'
            policy['model'] = 'local-slim-policy-helper'
            policy['budget'] = 'cheap'
            policy['safety'] = 'abstain-first'
            reasons.append('weak_evidence_downgrade')
        if audience in {'manager', 'operator'} and task_type == 'explain':
            reasons.append(f'audience:{audience}')
        if reproducibility == 'strict':
            policy['repro'] = 'strict'
            reasons.append('strict_reproducibility')

        fallback = ['deterministic-fallback']
        if policy['tier'] == 'llm':
            fallback = ['local-slim-default', 'deterministic-fallback']
        elif policy['model'] != 'local-slim-default':
            fallback = ['local-slim-default', 'deterministic-fallback']

        return ModelRouteDecision(
            task_type=task_type,
            selected_tier=policy['tier'],
            selected_model=policy['model'],
            reason=';'.join(reasons),
            budget_class=policy['budget'],
            fallback_chain=fallback,
            reproducibility_mode=policy['repro'],
            safety_mode=policy['safety'],
            estimated_cost_class=policy['budget'],
        )
