You are Claude (Haiku 4.5) executing an implementation phase with cost-optimized agent orchestration.

Mission:
Implement Community Analytics & Dashboard Enhancement for World of Shadows.
Add operational visibility into community health, user engagement, and content trends for moderators and administrators.

This is a standalone, well-scoped implementation phase (v0.0.33 → v0.0.34).
Do NOT redesign existing systems. Build on proven patterns.
Keep architecture intact. Add observability, not complexity.

Current repository reality:
- backend path: backend/
- administration-tool path: administration-tool/
- Activity logging already exists and records all moderation actions
- User roles: user, moderator, editor, admin with role_level hierarchy
- Forum has threads, posts, tags, categories with visibility rules
- News and Wiki articles exist with publication status
- Moderation reports and queue already implemented
- Test coverage: 85% gate enforced

Hard scope restriction:
Implement ONLY these analytics and dashboard features:
1. Backend analytics endpoints for community metrics
2. Admin dashboard analytics views (threads, posts, users, tags, reports)
3. Moderator dashboard summary (queue status, recent actions, trends)
4. Activity timeline visualization
5. User engagement metrics (activity levels, contribution patterns)
6. Content performance (popular threads, trending tags)
7. Dashboard filters and date range selection
8. Optional: Basic charts using Chart.js or similar lightweight library

Non-negotiable rules:
- keep current split architecture intact (backend API + administration-tool frontend)
- backend = Flask API endpoints for analytics data
- administration-tool = Jinja2 templates + vanilla JS for dashboard views
- do NOT introduce React, Vue, or SPA frameworks
- do NOT weaken permissions or expose sensitive user data
- do NOT touch forum moderation, auth, or core business logic
- do NOT leave TODO placeholders
- do NOT overclaim completion
- use English for code, comments, changelog entries, commit messages

Execution mode:
- do the work
- do not ask for confirmation on non-blocking choices
- after each phase, give required gate report, then continue automatically
- if no blocking contradiction, continue through all phases

PHASE 1 — Specification & Data Model
Inspect current activity logging, user data, and moderation patterns.
Design what metrics matter for community health.

Required outcomes:
- Define 8-10 key metrics (community health dashboard):
  - Daily active users
  - New threads/posts per day
  - Popular tags (by thread count)
  - Average response time on reports
  - Most active categories
  - Top contributors
  - Moderation actions timeline
  - Content age distribution (freshness)
- List all analytics queries needed (no N+1 patterns)
- Design dashboard layout for admin and moderator roles
- Identify which data is already available, what needs database querying

Required analytics queries:
- Date range filtering (last 7 days, 30 days, 90 days, custom)
- User activity aggregation (by role, by activity level)
- Content metrics (threads, posts, news, wiki articles created per day)
- Tag usage trends
- Moderation queue metrics (reports received, resolved, pending)
- Category performance (thread/post counts, last activity)

Rules:
- use existing ActivityLog table for moderation action trends
- use ForumThread, ForumPost, NewsArticle, WikiPage for content metrics
- leverage existing User, Role tables for user metrics
- no new tables required; aggregate from existing schema
- all queries must be efficient (indexed columns, no full table scans)

REVIEW GATE AFTER PHASE 1:
Report only:
- exact metrics chosen (8-10)
- exact dashboard sections defined (admin vs moderator views)
- exact backend endpoints needed (count)
- exact queries to be implemented
- no new database schema required? yes/no
- commit hash (if any schema inspection changes)

Then commit and continue automatically.

PHASE 2 — Backend Analytics Endpoints
Implement Flask API routes to serve analytics data.

Required outcomes:
- New endpoint: GET /api/v1/admin/analytics/summary
  - Returns: user counts, thread/post counts, report queue status, top tags
  - Query params: date_from, date_to (defaults to last 30 days)
  - Requires: admin role
- New endpoint: GET /api/v1/admin/analytics/timeline
  - Returns: daily activity counts (threads, posts, reports, moderation actions)
  - Query params: date_from, date_to, metric (threads/posts/reports/actions)
  - Requires: admin or moderator role
- New endpoint: GET /api/v1/admin/analytics/users
  - Returns: top contributors, most active users, user count by role
  - Query params: limit (1-100), sort_by (contributions/activity/joined)
  - Requires: admin role
