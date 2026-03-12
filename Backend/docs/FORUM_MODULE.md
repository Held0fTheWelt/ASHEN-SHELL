# Forum module overview (0.0.19 – Phase 0)

## Boundaries and architecture

- **Backend (source of truth)**: Forum lives in `app/forum/` (models, services, routes, permissions).
- **Frontend**: Public and management UIs live in `Frontend/templates/forum/` and `Frontend/static/forum_*.js`, consuming only `/api/v1/forum/*` APIs.
- **Separation**:
  - Forum is independent of News, Wiki, and User Admin, but reuses the shared auth/role/area system.
  - No direct cross-coupling to News/Wiki; future links (e.g. “discuss this article”) are left for later.

## Entities and relationships

- `ForumCategory`
  - `id`, `parent_id` (optional simple hierarchy), `slug`, `title`, `description`,
    `sort_order`, `is_active`, `is_private`, `required_role`, `created_at`, `updated_at`.
  - Relationships: `categories` 1–N `threads`.
  - Access is enforced per category (public vs. requires role vs. private).

- `ForumThread`
  - `id`, `category_id`, `author_id`, `slug`, `title`, `status`,
    `is_pinned`, `is_locked`, `view_count`, `reply_count`,
    `last_post_at`, `last_post_id`, `created_at`, `updated_at`, `deleted_at`.
  - Status: `open`, `locked`, `archived`, `hidden`, `deleted` (hidden/deleted are soft states, not hard-delete).
  - Relationships: belongs to one category; has many posts.

- `ForumPost`
  - `id`, `thread_id`, `author_id`, `parent_post_id` (nullable, only one-level replies),
    `content`, `status`, `like_count`, `created_at`, `updated_at`, `edited_at`, `edited_by`, `deleted_at`.
  - Status: `visible`, `edited`, `hidden`, `deleted` (deleted = soft delete via `deleted_at`).

- `ForumPostLike`
  - `id`, `post_id`, `user_id`, `created_at`, unique `(post_id, user_id)`.

- `ForumReport`
  - `id`, `target_type` (`thread` | `post`), `target_id`, `reported_by`, `reason`,
    `status` (`open` | `reviewed` | `resolved | dismissed`), `handled_by`, `handled_at`, `created_at`.

- `ForumThreadSubscription` (optional, minimal in this iteration)
  - `id`, `thread_id`, `user_id`, `created_at`.

## Roles and behavior

- **Anonymous user**
  - Can read public categories/threads/posts in non-private categories.
  - Cannot create threads/posts, like, or report.

- **Authenticated user (role `user` or higher)**
  - Can read all non-private categories plus those where `required_role` is satisfied.
  - Can create threads in allowed categories (category not locked/private for them).
  - Can reply in open threads (status `open`, not `locked`/`archived`).
  - Can edit own posts within backend-enforced rules (e.g. only non-deleted, non-hidden posts).
  - Can soft-delete own posts if policy allows (we allow soft-delete: mark `deleted_at`, status `deleted`).
  - Can like/unlike visible, non-deleted posts.
  - Can report threads/posts.

- **Moderator**
  - Can moderate in assigned areas/categories (same area-based feature model as News/Wiki where applicable).
  - Actions:
    - hide/unhide posts (status `hidden` vs `visible`).
    - lock/unlock threads (`status` / `is_locked`).
    - pin/unpin threads (`is_pinned`).
    - handle reports (set status, add resolution).
    - soft-delete inappropriate content (threads/posts) via status/`deleted_at`.

- **Admin**
  - All moderator capabilities.
  - Category management: create/edit/delete categories, set `is_active`, `is_private`, `required_role`.
  - Full access to private/staff categories and all reports.

## Soft-delete behavior and lifecycle

- Threads:
  - Normal delete = soft-delete: set `deleted_at` and status `deleted` or `hidden`.
  - Hidden/deleted threads are not listed in public lists; moderators/admins can still see them in moderation views.
  - Hard delete (DB row removal) is reserved for explicit admin-only destructive actions and is not part of the default flows.

- Posts:
  - User delete = soft-delete own post: sets `deleted_at`, status `deleted`, keeps audit trail.
  - Moderation hide = status `hidden` (may or may not set `deleted_at`, but not shown to public).
  - Likes on deleted/hidden posts are not allowed and not shown.

## Slug strategy

- Categories:
  - `slug` is required, unique, URL-safe (lowercase, `[a-z0-9-]`).
  - Generated from title if not provided; uniqueness ensured with suffixes (`-2`, `-3`, ...).

- Threads:
  - `slug` is required, unique per category (or globally, depending on route design); we will enforce uniqueness across all threads for simpler lookup.
  - Generated from title, normalized as for categories, with numeric suffixes if necessary.

## Pagination and search

- Pagination:
  - Category thread lists: `page`, `limit` (default limit ~20), ordered by `is_pinned` desc, `last_post_at` desc.
  - Thread post lists: `page`, `limit`, ordered by `created_at` asc (stable).

- Search:
  - Endpoint for searching thread titles (and optionally post content) via simple `ILIKE` matching.
  - Query parameters: `q`, `page`, `limit`, optional `category` filter.
  - Results respect category access rules and visibility (exclude hidden/deleted where appropriate).

## Moderation rules summary

- Regular users:
  - Cannot post in locked threads.
  - Cannot access private categories unless their role satisfies `required_role`.
  - Cannot edit or delete others’ posts.

- Moderators:
  - May lock/unlock and pin/unpin threads in allowed categories.
  - May hide/unhide posts and threads (status flags, no hard-delete).
  - May change report status; backend logs moderation actions via existing `ActivityLog` where appropriate.

- Admins:
  - Global moderation; no category restrictions.
  - Category CRUD and visibility configuration.

All permission checks are enforced on the backend; frontend only mirrors allowed actions in the UI.

## Thread/post lifecycle states

- Thread:
  - `open` → default, users can reply.
  - `locked` → no new posts; moderators/admins can still modify metadata.
  - `archived` → read-only; not shown in “active” lists except via filters.
  - `hidden`/`deleted` → removed from public listings; visible only to staff.

- Post:
  - `visible` → normal state.
  - `edited` → same as visible but with `edited_at`/`edited_by` populated.
  - `hidden` → hidden from public, visible to staff.
  - `deleted` → soft-deleted; not shown publicly, but retained for audit.

## API contract expectations (high level)

- Base prefix: `/api/v1/forum/...`
- All GET list endpoints return `{ items: [...], total, page, per_page }`.
- Detail endpoints return single objects with derived fields (e.g. `reply_count`, `last_post_at`, `like_count`).
- Mutating endpoints return the updated resource where practical, or `{ message, id }` on deletes.
- Permission failures always return `403` with `{ "error": "..." }`.

