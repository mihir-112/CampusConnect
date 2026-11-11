# Phase 1: Audit of the existing Flask project and migration map

This audit was done on the uploaded `CampusConnect.zip` **before** any change was made. The original zip is untouched; the migrated project is a separate tree.

## Existing architecture
Flask 3 application factory, Flask-SQLAlchemy + SQLite, Jinja templates, Flask-Login (session cookies), Flask-WTF (forms + CSRF), pytest. Dependencies pointed `routes -> services -> models`. 88 files, about 3,300 lines. **Baseline: all 111 existing tests passed** before migration began.

## Feature inventory (everything here is preserved)
| Feature | Where it lived in Flask | Where it lives now |
|---|---|---|
| Four fixed categories | `app/constants.py`, DB CHECK constraint | `backend/core/constants.py`, same DB CHECK, `frontend/src/utils/constants.js` |
| Student browsing without login | `routes/dashboard.py`, `templates/dashboard.html` | `GET /api/search`, `features/student-dashboard/frontend/pages/HomePage.jsx` |
| Notice detail page | `routes/notices.py`, `notice_detail.html` | `GET /api/announcements/{id}`, `features/notice-details/frontend/pages/AnnouncementDetailPage.jsx` |
| Publisher login/logout | `routes/auth.py` (session cookie) | `/api/auth/*` with JWT, `features/publisher-auth/` |
| Publisher dashboard | `routes/announcements.py` `admin.dashboard` | `GET /api/publisher/announcements` + `PublisherDashboardPage.jsx` (now with real statistics) |
| Create / edit / delete | `admin.create`, `admin.edit`, `admin.delete` | `POST/PUT/DELETE /api/announcements`, `AnnouncementFormPage.jsx` |
| Draft, publish, unpublish | `is_published`, `set_published` | same rules, `PATCH .../publish` and `.../unpublish` |
| `published_at` set on first publish | `announcement_service._apply_publish` | same behaviour, covered by a test |
| Ownership checks (403) | `_own_announcement` | `announcement_service.get_owned` |
| Poster and PDF upload | `attachment_service` | `features/notice-details/backend/services/attachment_service.py` |
| Files outside `static/`, random names | `UPLOAD_FOLDER` | `UPLOAD_DIR`, same approach |
| Magic-byte file check | `_signature_matches` | kept |
| Drafts' files hidden | `notices._serve` | `/api/attachments/{id}` checks visibility |
| Search and category filter | `search_service` | `GET /api/search`, LIKE wildcards still escaped |
| Notifications and bell | `notification_service`, `notifications.js` | `features/search-notifications/`, `NotificationBell.jsx` |
| Read state per browser, honestly | Flask session | Random browser id (`X-Client-Id`) stored server-side; see `features/search-notifications/documentation/notifications.md` |
| `create-publisher` command | `flask create-publisher` | `py -m backend.cli create-publisher` |
| Tests with temporary database | `conftest.py` | `conftest.py` (per-test app and temp SQLite file) |
| Docker with persistent volume | `Dockerfile`, compose | two images (backend, frontend) and one data volume |

## Same database schema
Table and column names are unchanged (`publishers`, `announcements`, `attachments`, `notifications`). Two small tables are new: `notification_reads` and `revoked_tokens`. An existing `campusconnect.db` therefore opens as it is; the new tables are added on first start.

## Conflicts with the requested architecture, and the smallest safe fix
| Conflict | Resolution |
|---|---|
| Flask sessions + CSRF cookies | Replaced by JWT in the `Authorization` header. Without cookies CSRF does not apply (see `features/publisher-auth/documentation/security.md`). |
| Publisher passwords were Werkzeug scrypt hashes | Verified as before, then upgraded to Argon2 on the next login, so existing publishers keep their passwords. |
| Notification read state lived in the Flask session | The React app has no server session, so each browser sends a random id and the server stores read receipts. Still per browser, never claimed to be per student. |
| Members' folders held only docs and tests; code was in one shared `app/` | Code organized into `features/<feature>/backend` and `features/<feature>/frontend`, wired together through documented interfaces. |
| Jinja pages and `static/js` | Rewritten as React pages and components. Same layout, wording and colours. |

## Missing functionality found (added)
- Real statistics on the publisher dashboard (counts by status and category).
- Document preview (PDF in a frame) and a separate download link.
- Removing an attachment through the API.
- Login throttling after repeated failures, and real token revocation on logout.
- Frontend tests (none existed), CI jobs for Node, and a frontend Docker image.

## Risks noted
1. Member code lives outside `frontend/`, so Vite needed a small resolver plugin (`frontend/vite.config.js`).
2. Tokens in `sessionStorage` are readable by injected scripts; mitigated by React's escaping, no `dangerouslySetInnerHTML` anywhere, and short token life.
3. SQLite allows one writer at a time. That is fine for a college notice board.
