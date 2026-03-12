# Phase 1 — Delta plan (remaining gaps)

Internal work note. Do not deploy.

## What already exists

### Backend
- **Models:** `NewsArticle.discussion_thread_id`, `WikiPage.discussion_thread_id` (FK to forum_threads); `Notification` (user_id, event_type, target_type, target_id, message, is_read, read_at); `ForumThread`, `ForumPost`, `ForumThreadSubscription`.
- **Migrations:** 022 (wiki/news discussion_thread_id), 023 (notifications) present.
- **News discussion API:** POST/DELETE `/api/v1/news/<id>/discussion-thread` (link/unlink); returns `discussion_thread_id` in response. No exposure in public list/detail serialization.
- **Wiki discussion API:** POST/DELETE `/api/v1/wiki/<page_id>/discussion-thread` in wiki_admin_routes (link/unlink). Public GET `/api/v1/wiki/<slug>` does not include discussion link.
- **Forum:** subscribe/unsubscribe `POST /api/v1/forum/threads/<id>/subscribe`, `DELETE .../unsubscribe`; GET `/api/v1/notifications` (list, paginated, unread_only). No notification creation on post create.
- **Public news:** `list_news` / `get_news_by_id` / `get_news_by_slug` use `_article_to_public_dict()` — no `discussion_thread_id` or discussion link. Management uses same for GET news/<id> and list (editor mode adds translation_statuses only).
- **Public wiki:** `wiki_routes.wiki_page_get` returns title, slug, content_markdown, html, language_code — no discussion link.
- **Forum post create:** `forum_routes.forum_post_create` calls `create_post()` then `log_activity()` — no Notification creation for subscribers.

### Administration tool
- **Paths:** `administration-tool/`, `frontend_app.py`, templates under `templates/`, static under `static/`.
- **Manage News:** `manage/news.html`, `manage_news.js` — list, edit, translations, publish/unpublish, delete. No discussion-thread UI (view/set/clear).
- **Manage Wiki:** `manage/wiki.html`, `manage_wiki.js` — page list, edit translations. No discussion-thread UI.
- **Forum:** `forum/thread.html`, `forum.js` — thread view, posts, reply, report, mod actions. No subscribe/unsubscribe control; no notification list or read state.
- **Config:** `BACKEND_API_URL` default in `frontend_app.py` is PythonAnywhere (remote-first). README says default `http://127.0.0.1:5000` — contradicts.

### Docs/changelog
- README: "Backend/", "Frontend" (should be backend/, administration-tool/ per user); BACKEND_API_URL default stated as localhost.
- CHANGELOG 0.0.22: describes discussion endpoints and notification foundation correctly; path casing mixed (Backend vs backend).
- Other docs: runbook, BackendApi, security, LocalDevelopment reference 127.0.0.1 for local dev (acceptable if marked as local-only).

## What is still missing

1. **Discussion-link integration end-to-end**
   - Public news: API does not expose discussion link; news_detail.html / news.js do not show "Discussion" entry when linked.
   - Public wiki: API does not expose discussion link; wiki_public.html inline script does not show "Discussion" entry.
   - Management: manage_news.js and manage_wiki.js have no UI to view/set/clear linked discussion thread; news/wiki list or detail do not show or load discussion_thread_id.
   - Backend: add safe discussion payload to public news (e.g. `discussion_thread_slug` or `discussion_thread_id` + slug) and public wiki; optionally add `discussion_thread_id` to management news/article and wiki page responses where already authorized.

2. **Real notification creation + usable UI**
   - On forum post create (reply): create Notification for each thread subscriber (except actor); persist; no code path today.
   - Notification list: endpoint exists; no UI in administration-tool or forum to list notifications, open thread/post, or mark read (if we add PATCH/PUT mark-read).
   - Forum thread page: no subscribe/unsubscribe button or state.

3. **Docs/changelog/path drift**
   - README: align with remote-first default (PythonAnywhere as default for initial testing); use backend/ and administration-tool/ consistently; fix BACKEND_API_URL description.
   - CHANGELOG: consistent path casing (backend/, administration-tool/); no contradictory default.
   - Stale "Frontend/" or "Backend/" references: correct or mark legacy.

4. **Focused tests**
   - News discussion link: API link/unlink, public serialization when linked/unlinked.
   - Wiki discussion link: same.
   - Subscribe/unsubscribe flow; notification creation on reply; notification list; any serializer/API used by new UI.

## Files to change (planned)

### Phase 2 (discussion-link)
- Backend: `app/services/news_service.py` (_article_to_public_dict: add discussion link; list_news/get_news editorial response: add discussion_thread_id); `app/api/v1/news_routes.py` (ensure detail returns discussion when present); `app/api/v1/wiki_routes.py` (add discussion link to wiki_page_get response); `app/services/wiki_service.py` or wiki_routes (expose thread slug for page); `app/api/v1/wiki_admin_routes.py` (return discussion_thread_id in page responses if needed).
- Administration-tool: `manage_news.js` (load/save discussion thread: fetch thread list, display current link, set/clear); `manage_wiki.js` (same); `manage/news.html` (section for discussion link); `manage/wiki.html` (section for discussion link); `news.js` (detail: show discussion link when present); `wiki_public.html` or inline script (show discussion link when present).

### Phase 3 (notifications)
- Backend: `app/api/v1/forum_routes.py` (after create_post: create Notifications for subscribers except author); optional: PATCH/PUT notifications/<id>/read or bulk mark-read; `app/services/forum_service.py` (optional: helper to create notifications for thread reply).
- Administration-tool: `forum.js` (subscribe/unsubscribe button on thread page; optional notifications list); `forum/thread.html` (place for subscribe + notifications link); possibly new template or section for notification list.

### Phase 4 (docs)
- README.md, CHANGELOG.md, docs/development/LocalDevelopment.md, docs/runbook.md, docs/BackendApi.md — path and default URL alignment.

### Phase 5 (tests)
- Backend/tests: new or extend test_news_api, test for wiki public, test_forum_api (notifications, subscribe), test_notifications or in forum.

## What we will not refactor

- No change to split architecture (backend = API + DB + auth; administration-tool = Flask + Jinja + static JS).
- No new framework; no mock-only UI; no permission shortcuts.
- No broad unrelated cleanup; no reopening finished areas (forum core, migrations 022/023).
- Remote-first default remains (PythonAnywhere in frontend_app.py); local switching only for troubleshooting.
