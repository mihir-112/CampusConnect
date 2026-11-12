# Search & Notifications: Search, filtering and notifications

**Branch:** `feature/search-notifications`

## What I built
| Area | Files |
|---|---|
| Models | `features/search-notifications/backend/models/notification.py` (`notifications`, `notification_reads`) |
| Search | `services/search_service.py`, `routes/search.py` (`GET /api/search`) |
| Notifications | `services/notification_service.py`, `routes/notifications.py` |
| Frontend | `features/search-notifications/frontend/`: `SearchBar`, `NotificationBell`, `NotificationsPage`, `useAnnouncementSearch`, `NotificationsContext`, `clientId.js`, API modules |
| Tests | `features/search-notifications/tests/test_search.py`, `test_notifications.py`, `search-notifications.test.jsx` |

## Completed tasks
- [x] Keyword search over title, description, venue (case-insensitive, wildcards escaped)
- [x] Category filter, combined with keyword, newest first, pagination
- [x] Notification created on publish, removed on unpublish or delete
- [x] Unread count, list, mark one and mark all as read
- [x] Read state per browser without student accounts
- [x] Search bar, bell with unread badge, notifications page
- [x] Tests and documentation

## How it connects to the others
I subscribe to core-announcement-engine's publish and unpublish events, so his code never imports mine. My search builds on his `published_query()`. student-dashboard's home page uses my hook and search bar; the layout shows my bell.

Documentation: [notifications.md](documentation/notifications.md).

## Git history and pull requests
Fill this in from your real GitHub history. Leave a row empty rather than invent one.

| Commit or PR | What it contains | Link |
|---|---|---|
| | | |
| | | |
