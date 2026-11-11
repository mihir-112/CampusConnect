# Notification documentation (Mridul)

| Action | Result |
|---|---|
| Publish an announcement | One notification row; unread count rises in every browser that has not read it |
| Open a notification | Marked read in that browser; unread count drops |
| Mark all as read | All recent notifications marked read in that browser |
| Unpublish / delete | Notification removed; the bell never links to a hidden notice |
| Clear cookies / new browser | Everything shows as unread again (by design) |

Endpoints: `GET /api/notifications`, `POST /api/notifications/<id>/read`, `POST /api/notifications/read-all`. The bell shows the 10 most recent.
No real-time push: the count updates on the next page load.
