from __future__ import annotations

from fy_platform.ai.graph_recipes.recipe_base import RecipeResult, RecipeStep


def run_audit_recipe(adapter, target_repo_root: str) -> RecipeResult:
    steps = [RecipeStep('bind_target', {'target_repo_root': target_repo_root}), RecipeStep('execute_audit')]
    payload = adapter.audit(target_repo_root)
    steps.append(RecipeStep('collect_artifacts', {'ok': payload.get('ok', False)}))
    return RecipeResult(recipe='audit', ok=bool(payload.get('ok')), steps=steps, output=payload)
