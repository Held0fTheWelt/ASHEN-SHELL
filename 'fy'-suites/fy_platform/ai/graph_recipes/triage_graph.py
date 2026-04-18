from __future__ import annotations

from fy_platform.ai.graph_recipes.recipe_base import RecipeResult, RecipeStep


def run_triage_recipe(adapter, query: str | None = None) -> RecipeResult:
    steps = [RecipeStep('route_model'), RecipeStep('triage_query', {'query': query or ''})]
    payload = adapter.triage(query)
    return RecipeResult(recipe='triage', ok=bool(payload.get('ok')), steps=steps, output=payload)
