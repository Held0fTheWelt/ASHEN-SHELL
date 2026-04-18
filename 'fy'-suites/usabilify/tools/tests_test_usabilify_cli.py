from fy_platform.tests.fixtures_autark import create_target_repo
from usabilify.tools.evaluator import evaluate
from usabilify.tools.template_inventory import inspect_areas


def test_usabilify_inspect_and_evaluate_basic(tmp_path):
    repo = create_target_repo(tmp_path)
    inventory = inspect_areas(repo)
    evaluation = evaluate(repo)
    assert inventory['suite'] == 'usabilify'
    assert len(inventory['areas']) >= 5
    assert evaluation['suite'] == 'usabilify'
    assert 'areas' in evaluation
