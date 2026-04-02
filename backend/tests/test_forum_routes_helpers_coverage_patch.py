"""Helper and moderation-route coverage for forum_routes."""

from __future__ import annotations

from datetime import datetime, timezone

from app.api.v1.forum_routes import (
    _enrich_report_dict,
    _parse_int,
    _validate_category_title_length,
    _validate_content_length,
    _validate_title_length,
)
from app.extensions import db
from app.models import ForumCategory, ForumPost, ForumReport, ForumThread, User


def test_parse_int_variants():
    assert _parse_int(None, 7) == 7
    assert _parse_int("3", 1, min_val=1, max_val=10) == 3
    assert _parse_int("0", 5, min_val=1) == 5
    assert _parse_int("99", 1, min_val=1, max_val=10) == 10
    assert _parse_int("x", 2) == 2


def test_validate_content_length():
    ok, err = _validate_content_length(123)
    assert ok is False and "string" in (err or "").lower()

    ok2, err2 = _validate_content_length("a")
    assert ok2 is False and "at least" in (err2 or "").lower()

    ok3, err3 = _validate_content_length("hello there")
    assert ok3 is True and err3 is None


def test_validate_title_and_category_title():
    ok, err = _validate_title_length(None)
    assert ok is False

    ok2, err2 = _validate_title_length("ab")
    assert ok2 is False

    ok3, _ = _validate_title_length("valid title here")
    assert ok3 is True

    ok4, err4 = _validate_category_title_length("x")
    assert ok4 is False
    ok5, _ = _validate_category_title_length("Category title ok")
    assert ok5 is True


def test_enrich_report_dict_thread_and_post(app, test_user):
    with app.app_context():
        user, _ = test_user
        cat = ForumCategory(slug="rep-cat", title="RC", is_active=True, is_private=False)
        db.session.add(cat)
        db.session.flush()
        thread = ForumThread(
            category_id=cat.id,
            slug="rep-thread",
            title="Thread Title",
            status="open",
            author_id=user.id,
        )
        db.session.add(thread)
        db.session.flush()
        post = ForumPost(thread_id=thread.id, author_id=user.id, content="Post body text here", status="visible")
        db.session.add(post)
        db.session.flush()

        rt = ForumReport(
            target_type="thread",
            target_id=thread.id,
            reported_by=user.id,
            reason="spam",
            status="open",
        )
        rp = ForumReport(
            target_type="post",
            target_id=post.id,
            reported_by=user.id,
            reason="abuse",
            status="open",
        )
        db.session.add_all([rt, rp])
        db.session.commit()

        dt = _enrich_report_dict(rt)
        assert dt.get("thread_slug") == "rep-thread"
        assert dt.get("target_title") == "Thread Title"

        dp = _enrich_report_dict(rp)
        assert dp.get("thread_slug") == "rep-thread"
        assert "Post body" in (dp.get("target_title") or "")


def test_moderation_recent_reports_and_locked_threads(app, client, moderator_headers, test_user):
    with app.app_context():
        user, _ = test_user
        cat = ForumCategory(slug="mod-api-cat", title="MAC", is_active=True, is_private=False)
        db.session.add(cat)
        db.session.flush()
        thread = ForumThread(
            category_id=cat.id,
            slug="locked-slug",
            title="Locked",
            status="open",
            author_id=user.id,
            is_locked=True,
        )
        db.session.add(thread)
        db.session.flush()
        rep = ForumReport(
            target_type="thread",
            target_id=thread.id,
            reported_by=user.id,
            reason="test",
            status="open",
        )
        db.session.add(rep)
        db.session.commit()

    r1 = client.get("/api/v1/forum/moderation/recent-reports", headers=moderator_headers)
    assert r1.status_code == 200
    data = r1.get_json()
    assert "items" in data
    assert data["total"] >= 1

    r2 = client.get("/api/v1/forum/moderation/locked-threads", headers=moderator_headers)
    assert r2.status_code == 200
    items = r2.get_json().get("items", [])
    assert any(x.get("slug") == "locked-slug" for x in items)


def test_moderation_recently_handled(app, client, moderator_headers, test_user):
    with app.app_context():
        user, _ = test_user
        cat = ForumCategory(slug="handled-cat", title="HC", is_active=True, is_private=False)
        db.session.add(cat)
        db.session.flush()
        thread = ForumThread(
            category_id=cat.id,
            slug="handled-thread",
            title="Handled T",
            status="open",
            author_id=user.id,
        )
        db.session.add(thread)
        db.session.flush()
        now = datetime.now(timezone.utc)
        rep = ForumReport(
            target_type="thread",
            target_id=thread.id,
            reported_by=user.id,
            reason="x",
            status="resolved",
            handled_at=now,
        )
        db.session.add(rep)
        db.session.commit()

    r = client.get("/api/v1/forum/moderation/recently-handled", headers=moderator_headers)
    assert r.status_code == 200
    assert r.get_json().get("total", 0) >= 1


def test_moderation_bulk_threads_invalid_json(client, moderator_headers):
    r = client.post(
        "/api/v1/forum/moderation/bulk-threads/status",
        headers={**moderator_headers, "Content-Type": "application/json"},
        data="not json",
    )
    assert r.status_code == 400
