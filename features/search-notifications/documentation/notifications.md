# Notifications and read state

## How it works
1. A publisher publishes an announcement. core-announcement-engine's service emits `announcement.published`.
2. My handler creates one row in `notifications` ("New in Events: Tech Fest"). Unpublishing removes it; deleting the announcement removes it by cascade.
3. The React app asks `GET /api/notifications` and shows the bell badge, a dropdown, and a full page.

## Read state, honestly
There are **no student accounts**, so the server cannot know who a student is. A single `is_read` column would mark a notification read for everyone, which would be wrong.

Instead, the first time the app runs it creates a random id (`crypto.randomUUID()`) and keeps it in the browser's `localStorage`. It sends the id as `X-Client-Id` on notification requests. The table `notification_reads (client_id, notification_id)` records what that browser has read.

What this means, and what we do **not** claim:
- Read state is **per browser**, not per student and not synchronised between a student's phone and laptop.
- Clearing browser data, or using a private window, makes every notification unread again.
- The id is random and carries no personal information.
- Marking read needs a valid id (400 otherwise); reading the list without one simply shows everything unread.

## Refresh
The bell refreshes when the window regains focus and once a minute while the tab is visible. There are no websockets.

## Search
`GET /api/search?q=&category=&page=` filters published announcements only, newest first. Keywords match title, description or venue. `%`, `_` and `\` typed by the user are escaped so they search literally. Keywords are capped at 100 characters.
