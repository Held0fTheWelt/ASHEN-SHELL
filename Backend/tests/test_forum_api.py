"""Forum API tests: visibility, permissions, counters, and reports."""
from datetime import datetime, timezone

import pytest

from app.extensions import db
from app.models import ForumCategory, ForumThread, ForumPost, User


@pytest.mark.usefixtures("app")
def test_hidden_threads_not_listed_for_normal_user(client):
    """Hidden/archived threads must not appear in category listings for normal users."""
    with client.application.app_context():
        # Create category and threads as admin
        cat = ForumCategory(
            slug="public",
            title="Public",
            description="",
            sort_order=0,
            is_active=True,
            is_private=False,
        )
        db.session.add(cat)
        db.session.commit()
        visible_thread = ForumThread(
            category_id=cat.id,
            slug="visible-thread",
            title="Visible",
            status="open",
        )
        hidden_thread = ForumThread(
            category_id=cat.id,
            slug="hidden-thread",
            title="Hidden",
            status="hidden",
        )
        db.session.add_all([visible_thread, hidden_thread])
        db.session.commit()

    # Anonymous request (optional JWT) must not see hidden thread.
    resp = client.get("/api/v1/forum/categories/public/threads")
    assert resp.status_code == 200
    data = resp.get_json()
    slugs = {t["slug"] for t in data["items"]}
    assert "visible-thread" in slugs
    assert "hidden-thread" not in slugs


def test_like_requires_visibility(app, client, auth_headers):
    """Users must not be able to like posts they cannot see (e.g. in private categories)."""
    with app.app_context():
        # auth_headers user is a normal user with ROLE_USER
        user = User.query.filter_by(username="testuser").first()
        assert user is not None
        # Private category (no required_role set -> treated as staff-only)
        cat = ForumCategory(
            slug="private-cat",
            title="Private",
            description="",
            sort_order=0,
            is_active=True,
            is_private=True,
        )
        db.session.add(cat)
        db.session.commit()
        thread = ForumThread(
            category_id=cat.id,
            slug="private-thread",
            title="Private thread",
            status="open",
        )
        db.session.add(thread)
        db.session.commit()
        post = ForumPost(
            thread_id=thread.id,
            author_id=user.id,
            content="secret",
            status="visible",
        )
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    resp = client.post(f"/api/v1/forum/posts/{post_id}/like", headers=auth_headers)
    # Normal user must not be able to like a post in a private/staff-only category.
    assert resp.status_code in (403, 404)


def test_parent_post_validation_same_thread_only(app, client, auth_headers):
    """parent_post_id must exist, belong to same thread, and not exceed depth."""
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        assert user is not None
        cat = ForumCategory(
            slug="cat",
            title="Cat",
            description="",
            sort_order=0,
            is_active=True,
            is_private=False,
        )
        db.session.add(cat)
        db.session.commit()
        t1 = ForumThread(category_id=cat.id, slug="t1", title="T1", status="open")
        t2 = ForumThread(category_id=cat.id, slug="t2", title="T2", status="open")
        db.session.add_all([t1, t2])
        db.session.commit()
        p1 = ForumPost(thread_id=t1.id, author_id=user.id, content="p1", status="visible")
        db.session.add(p1)
        db.session.commit()
        t2_id = t2.id
        parent_id = p1.id

    # parent in different thread -> 400
    resp = client.post(
        f"/api/v1/forum/threads/{t2_id}/posts",
        json={"content": "reply", "parent_post_id": parent_id},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "same thread" in resp.get_json().get("error", "").lower()


def test_counters_after_hide_unhide(app, client, auth_headers):
    """reply_count and last_post metadata must follow visible posts when hiding/unhiding."""
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        assert user is not None
        cat = ForumCategory(
            slug="counter-cat",
            title="Counter",
            description="",
            sort_order=0,
            is_active=True,
            is_private=False,
        )
        db.session.add(cat)
        db.session.commit()
        thread = ForumThread(
            category_id=cat.id,
            slug="counter-thread",
            title="Counter thread",
            status="open",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.session.add(thread)
        db.session.commit()
        p1 = ForumPost(thread_id=thread.id, author_id=user.id, content="first", status="visible")
        p2 = ForumPost(thread_id=thread.id, author_id=user.id, content="second", status="visible")
        db.session.add_all([p1, p2])
        db.session.commit()

        from app.services.forum_service import recalc_thread_counters, hide_post, unhide_post

        recalc_thread_counters(thread)
        db.session.refresh(thread)
        assert thread.reply_count == 1
        assert thread.last_post_id == p2.id

        hide_post(p2)
        db.session.refresh(thread)
        assert thread.last_post_id == p1.id

        unhide_post(p2)
        db.session.refresh(thread)
        assert thread.last_post_id == p2.id

