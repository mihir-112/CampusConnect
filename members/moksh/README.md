# Moksh: Student Dashboard and Frontend Interface

**Branch:** `feature/student-dashboard`

## What I own
| File | Purpose |
|---|---|
| `app/routes/dashboard.py`, `app/templates/dashboard.html` | Homepage |
| `app/templates/base.html`, `partials/_announcement_card.html`, `partials/_search_bar.html` | Layout, navbar, cards |
| `app/templates/errors/error.html`, `app/templating.py` | Error pages and date/time filters |
| `app/static/css/style.css`, `app/static/js/app.js` | Design tokens, responsive CSS, mobile menu |

## Tests
`members/moksh/tests/test_dashboard.py` and the manual checklist in [design-documentation.md](design-documentation.md). Run: `python -m pytest members/moksh`.

## How it connects to the others
The dashboard gets its data from Mridul's `search_announcements` (which reads Mihir's Announcement table). Cards link to Nayeem's `notices.detail`. `base.html` includes Mridul's bell and Aariz's login/logout links.
See [implementation.md](implementation.md).
