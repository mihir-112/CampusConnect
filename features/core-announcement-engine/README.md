# Core Announcement Engine: Core backend architecture and announcement management

**Branch:** `feature/core-announcement-engine`

## What I built
| Area | Files |
|---|---|
| Application foundation | `backend/main.py`, `backend/database.py`, `backend/dependencies.py`, `backend/core/*` |
| Shared contracts | `backend/shared/events.py` (event hub), `schemas.py`, `pagination.py`, `serializers.py` |
| Announcement model | `features/core-announcement-engine/backend/models/announcement.py` |
| Schemas and validation | `features/core-announcement-engine/backend/schemas/announcement.py` |
| Business rules | `features/core-announcement-engine/backend/services/announcement_service.py` (CRUD, draft/publish/unpublish, `published_at`, ownership, stats) |
| REST routes | `features/core-announcement-engine/backend/routes/announcements.py` |
| Frontend | `frontend/src/api/client.js` (shared API client), `features/core-announcement-engine/frontend/`: publisher dashboard with statistics, create/edit form |
| Tests | `features/core-announcement-engine/tests/`: `test_app_core.py`, `test_announcement_api.py`, `publisher.test.jsx`; plus `tests/integration/` |

## Completed tasks
- [x] FastAPI app factory, Swagger documentation at `/docs`
- [x] SQLAlchemy 2 setup, SQLite persistence, foreign keys on
- [x] Announcement model, four-category CHECK constraint
- [x] Pydantic validation with friendly messages
- [x] Create, read, update, delete endpoints
- [x] Draft, publish, unpublish, `published_at` on first publish
- [x] Ownership checks (403) and 404 for other people's drafts
- [x] One error format for every endpoint
- [x] Event hub so notifications and file clean-up plug in without the core importing them
- [x] Publisher dashboard with real statistics and the announcement form
- [x] Backend, frontend and integration tests

## How it connects to the others
publisher-auth's `get_current_publisher` protects my routes. When I publish, unpublish or delete, I announce an event; search-notifications's notifications and notice-details's file clean-up react to it. notice-details's `AttachmentUploader` is used inside my form. search-notifications's search builds on my `published_query()`.

Documentation: [architecture](documentation/architecture.md), [API contract](../../docs/api-documentation.md), [database](../../docs/database-design.md).

## Git history and pull requests
Fill this in from your real GitHub history. Leave a row empty rather than invent one.

| Commit or PR | What it contains | Link |
|---|---|---|
| | | |
| | | |
