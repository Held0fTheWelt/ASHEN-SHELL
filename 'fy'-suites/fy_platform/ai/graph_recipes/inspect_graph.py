from __future__ import annotations

from fy_platform.ai.graph_recipes.recipe_base import RecipeResult, RecipeStep


def run_inspect_recipe(adapter, query: str | None = None) -> RecipeResult:
    steps = [RecipeStep('load_latest_run')]
    payload = adapter.inspect(query)
    if query:
        steps.append(RecipeStep('query_index', {'query': query, 'hit_count': payload.get('hit_count', 0)}))
    return RecipeResult(recipe='inspect', ok=bool(payload.get('ok')), steps=steps, output=payload)
