from __future__ import annotations


def test_variant_creation_and_lineage(client, auth_headers):
    response = client.post(
        "/api/v1/improvement/variants",
        headers=auth_headers,
        json={
            "baseline_id": "god_of_carnage",
            "candidate_summary": "Increase de-escalation options in scene transitions.",
            "metadata": {"source": "writers_room"},
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["baseline_id"] == "god_of_carnage"
    assert data["lineage"]["derived_from"] == "god_of_carnage"
    assert data["review_status"] == "pending_review"


def test_sandbox_execution_evaluation_and_recommendation_package(client, auth_headers):
    variant_resp = client.post(
        "/api/v1/improvement/variants",
        headers=auth_headers,
        json={
            "baseline_id": "god_of_carnage",
            "candidate_summary": "Experiment with alternative conflict pacing.",
        },
    )
    variant_id = variant_resp.get_json()["variant_id"]

    experiment_resp = client.post(
        "/api/v1/improvement/experiments/run",
        headers=auth_headers,
        json={
            "variant_id": variant_id,
            "test_inputs": [
                "I argue with measured tone.",
                "I repeat the same accusation again and again.",
                "I try to de-escalate the conflict.",
            ],
        },
    )
    assert experiment_resp.status_code == 200
    payload = experiment_resp.get_json()
    experiment = payload["experiment"]
    recommendation = payload["recommendation_package"]

    assert experiment["sandbox"] is True
    assert experiment["variant_id"] == variant_id
    assert recommendation["candidate"]["variant_id"] == variant_id
    assert recommendation["review_status"] == "pending_governance_review"
    metrics = recommendation["evaluation"]["metrics"]
    assert "guard_reject_rate" in metrics
    assert "trigger_coverage" in metrics
    assert "repetition_signal" in metrics
    assert "structure_flow_health" in metrics
    assert "transcript_quality_heuristic" in metrics


def test_governance_accessibility_lists_recommendation_packages(client, auth_headers):
    response = client.get("/api/v1/improvement/recommendations", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "packages" in data
    assert isinstance(data["packages"], list)
