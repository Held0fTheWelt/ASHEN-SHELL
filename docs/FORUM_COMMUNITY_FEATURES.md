# Forum Community Features

This document covers user-facing forum features introduced in the forum integration waves:
bookmarks, thread tags, and search/filter options.

---

## Bookmarks

Authenticated users can save threads to a personal bookmark list. Bookmarks are private — only
the bookmarking user can see their own list.

### Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/forum/threads/<thread_id>/bookmark` | User+ | Bookmark a thread (idempotent) |
| `DELETE` | `/api/v1/forum/threads/<thread_id>/bookmark` | User+ | Remove a bookmark |
| `GET` | `/api/v1/forum/bookmarks` | User+ | List bookmarked threads (paginated) |

### Bookmark a thread

```
POST /api/v1/forum/threads/42/bookmark
Authorization: Bearer <jwt>

Response 200:
{ "message": "Bookmarked" }
```

- Idempotent: bookmarking an already-bookmarked thread returns 200 without creating a duplicate.
- Returns 404 if the thread does not exist or the user cannot view it.

### Remove a bookmark

```
DELETE /api/v1/forum/threads/42/bookmark
Authorization: Bearer <jwt>

Response 200:
{ "message": "Unbookmarked" }
```

- Idempotent: removing a bookmark that does not exist still returns 200.

### List bookmarked threads

```
GET /api/v1/forum/bookmarks?page=1&limit=20
Authorization: Bearer <jwt>
```

**Query parameters:**

| Parameter | Default | Max | Description |
|-----------|---------|-----|-------------|
| `page` | 1 | — | Page number (1-based) |
| `limit` | 20 | 100 | Items per page |

**Response:**

```json
{
  "items": [
    {
      "id": 42,
      "slug": "welcome-to-the-community",
      "title": "Welcome to the community",
      "status": "open",
      "is_pinned": false,
      "is_locked": false,
      "is_featured": false,
      "view_count": 120,
      "reply_count": 14,
      "last_post_at": "2026-03-12T18:00:00+00:00",
      "author_username": "shadow_runner",
      "category": { "id": 1, "slug": "general", "title": "General" },
      "tags": [
        { "slug": "welcome", "label": "welcome" }
      ]
    }
  ],
  "total": 5,
  "page": 1,
  "per_page": 20
}
```

- Only threads in active categories are returned.
- Deleted threads are excluded.
- `tags` is omitted when the thread has no tags.
- Ordering: pinned threads first, then by `last_post_at` descending.

### Visibility rules

Bookmarking is only available to non-banned authenticated users. If a bookmarked thread is later
deleted, moved to an inactive category, or otherwise becomes inaccessible, it is silently excluded
from the bookmark list.

### Saved Threads page

A dedicated page at `/forum/saved` displays a user's bookmarked threads in paginated view. Features:

- **Access**: Logged-in users only; bookmark list is private to the user
- **Display**: Thread title (linked), category, reply count, last activity date, tags, and bookmark removal button
- **Pagination**: Standard page/limit controls (default 20 per page)
- **Unbooking**: Click the bookmark button (★) to remove a thread from the saved list
- **Refresh**: Saved list updates immediately after unbooking

This page provides a convenient way to review and manage saved threads without navigating through category views.

---

## Thread Tags

Tags provide a light categorisation layer within the forum. Tags are normalized slug strings stored
in a shared `forum_tags` table and linked to threads via `forum_thread_tags`.

### Tag normalization

When a tag string is submitted, it is normalized as follows:

1. Stripped of leading and trailing whitespace.
2. Lowercased.
3. Non-alphanumeric characters (except hyphens and underscores) are replaced with hyphens.
4. Consecutive hyphens are collapsed to a single hyphen.
5. Leading and trailing hyphens are stripped.

A tag that normalizes to an empty string is silently discarded. Tags are truncated to 64 characters
(label and slug both).

If two different input strings normalize to the same slug, they share a single `ForumTag` row. The
`label` stored is the first-seen human-readable form for that slug.

### Setting tags on a thread

```
PUT /api/v1/forum/threads/<thread_id>/tags
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "tags": ["lore", "main-quest", "spoilers"]
}
```

- Allowed for: thread author, moderators, and admins.
- The `tags` array **replaces** all existing tags on the thread; send an empty array to remove all tags.
- Returns the current set of applied tags after the update.

