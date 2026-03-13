## Forum Integration Wave — v0.0.27 (2026-03-13)

### Added

- **`resolution_note` on forum reports:** `ForumReport` model gained a `resolution_note TEXT` column
  (migration 027). The field is included in all `to_dict()` outputs. Both `PUT /api/v1/forum/reports/<id>`
  and `POST /api/v1/forum/reports/bulk-status` accept an optional `resolution_note` field in the request
  body; if supplied it is stored on each affected report. The field is visible in the administration tool's
  Reports table as a truncated snippet, and moderators are prompted for a resolution note when resolving or
  dismissing individual reports via the quick-action buttons.

- **Report list pagination and filtering (`GET /api/v1/forum/reports`):** The endpoint now accepts
  `page`, `limit`, `status`, and `target_type` query parameters. The service function `list_reports()`
  returns `(items, total)` and the route includes `page` and `limit` in the JSON envelope alongside `items`
  and `total`. The administration tool loads reports with load-more pagination using these parameters.

- **Moderation log UI (`GET /api/v1/forum/moderation/log`):** The administration tool's forum management
  page initialises a moderation log card (`initModerationLog`) for moderators and admins. The log card
  displays actor, action, target, message snippet, and timestamp for all forum activity log entries. It
  supports load-more pagination with `page` and `limit` parameters.

- **Bulk report status via administration tool:** The Reports table in the administration tool includes
  per-row checkboxes, a select-all checkbox in the table head, a bulk action selector, and an optional bulk
  resolution note input. Submitting fires `POST /api/v1/forum/reports/bulk-status` with `report_ids`,
  `status`, and the optional `resolution_note`.

### Changed

- **`POST /api/v1/forum/reports` request shape corrected:** The correct body is
  `{ target_type, target_id, reason }`. Earlier Postman examples used `post_id` and `comment` fields which
  are not accepted by the backend. The Postman collection has been updated to match the actual API contract.

- **`PUT /api/v1/forum/reports/<id>` body extended:** The request body now documents `resolution_note` as
  an optional field alongside `status`.

- **`POST /api/v1/forum/reports/bulk-status` body extended:** The request body now documents
  `resolution_note` as an optional field alongside `report_ids` and `status`.

- **`GET /api/v1/forum/categories/<slug>/threads` response documented:** The response envelope includes
  `items`, `total`, `page`, and `per_page` fields. Thread objects include `author_username`. Moderators and
  admins receive hidden and archived threads that regular users do not see.

### Performance

- **Migration 028 — additional indexes:** Three indexes added to support common query patterns:
  - `ix_forum_posts_status` on `forum_posts(status)` — speeds post visibility filtering.
  - `ix_forum_posts_thread_status` on `forum_posts(thread_id, status)` — speeds thread detail page post
    list queries filtered by status.
  - `ix_forum_threads_status` on `forum_threads(status)` — speeds thread listing visibility filter.
  - `ix_notifications_user_is_read` on `notifications(user_id, is_read)` — speeds unread notification
    count and list queries.

  All four indexes are created idempotently (existence checked via `inspector.get_indexes()` before
  `CREATE INDEX`).

### Fixed

- **`escapeHtml` in `manage_forum.js`:** The forum management JS module defines a local `escapeHtml`
  helper that properly escapes `&`, `<`, `>`, and `"` before inserting user-originated strings into table
  cells. Resolution note snippets and report reasons rendered in the Reports table are passed through this
  helper.
