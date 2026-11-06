# CampusConnect — Reorganized Folder Structure Guide

## 1. Overview and Architecture Principles

CampusConnect has been organized into a professional, member-wise feature architecture.
This architecture preserves:
- **Single full-stack application:** Exactly one React application, one FastAPI application, and one shared SQLite database.
- **Clear member ownership:** Each team member's feature resides in their dedicated folder under `features/` containing their frontend components, backend routes/services/models, and test suites.
- **Shared core infrastructure:** Database connection, global application state, authentication helpers, pagination, and shared UI styles reside in `backend/app/` and `frontend/src/shared/`.

---

## 2. Target Directory Layout

```text
CampusConnect/
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI factory & router assembly (Owner: Mihir)
│   │   ├── database/                # SQLite engine & Base model (Owner: Mihir)
│   │   │   ├── __init__.py
│   │   │   └── connection.py
│   │   ├── core/                    # App configuration, constants & error handlers
│   │   │   ├── config.py
│   │   │   ├── constants.py
│   │   │   ├── errors.py
│   │   │   └── __init__.py
│   │   ├── shared/                  # Event hub, pagination, models loader, serializers
│   │   │   ├── events.py
│   │   │   ├── models.py
│   │   │   ├── pagination.py
│   │   │   ├── schemas.py
│   │   │   ├── serializers.py
│   │   │   └── time.py
│   │   ├── cli.py                   # CLI administration commands
│   │   └── dependencies.py          # Global FastAPI dependencies
│   ├── requirements.txt             # Backend production dependencies
│   └── requirements-dev.txt         # Testing and development tools (pytest, httpx)
│
├── frontend/
│   ├── src/
│   │   ├── app/                     # React application root
│   │   │   ├── App.jsx              # Providers (Auth, Notifications) & Error Boundary
│   │   │   └── AppRoutes.jsx        # Unified client router mapping all feature views
│   │   ├── shared/                  # Common frontend utilities & components
│   │   │   ├── api/                 # Axios client with JWT interceptor & abort helpers
│   │   │   ├── components/          # ErrorBoundary and common UI widgets
│   │   │   ├── styles/              # Global Tailwind & design token stylesheets
│   │   │   ├── test/                # Shared test utilities (mockApi, test wrappers)
│   │   │   └── utils/               # Formatting, constants, and document title hooks
│   │   └── main.jsx                 # Vite application mount point
│   ├── index.html                   # HTML template
│   ├── package.json                 # React dependencies and build scripts
│   └── vite.config.js               # Path aliases (@features, @shared, @app) & Vitest config
│
├── features/
│   │
│   ├── mihir-core-announcement-engine/
│   │   ├── backend/
│   │   │   ├── models/announcement.py       # Announcement SQLAlchemy model
│   │   │   ├── routes/announcements.py      # CRUD REST API endpoints
│   │   │   ├── schemas/announcement.py      # Pydantic request/response schemas
│   │   │   └── services/announcement_service.py # Lifecycle & statistics logic
│   │   ├── frontend/
│   │   │   ├── components/AnnouncementTable.jsx, StatsCards.jsx
│   │   │   ├── pages/AnnouncementFormPage.jsx, PublisherDashboardPage.jsx
│   │   │   └── announcementsApi.js
│   │   └── tests/
│   │       ├── test_announcement_api.py, test_app_core.py (Pytest)
│   │       └── publisher.test.jsx (Vitest)
│   │
│   ├── aariz-publisher-auth/
│   │   ├── backend/
│   │   │   ├── models/publisher.py, revoked_token.py
│   │   │   ├── routes/auth.py               # Login, logout, current publisher endpoints
│   │   │   ├── schemas/auth.py              # Auth request & JWT token schemas
│   │   │   ├── security/passwords.py, tokens.py, throttle.py
│   │   │   └── services/auth_service.py     # Argon2 hashing & JWT issuance
│   │   ├── frontend/
│   │   │   ├── auth/AuthContext.jsx, tokenStorage.js, authApi.js
│   │   │   ├── components/ProtectedRoute.jsx
│   │   │   └── pages/LoginPage.jsx
│   │   └── tests/
│   │       ├── test_auth.py (Pytest)
│   │       └── auth.test.jsx (Vitest)
│   │
│   ├── nayeem-notice-details/
│   │   ├── backend/
│   │   │   ├── models/attachment.py         # Attachment model
│   │   │   ├── routes/attachments.py        # Upload, view, download, delete endpoints
│   │   │   ├── schemas/attachment.py
│   │   │   └── services/attachment_service.py # Magic byte validation & secure storage
│   │   ├── frontend/
│   │   │   ├── components/AttachmentSection.jsx, AttachmentUploader.jsx
│   │   │   ├── pages/AnnouncementDetailPage.jsx
│   │   │   ├── attachmentsApi.js
│   │   │   └── fileRules.js                 # Frontend file size & type constraints
│   │   └── tests/
│   │       ├── test_attachments.py (Pytest)
│   │       └── details.test.jsx (Vitest)
│   │
│   ├── moksh-student-dashboard/
│   │   ├── backend/
│   │   │   └── routes/dashboard.py          # Category metrics & statistics endpoint
│   │   ├── frontend/
│   │   │   ├── components/Layout.jsx, AnnouncementCard.jsx, CategoryNav.jsx, Pagination.jsx
│   │   │   ├── pages/HomePage.jsx, NotFoundPage.jsx
│   │   │   └── styles/dashboard.css         # Figma design implementation
│   │   └── tests/
│   │       ├── test_dashboard.py (Pytest)
│   │       └── dashboard.test.jsx (Vitest)
│   │
│   └── mridul-search-notifications/
│       ├── backend/
│       │   ├── models/notification.py       # Notification & read receipt models
│       │   ├── routes/search.py, notifications.py # Search & bell notification routes
│       │   ├── schemas/notification.py
│       │   └── services/search_service.py, notification_service.py
│       ├── frontend/
│       │   ├── components/SearchBar.jsx, NotificationBell.jsx
│       │   ├── hooks/NotificationsContext.jsx, useAnnouncementSearch.js
│       │   └── pages/NotificationsPage.jsx
│       └── tests/
│           ├── test_search.py, test_notifications.py (Pytest)
│           └── search-notifications.test.jsx (Vitest)
│
├── docs/
│   ├── architecture.md                      # Full architectural specification
│   ├── folder-structure.md                  # This document
│   ├── api-documentation.md                 # Complete OpenAPI/REST API guide
│   ├── contribution-report.md               # Member-by-member breakdown
│   ├── database-design.md                   # SQLite schema, tables & indexes
│   ├── docker-guide.md                      # Containerization instructions
│   └── walkthrough-guide.md                 # 8-minute demo & viva run-through
│
├── scripts/
│   └── seed_demo_data.py                    # Demo database populator
├── .github/
│   └── workflows/ci.yml                     # Automated Pytest & Vitest CI pipeline
├── Dockerfile                               # Backend Docker container
├── docker-compose.yml                       # Multi-container orchestration
├── README.md                                # Project landing documentation
└── .env.example                             # Environment variable template
```

