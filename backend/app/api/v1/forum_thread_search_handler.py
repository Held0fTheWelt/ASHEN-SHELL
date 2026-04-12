"""Forum thread search — route entry delegates to phased implementation (DS-021)."""

from __future__ import annotations


def run_forum_thread_search():
    """
    Search over thread titles and optionally post content with filters.
    Same contract as ``forum_routes.forum_search`` (OpenAPI / status codes).
    """
    from app.api.v1.forum_thread_search_phases import execute_forum_thread_search

    return execute_forum_thread_search()
