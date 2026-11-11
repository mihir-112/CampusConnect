# CampusConnect: Your campus. One place.

CampusConnect is a modern college announcement portal built with React, FastAPI, SQLite, and Tailwind CSS. Students can browse, filter, search announcements, view event metadata, download official attachments, and receive real-time unread notifications without creating an account. Authorized college publishers log in securely to draft, publish, manage, and attach documents to notices.

This is a five-member Collaborative Development and Deployment (CDD) project organized cleanly by member ownership.

**Technology Stack:** React 18 · Vite · Tailwind CSS · Python 3.12+ · FastAPI · SQLAlchemy 2.0 · SQLite · Pydantic v2 · JWT Authentication · Argon2 Password Hashing · Pytest · Vitest · React Testing Library · Docker & Docker Compose · GitHub Actions.

Categories: **Examinations, Events, Clubs, General**.

---

## Team Members and Feature Ownership

| Member | Feature Responsibility | Dedicated Feature Folder | Git Branch |
|---|---|---|---|
| **Mihir Sahoo** | Core Backend & Announcement Engine (CRUD, SQLite/SQLAlchemy, Lifecycle) | [`features/core-announcement-engine`](features/core-announcement-engine/) | `feature/core-announcement-engine` |
| **Aariz** | Publisher Authentication (JWT, Argon2, Throttling, Protected Routes) | [`features/aariz-publisher-auth`](features/aariz-publisher-auth/) | `feature/publisher-auth` |
| **Nayeem** | Notice Details & Attachments (Magic Byte Validation, PDF/Posters, Event Data) | [`features/nayeem-notice-details`](features/nayeem-notice-details/) | `feature/notice-details` |
| **Moksh** | Figma-Based Frontend & Student Dashboard (UI Components, Tailwind Tokens) | [`features/moksh-student-dashboard`](features/moksh-student-dashboard/) | `feature/student-dashboard` |
| **Mridul** | Search & Notifications (Sanitized Keyword Query, Filter, Browser-session Bell) | [`features/mridul-search-notifications`](features/mridul-search-notifications/) | `feature/search-notifications` |

---

## Quick Start (Local Development)

### 1. Backend (FastAPI + SQLite)
```powershell
# In PowerShell:
py -m venv venv
venv\Scripts\Activate.ps1
py -m pip install -r backend\requirements-dev.txt

# Create the first publisher account:
py -m backend.cli create-publisher

# (Optional) Seed realistic demo announcements, posters, and PDFs:
py scripts\seed_demo_data.py

# Start FastAPI server (or via uvicorn backend.app.main:app):
py -m uvicorn backend.app.main:app --reload --port 8000
```
API Documentation (Interactive Swagger): <http://127.0.0.1:8000/docs>

### 2. Frontend (React + Vite)
```powershell
# In a second terminal window:
cd frontend
npm install
npm run dev
```
Student Dashboard: <http://localhost:5173>
Publisher Portal: <http://localhost:5173/publisher/login> (Default demo credentials: `editor` / `password123`)

---

## Automated Tests

Run the full automated test suite (100% pass rate):

```powershell
# 1. Backend tests (123 Pytest unit, API & integration tests):
py -m pytest

# 2. Frontend tests (58 Vitest component, routing & mock API tests):
cd frontend
npm test
```

---

## Docker Deployment

To spin up the entire application stack in containers:

```powershell
Copy-Item .env.example .env     # Set a secure SECRET_KEY in .env
docker compose up --build
```
- Student App: <http://localhost:8080>
- FastAPI API & Swagger: <http://localhost:8000/docs>

---

## Project Structure Overview

```text
CampusConnect/
├── backend/app/                 # Core backend: main.py, database/, core/, shared/ (Mihir)
├── frontend/src/                # Single React client: app/, shared/, main.jsx (Moksh)
├── features/
│   ├── core-announcement-engine/    # Mihir's backend, frontend, tests & docs
│   ├── aariz-publisher-auth/              # Aariz's backend, frontend, tests & docs
│   ├── nayeem-notice-details/             # Nayeem's backend, frontend, tests & docs
│   ├── moksh-student-dashboard/           # Moksh's backend, frontend, tests & docs
│   └── mridul-search-notifications/       # Mridul's backend, frontend, tests & docs
├── docs/                        # Architecture, Folder Structure, API, Contribution report
├── scripts/seed_demo_data.py    # Database demo populator with posters and PDF files
├── tests/integration/           # Cross-feature full workflow tests
└── docker-compose.yml           # Multi-container deployment configuration
```

---

## Documentation Links

- [System Architecture](docs/architecture.md)
- [Folder Structure Guide](docs/folder-structure.md)
- [API Documentation](docs/api-documentation.md)
- [Member Contribution Report](docs/contribution-report.md)
- [Database Design & Schema](docs/database-design.md)
- [Walkthrough & Viva Guide](docs/walkthrough-guide.md)
- [Docker Deployment Guide](docs/docker-guide.md)
