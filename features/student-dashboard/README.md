# Student Dashboard: React frontend

**Branch:** `feature/student-dashboard`

## What I built
| Area | Files |
|---|---|
| Frontend foundation | `frontend/vite.config.js`, `frontend/src/main.jsx`, `App.jsx`, `routes/AppRoutes.jsx`, `styles/tokens.css`, `styles/base.css`, `utils/*`, `components/ErrorBoundary.jsx` |
| Layout | `features/student-dashboard/frontend/components/Layout.jsx` (header, mobile menu, footer, skip link) |
| Student pages | `pages/HomePage.jsx`, `NotFoundPage.jsx` |
| Components | `AnnouncementCard`, `CategoryNav`, `CategoryBadge`, `Pagination`, `StateMessage` (loading, empty, error) |
| Styles | `frontend/styles/dashboard.css` |
| Backend | `features/student-dashboard/backend/routes/dashboard.py`: `GET /api/dashboard` (counts per category) |
| Docs | `documentation/design-documentation.md` (wireframes and UI notes) |
| Tests | `features/student-dashboard/tests/test_dashboard.py`, `dashboard.test.jsx`; shared test helpers in `frontend/src/test/utils.jsx` |

## Completed tasks
- [x] Vite + React project, route table, shared design tokens
- [x] Student landing page with search, category tabs with counts, cards, pagination
- [x] Loading, empty and error states with retry
- [x] Responsive layout for phone, tablet, desktop; mobile menu
- [x] Accessible structure: skip link, labelled controls, `aria-current`, focus rings
- [x] Dashboard endpoint and tests
- [x] UI design documentation

## How it connects to the others
My `HomePage` uses search-notifications's search hook and search bar; cards link to notice-details's detail page; `Layout` includes search-notifications's bell and publisher-auth's login/logout. Everyone reuses my `StateMessage` and `CategoryBadge`.

Documentation: [design-documentation.md](documentation/design-documentation.md).

## Git history and pull requests
Fill this in from your real GitHub history. Leave a row empty rather than invent one.

| Commit or PR | What it contains | Link |
|---|---|---|
| | | |
| | | |
