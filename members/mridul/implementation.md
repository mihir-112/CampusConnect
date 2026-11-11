# Implementation notes (Mridul)

- **Search:** case-insensitive match on title, description and venue. `%`, `_` and `\` typed by the user are escaped so they match literally.
- **Filtering:** `category` must be one of the four; an unknown value is ignored on the dashboard (the JSON API returns 400). Search and category combine.
- **Order and paging:** published announcements only, newest `published_at` first (ties broken by id), 9 per page.
- **Empty results:** the dashboard shows "No announcements found" with a Clear filters button.
- **Notifications:** publishing inserts one row (`message` like "New in Events: Tech Fest"); repeated calls do nothing; unpublishing or deleting removes it.
- **Bell:** a context processor gives every page the 10 latest notifications and the unread count. The bell shows a count badge, a list that links to each notice, and "Mark all as read".
- **Mark as read:** clicking a notification sends a POST (with the CSRF header) before the browser follows the link; the state is stored in `session["read_notification_ids"]`.
- **Why the session:** there are no student accounts, so a shared `is_read` column would mark notices read for everyone. Notifications are stored in the database; read state is per browser.
