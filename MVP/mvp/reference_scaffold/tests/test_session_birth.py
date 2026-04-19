from wos_mvp.session_birth import PublishedArtifactBundle, build_story_session_birth_plan, validate_publish_bound_birth


def test_publish_bound_birth_requires_full_bundle():
    ok, missing = validate_publish_bound_birth({"artifact_id": "a"})
    assert ok is False
    assert "artifact_revision" in missing


def test_story_session_birth_plan_keeps_artifact_bundle():
    artifact = PublishedArtifactBundle(
        artifact_id="artifact-1",
        artifact_revision="rev-7",
        publish_state="published",
        published_at="2026-04-15T12:00:00Z",
        module_id="god_of_carnage",
        content_contract_version="v21",
        binding_source="published_artifact",
    )
    plan = build_story_session_birth_plan(session_id="sess-1", start_scene_id="scene-0", artifact=artifact)
    assert plan.turn_zero_required is True
    assert plan.artifact.artifact_revision == "rev-7"