---

## 3. Team Member Feature Mapping

| Member | Feature Folder | Primary Responsibilities |
|---|---|---|
| **Mihir Sahoo** | `features/mihir-core-announcement-engine` | Overall backend architecture, SQLite/SQLAlchemy setup, announcement CRUD, draft/published lifecycle, publisher dashboard logic |
| **Aariz** | `features/aariz-publisher-auth` | Publisher authentication, JWT tokens, Argon2 password hashing, login brute-force throttle, protected routes |
| **Nayeem** | `features/nayeem-notice-details` | Poster and PDF attachments, magic byte validation, PDF viewer/download endpoints, event metadata |
| **Moksh** | `features/moksh-student-dashboard` | Figma visual implementation, student landing page, responsive layouts, Tailwind design tokens, card grid |
| **Mridul** | `features/mridul-search-notifications` | Multi-field sanitized search, category filters, notification bell, per-browser unread count tracking |

---

## 4. Import & Alias Conventions

- **Python:**
  - `features.__init__` provides a dynamic `MetaPathFinder` (`FeaturePackageFinder`) that maps both `features.<member_feature_name>` and legacy aliases to the disk directory.
  - Shared models are consolidated via `backend.app.shared.models.import_all_models()`.
- **Frontend / Vite:**
  - `@features/<member-feature-name>` points to `features/<member-feature-name>`.
  - `@shared` points to `frontend/src/shared`.
  - `@app` points to `frontend/src/app`.
  - `@/` points to `frontend/src`.
