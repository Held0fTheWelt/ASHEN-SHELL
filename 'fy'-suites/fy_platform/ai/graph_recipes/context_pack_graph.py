from __future__ import annotations

from fy_platform.ai.graph_recipes.recipe_base import RecipeResult, RecipeStep


def run_context_pack_recipe(adapter, query: str, audience: str = 'developer') -> RecipeResult:
    steps = [RecipeStep('refresh_index'), RecipeStep('build_context_pack', {'query': query, 'audience': audience})]
    payload = adapter.prepare_context_pack(query, audience)
    steps.append(RecipeStep('persist_context_pack', {'hit_count': payload.get('hit_count', 0)}))
    return RecipeResult(recipe='context-pack', ok=True, steps=steps, output=payload)
