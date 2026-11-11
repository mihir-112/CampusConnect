# Member-wise Contribution Report

Each member's feature work is organized under their dedicated directory in `features/<member-feature>/`.
This table documents what each team member owns, the files they authored, their assigned Git feature branches, and their test coverage.

| Member | Feature Folder | Git Branch | Backend Responsibilities | Frontend Responsibilities | Test Files |
|---|---|---|---|---|---|
| **Mihir Sahoo** | `features/core-announcement-engine` | `feature/core-announcement-engine` | FastAPI app factory (`backend/app/main.py`), database setup, settings, error handlers, event hub, Announcement SQLAlchemy model, CRUD schemas, announcement service, REST routes | API client, publisher dashboard page, announcement creation/edit form, announcement table, statistics cards | `test_app_core.py`, `test_announcement_api.py`, `publisher.test.jsx`, `test_workflows.py` |
| **Aariz** | `features/aariz-publisher-auth` | `feature/publisher-auth` | Publisher and RevokedToken models, Argon2 password hashing, JWT creation & verification, auth dependencies, login throttle, auth routes, CLI helper | AuthContext provider, token storage, login page, ProtectedRoute guard | `test_auth.py`, `auth.test.jsx` |
| **Nayeem** | `features/nayeem-notice-details` | `feature/notice-details` | Attachment model, file type and size validation (magic bytes), file storage service, upload/view/download/delete routes | Announcement detail page, attachment section, embedded PDF modal, attachment uploader, file rules | `test_attachments.py`, `details.test.jsx` |
| **Moksh** | `features/moksh-student-dashboard` | `feature/student-dashboard` | Student dashboard statistics endpoint (`/api/dashboard`) | Figma-based UI implementation, Vite setup, Layout component, HomePage, AnnouncementCard, CategoryNav, Pagination, NotFoundPage, Tailwind design tokens | `test_dashboard.py`, `dashboard.test.jsx`, shared test utilities |
| **Mridul** | `features/mridul-search-notifications` | `feature/search-notifications` | Notification & NotificationRead models, search service (multi-field search & category filter), notification routes & client-id tracking | SearchBar component, search hook (`useAnnouncementSearch`), NotificationBell dropdown, NotificationsPage | `test_search.py`, `test_notifications.py`, `search-notifications.test.jsx` |

---

### Shared Core Infrastructure
- `backend/app/main.py`: Main application factory & route assembler (Maintained by Mihir)
- `backend/app/database/`: Shared SQLAlchemy connection & Base declarative model (Maintained by Mihir)
- `backend/app/core/`: Application settings, constants, and global exception handlers (Mihir)
- `backend/app/shared/`: Decoupled publish/delete event hub, pagination helpers, UTC timestamps (Mihir)
- `frontend/src/app/App.jsx` & `AppRoutes.jsx`: Central routing table connecting all member pages (Moksh)
- `frontend/src/shared/`: Shared Axios client, design tokens, error boundary, test utilities (Moksh & Aariz)
- `docker-compose.yml` & `Dockerfile`: Containerization and DevOps orchestration (Whole Team)
