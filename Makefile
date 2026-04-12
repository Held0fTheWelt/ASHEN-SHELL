# World of Shadows — convenience targets (GNU Make). Requires Python on PATH.
# Mirrors CI working-directory semantics for backend and world-engine (see docs/dev/contributing.md).

.PHONY: test-backend test-engine test-ai-stack verify-goc-scene-identity

verify-goc-scene-identity:
	python tools/verify_goc_scene_identity_single_source.py

test-backend:
	cd backend && python -m pytest tests/ -q --tb=short

test-engine:
	cd world-engine && python -m pytest tests/ -q --tb=short

# Install editable deps first (same order as .github/workflows/ai-stack-tests.yml).
test-ai-stack: verify-goc-scene-identity
	python -m pip install -q -e "./story_runtime_core" -e "./ai_stack[test]"
	PYTHONPATH=. python -m pytest ai_stack/tests -q --tb=short
