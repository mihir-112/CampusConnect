# UI design documentation

## Identity
| Token | Value | Use |
|---|---|---|
| Navy | `#14233F` | header, headings, links |
| White | `#FFFFFF` | page background, cards |
| Soft blue | `#E8EEF8` | hero band, tables headers, information boxes |
| Green | `#16845B` | primary buttons, active tab, unread marker |
Headings use Georgia, body text uses the system font (Segoe UI on Windows). Cards have a 6 px radius and a hairline border; no gradients and almost no animation (only the loading spinner, switched off when the visitor prefers reduced motion).

## Wireframes
**Student home (desktop)**
```text
+--------------------------------------------------------------+
| CampusConnect  Your campus. One place.   Announcements  Login  🔔 |
+--------------------------------------------------------------+
| [ Campus announcements                                        ]|
| [ Exams, events, clubs and general notices...                 ]|
| [ Search by title, details or venue            ] [Search]     ]|
|                                                                |
| All 7 | Examinations 3 | Events 2 | Clubs 1 | General 1        |
| 7 announcements                                                |
| +-----------+ +-----------+ +-----------+                      |
| | chip date | | chip date | | chip date |                      |
| | Title     | | Title     | | Title     |                      |
| | summary   | | summary   | | summary   |                      |
| | tags  Read| | tags  Read| | tags  Read|                      |
| +-----------+ +-----------+ +-----------+                      |
|                  Newer   Page 1 of 3   Older                   |
+--------------------------------------------------------------+
```
**Phone:** header collapses behind a menu button; one card per row; category tabs scroll sideways.
**Notice page:** back link, category chip and date, title, facts box (date, time, venue), description, Register button, poster, PDF actions with preview.
**Publisher dashboard:** title and New button, three statistic boxes (Total, Published, Drafts), category counts, table (Title, Category, Status, Updated, Actions); on phones each row becomes a stacked block.
**Form:** one column, labels above fields, attachments fieldset, "Publish now" checkbox, Save and Cancel.

## States designed for every screen
Loading (spinner and text), empty (what is missing and what to do), error (what failed and a Try again button), not found.

## Accessibility checklist
- [x] Every input has a visible label
- [x] Skip-to-content link
- [x] Focus outline on all controls (3 px green)
- [x] Active tab and current page marked with `aria-current`
- [x] Errors announced with `role="alert"`, loading with `role="status"`
- [x] Category chip colours pass 4.5:1 contrast
- [x] Works with keyboard only (bell closes with Escape)

## Figma
Create the Figma file from these wireframes and add the link here once it exists: _(link)_.