**Response 200:**

```json
{
  "tags": [
    { "slug": "lore", "label": "lore" },
    { "slug": "main-quest", "label": "main-quest" },
    { "slug": "spoilers", "label": "spoilers" }
  ]
}
```

### Tags in thread responses

Tags appear in the following responses when a thread has at least one tag:

- `GET /api/v1/forum/threads/<slug>` — `tags` array in the thread object.
- `GET /api/v1/forum/bookmarks` — `tags` array per bookmark item.

The category thread list (`GET /api/v1/forum/categories/<slug>/threads`) includes `tags` (array of label strings) and `bookmarked_by_me` (bool) per thread item. Anonymous requests always receive `bookmarked_by_me: false`.

### Tag management (moderator/admin)

`GET /api/v1/forum/tags` lists all tags with thread counts. Requires moderator or admin.

Query params:
- `q` -- optional text filter (matches label or slug)
- `page` -- page number (default 1)
- `limit` -- results per page (default 50, max 100)

Response:

```json
{
  "items": [
    {
      "id": 1,
      "slug": "lore",
      "label": "lore",
      "thread_count": 12,
      "created_at": "2026-03-01T10:00:00+00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 50
}
```

`DELETE /api/v1/forum/tags/<id>` deletes a tag. Requires admin. Returns 409 if the tag is currently associated with any threads.

### Tag editing (user-facing)

Thread authors and moderators can edit tags directly on the thread detail page. When viewing a thread:

- **View tags**: Existing tags are displayed as clickable badges
- **Edit button**: Authors and moderators see an "Edit tags" button next to the tag display
- **Editor interface**: Click to open an inline tag editor with:
  - List of existing tags with individual remove buttons (×)
  - Input field for adding new tags (normalized per tag rules)
  - Save and Cancel buttons
  - Error feedback for invalid input
- **Save**: Click Save to apply tag changes via `PUT /api/v1/forum/threads/<id>/tags`
- **Permissions**: Only thread author, moderators, and admins can edit tags; unauthorized users see tags as read-only

This provides a lightweight way for community members to organize and categorize discussions without requiring admin intervention.

### Searching by tag

Pass the `tag` query parameter to `GET /api/v1/forum/search` to filter results to threads with a
specific tag slug:

```
GET /api/v1/forum/search?tag=lore&page=1&limit=20
```

This filter can be combined with `q` (title search), `category`, and `status` filters.

---

## Search and Filters

`GET /api/v1/forum/search` provides a lightweight full-text thread search with optional filters.

### Endpoint

```
GET /api/v1/forum/search
```

Authentication is optional. Anonymous users only see threads in public categories.

### Query parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `q` | — | Search term matched against thread titles via `ILIKE %q%`. Truncated to 200 characters. |
| `page` | 1 | Page number (1-based). |
| `limit` | 20 | Items per page (max 100). |
| `category` | — | Filter by category slug (exact match). |
| `status` | — | Filter by thread status: `open`, `locked`, `archived`, `hidden`. |
| `tag` | — | Filter by tag slug (exact match). |
| `include_content` | 0 | Set to `1` or `true` to also search post content (requires `q` with length ≥ 3). |

### Behavior notes

- A request with no `q`, no `category`, no `status`, and no `tag` returns an empty result
  immediately (no unbounded scans).
- Deleted threads are excluded for non-moderator users.
- Post-content search (`include_content=1`) uses a subquery to find threads that contain matching
  posts; it only executes when `q` is at least 3 characters.
- Results are filtered by the caller's visibility permissions after the SQL query.

### Response

```json
{
  "items": [
    {
      "id": 1,
      "slug": "first-thread",
      "title": "First thread",
      "status": "open",
      "is_pinned": true,
      "reply_count": 8,
      "author_username": "admin"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

Ordering: pinned threads first, then `last_post_at` descending, then `id` ascending.

### Category thread list filters

`GET /api/v1/forum/categories/<slug>/threads` accepts `page` and `limit` parameters and returns
a paginated response:

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "per_page": 20
}
```

Each thread object includes `bookmarked_by_me` (bool) and `tags` (array of label strings). Moderators and admins automatically see hidden and archived threads in addition to open and locked threads. Regular users only see open and locked threads. SQL-level visibility filtering is used for pagination accuracy.
