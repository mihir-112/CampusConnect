# Project proposal: CampusConnect, "Your campus. One place."

## Problem statement
College announcements are distributed through disconnected communication channels such as WhatsApp groups, emails, department notices, physical notice boards and informal classroom announcements. Students frequently miss important information because announcements are scattered across different platforms.

CampusConnect addresses this problem by providing a centralized college announcement portal where students can conveniently view important college updates in one place.

## Objectives
1. Give students one place to read every college announcement, without creating an account.
2. Let authorised publishers create, edit, draft, publish, unpublish and delete announcements.
3. Support posters and PDF documents with safe storage, preview and download.
4. Make announcements easy to find through keyword search and four fixed categories.
5. Tell students when something new is published.
6. Build it as a five-member team using Git, GitHub, CI/CD and Docker.

## Existing system
Notices are spread over WhatsApp groups, e-mail, paper boards and word of mouth. There is no single list, no search, no history and no way to tell what is new.

## Proposed system
A web portal with a React front end and a FastAPI back end with an SQLite database. Students browse freely. Publishers log in to manage announcements. Four categories: Examinations, Events, Clubs, General.

## Scope
In scope: the features above. **Out of scope** (deliberately): college ERP, attendance, learning management, social networking, student registration, chat.

## Technology
React + Vite + React Router (Node.js/npm), FastAPI + Pydantic + SQLAlchemy + SQLite (Uvicorn), JWT + Argon2, pytest, Vitest + React Testing Library, GitHub Actions, Docker Compose.

## Team
| Member | Responsibility |
|---|---|
| Mihir Sahoo | Core backend architecture and announcement management |
| Aariz | Publisher authentication and security |
| Nayeem | Announcement details and document management |
| Moksh | React frontend and student dashboard |
| Mridul | Search, filtering and notifications |
