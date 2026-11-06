# Testing guide

| Layer | Tool | Where | Run |
|---|---|---|---|
| Backend and API | pytest + FastAPI TestClient | `features/<feature>/tests/test_*.py` | `py -m pytest` |
| Cross-module journeys | pytest | `tests/integration/` | `py -m pytest tests` |
| React components and pages | Vitest + React Testing Library | `features/<feature>/tests/*.test.jsx` | `cd frontend; npm test` |

## Isolation
Every backend test builds its own app with its own temporary SQLite file and upload folder (`conftest.py`), so the development database is never touched. Frontend tests replace `fetch` with a fake server (`frontend/src/test/utils.jsx`), so no network or backend is needed.

## What is covered
Backend: startup, database creation, foreign keys, error format; announcement create, read, update, publish, unpublish, delete, validation, ownership; login, tokens (forged, expired, revoked), throttling, password hashing and old-hash upgrade; upload, replace, limits, content checks, view, download, privacy of drafts, missing files; search, filters, wildcards, pagination; notifications, per-browser read state; dashboard counts.
Frontend: dashboard cards and tabs, loading/empty/error states, search, pagination, login, protected pages, logout, notification bell and page, detail page and attachments, file picker rules, publisher dashboard actions, announcement form.
Integration: a full publisher-to-student journey over the real API, an ownership test between two publishers, and a check that the response shapes the React app reads still exist.

## Running one feature's tests
```powershell
py -m pytest features\publisher-auth
cd frontend; npx vitest run ../features/publisher-auth
```

## Manual check before presenting
1. Log in; create a draft; confirm students do not see it (open the site in a private window).
2. Attach a poster and a PDF; publish; confirm it appears on the home page, in search and in the bell.
3. Try a `.exe` renamed to `.png`; confirm it is rejected.
4. Narrow the window to phone width.
5. Unpublish, then delete; confirm it disappears everywhere.
Save real screenshots into your `features/<feature>/evidence/` folder.
