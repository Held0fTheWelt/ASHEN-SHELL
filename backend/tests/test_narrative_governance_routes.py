"""Contract tests for narrative governance admin APIs."""

from __future__ import annotations

from app.extensions import db
from app.models import NarrativeRevisionCandidate


def test_runtime_config_get_returns_envelope(client, moderator_headers):
    response = client.get("/api/v1/admin/narrative/runtime/config", headers=moderator_headers)
    assert response.status_code == 200
    body = response.get_json()
    assert body["ok"] is True
    assert "data" in body
    assert "meta" in body


def test_runtime_config_post_rejects_invalid_strategy(client, moderator_headers):
    response = client.post(
        "/api/v1/admin/narrative/runtime/config",
        headers=moderator_headers,
        json={"output_validator": {"strategy": "made_up"}},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["ok"] is False
    assert body["error"]["code"] == "invalid_validation_strategy"


def test_revision_transition_invalid_path_returns_409(app, client, moderator_headers):
    with app.app_context():
        row = NarrativeRevisionCandidate(
            revision_id="rev_test_001",
            module_id="god_of_carnage",
            source_finding_id=None,
            target_kind="actor_mind",
            target_ref="veronique",
            operation="replace_clause",
            structured_delta_json={"path": "actor_minds.veronique", "value": "x"},
            expected_effects_json=["stability"],
            risk_flags_json=[],
            review_status="pending",
            requires_review=True,
            mutation_allowed=False,
            created_by="system",
        )
        db.session.add(row)
        db.session.commit()

    response = client.post(
        "/api/v1/admin/narrative/revisions/rev_test_001/transition",
        headers=moderator_headers,
        json={"to_status": "promoted", "by_role": "operator"},
    )
    assert response.status_code == 409
    body = response.get_json()
    assert body["ok"] is False
    assert body["error"]["code"] == "invalid_revision_transition"


def test_notifications_rule_upsert_roundtrip(client, moderator_headers):
    response = client.post(
        "/api/v1/admin/narrative/notifications/rules",
        headers=moderator_headers,
        json={
            "rule_id": "notif_rule_test",
            "event_type": "evaluation_failed",
            "condition": {"count": {"$gte": 1}},
            "channels": ["admin_ui"],
            "recipients": ["ops"],
            "enabled": True,
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["ok"] is True
    assert body["data"]["rule_id"] == "notif_rule_test"

    list_response = client.get("/api/v1/admin/narrative/notifications/rules", headers=moderator_headers)
    assert list_response.status_code == 200
    rows = list_response.get_json()["data"]["rules"]
    assert any(item["rule_id"] == "notif_rule_test" for item in rows)