- New endpoint: GET /api/v1/admin/analytics/content
  - Returns: popular tags, most discussed threads, trending content
  - Query params: date_from, date_to, limit
  - Requires: admin or moderator role
- New endpoint: GET /api/v1/admin/analytics/moderation
  - Returns: report queue status, resolution trends, moderator activity
  - Query params: date_from, date_to
  - Requires: admin or moderator role
- All responses: include metadata (query_date, date_range, result_count)

Implementation patterns:
- Use service layer (analytics_service.py) for query logic
- Batch queries where possible (avoid N+1)
- Cache results for up to 5 minutes (same query within 5min window reuses cached data)
- Rate limit: 30 per minute for analytics endpoints
- All queries respect visibility rules (moderators see only their queue, etc.)

Rules:
- no permission leaks (moderators can't see all user details, only activity counts)
- all dates in UTC
- all timestamps in ISO 8601 format
- error handling: 400 for bad date range, 403 for permission, 500 for query failure
- return empty arrays/0 counts if no data (not errors)

REVIEW GATE AFTER PHASE 2:
Report only:
- exact endpoints implemented
- exact query patterns used
- exact permission model enforced
- exact caching strategy
- performance: test query on 10k+ records confirms <500ms response
- commit hash

Then commit and continue automatically.

PHASE 3 — Admin Dashboard Views
Implement dashboard pages in administration-tool for analytics visualization.

Required outcomes:
- New route: /manage/analytics (requires admin role)
- Dashboard layout:
  - Header: date range picker, role-aware summary cards (DAU, threads, reports)
  - Left panel: metric selector (timeline, users, content, moderation)
  - Main panel: metric-specific view
  - Right panel: filters and export options (optional)
- Timeline view:
  - Line chart or bar chart (Chart.js) showing daily activity
  - Y-axis: metric count (threads, posts, reports)
  - X-axis: date range
  - Legend for multiple metrics
  - Hover tooltip showing exact values
- Users view:
  - Table: top contributors (username, role, thread count, post count, join date)
  - Sortable columns
  - Filter by role dropdown
- Content view:
  - Popular tags section (tag name, thread count, last updated)
  - Trending threads section (thread title, author, replies, last activity)
  - Content age distribution (freshness: new, recent, old)
- Moderation view:
  - Report queue status (pending, in-review, resolved counts)
  - Recent actions timeline (who did what, when, on what)
  - Resolution time metrics

Template structure:
- manage_analytics.html (main template)
- static/manage_analytics.js (all logic)
- static/css/manage_analytics.css (styling, minimal)
- Use FrontendConfig.apiFetch() for all API calls
- Use escapeHtml() for user-controlled content
- No hardcoded data; all from backend

Interaction patterns:
- Date range picker: preset buttons (last 7d, 30d, 90d) + custom date inputs
- Metric selector: buttons to switch views, active state styling
- Filters: dropdown for role, category, etc. (context-dependent)
- Export: optional "Export as CSV" button for data export (scope: if easy, skip if time-constrained)

Rules:
- responsive design (works on tablet, desktop; mobile not required)
- graceful degradation if Chart.js unavailable (show tables instead)
- loading states (spinner/skeleton) while fetching
- error handling: show user-friendly error message, not API errors
- accessibility: semantic HTML, ARIA labels where needed
- performance: render <1s on typical data, lazy-load charts if needed

REVIEW GATE AFTER PHASE 3:
Report only:
- exact pages created
- exact FrontendConfig.apiFetch calls made
- exact chart library used (Chart.js or alternative)
- exact filters/interactions implemented
- manual verification: screenshots or description of working dashboard
- commit hash

Then commit and continue automatically.

PHASE 4 — Moderator Dashboard Summary
Implement focused moderator view (lighter version of admin dashboard).

Required outcomes:
- New route: /manage/moderator-dashboard (requires moderator role)
- Moderator view focuses on actionable data:
  - Report queue summary (pending count, recent reports)
  - Recent moderation actions (last 10 by me and other mods)
  - Assigned reports list (if assignment feature exists)
  - Quick stats: reports resolved today, posts hidden, threads locked
  - Trending violations (if tracked)
- Design: simpler than admin dashboard, action-focused
- No user analytics or global community stats (only moderation-relevant data)
- Link to full report queue and moderation log

Rules:
- moderators can only see their own actions or reports in their queue
- no cross-moderator stats (privacy)
- refresh data every 30 seconds (auto-update)
- red/amber/green status indicators for queue health

REVIEW GATE AFTER PHASE 4:
Report only:
- exact moderator dashboard pages created
- exact data exposed (no leaks?)
- exact auto-refresh frequency
- manual verification: working moderator view
- commit hash

Then commit and continue automatically.

PHASE 5 — Tests & Verification
Add analytics endpoint and dashboard tests.

Required at minimum:
- Backend tests (pytest):
  - test_analytics_summary_endpoint (admin access, returns expected fields)
  - test_analytics_timeline_endpoint (date filtering, valid data)
  - test_analytics_users_endpoint (top users returned, sorted correctly)
  - test_analytics_content_endpoint (tags ranked by count, threads trending)
  - test_analytics_moderation_endpoint (report queue status, action timeline)
  - test_analytics_permission_checks (moderator can't access admin endpoints)
  - test_analytics_performance (10k+ records, response <500ms)
  - test_analytics_caching (same query twice uses cache)
- Frontend tests (manual or Playwright if available):
  - verify admin dashboard loads, date picker works, metrics switch
  - verify moderator dashboard shows queue, recent actions
  - verify charts render (or fallback to table if Chart.js fails)
  - verify no XSS via escapeHtml on user-controlled data

Rules:
- no placeholder tests
- coverage goal: 85% on new code
- all tests must pass before phase completion

REVIEW GATE AFTER PHASE 5:
Report only:
- exact tests added
- exact commands run (pytest --cov=app --cov-report=term-missing)
- exact pass/fail results
- exact coverage percentage
- any legacy test failures? (unrelated to this work)
- commit hash

Then commit and continue automatically.

PHASE 6 — Documentation & Changelog
Update docs and Postman for new analytics feature.

Required:
- Postman: Add analytics endpoints collection
  - GET /api/v1/admin/analytics/summary (with example response)
  - GET /api/v1/admin/analytics/timeline (with date params)
  - GET /api/v1/admin/analytics/users (with pagination)
  - GET /api/v1/admin/analytics/content (trending data)
  - GET /api/v1/admin/analytics/moderation (queue status)
  - Each with description, required auth, example response
- docs/API_REFERENCE.md: Add "Community Analytics" section
  - Explain each endpoint
  - Permission model
  - Query parameter reference
  - Example use cases
- docs/ADMIN_GUIDE.md: Add "Analytics Dashboard" section (NEW)
  - How to navigate admin analytics
  - How to filter by date range
  - How to interpret charts/trends
  - What metrics mean
- docs/MODERATOR_GUIDE.md: Add "Moderator Dashboard" section (NEW)
  - How to access moderator dashboard
  - Queue status explained
  - Recent actions timeline
- CHANGELOG.md: Add v0.0.34 entry
  - Summary: Community analytics, admin dashboard, moderator summary
  - Features added
  - Endpoints added
  - Tests added
  - Known limitations (if any)

Rules:
- keep docs truthful and clear
- keep changelog concrete
- do not overclaim features
- note any caching behavior or rate limits in docs

REVIEW GATE AFTER PHASE 6:
Report only:
- exact Postman collections added
- exact docs created/updated
- exact changelog entries
- all links/references valid?
- commit hash

Then stop.

Git discipline:
- commit after every completed phase
- keep commits coherent
- format: "phase N: [phase name] - [key work]"

Final report requirements:
1. What was implemented in each phase
2. Exact files changed (all 6 phases)
3. Exact routes/endpoints added
4. Exact dashboard pages added
5. Exact tests added
6. Exact commands run to verify
7. Exact results (coverage %, pass/fail, response times)
8. Any remaining limitations
9. Commit hashes for all 6 phases

Definition of done:
This phase is complete only when:
- Analytics endpoints serve accurate, efficient data
- Admin dashboard visualizes community health metrics
- Moderator dashboard shows actionable queue/moderation data
- All tests pass with 85%+ coverage
- Documentation is complete and accurate
- Postman collection reflects all endpoints
- All review gates were passed with evidence
