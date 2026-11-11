# Implementation notes (Moksh)

- **Homepage:** `dashboard.index` reads `q`, `category` and `page`, asks `search_service` for published announcements, and renders cards. Nothing is hardcoded; with an empty database the page shows an empty state.
- **Cards:** category chip, publication date, title, 150-character summary, tags for event date / poster / PDF, and a "Read notice" link.
- **Category navigation:** All plus the four categories; the active one is highlighted with `aria-current`, and the search text is kept when switching.
- **States:** empty ("No announcements yet"), no results ("No announcements found" with Clear filters), load error (database failure shows an error card with a 500 status), and error pages for 403/404/413/500. While a search loads, the button shows "Searching...".
- **Responsive:** three columns, two at 900 px, one at 640 px. Below 640 px the navbar collapses into a menu button, the category tabs scroll sideways, and the admin table becomes stacked rows.
- **Design:** colours from the brief as CSS variables in `style.css` (navy `#14233F`, green `#16845B`, soft blue `#E8EEF8`). Georgia headings, system sans-serif body, visible keyboard focus, reduced-motion support, skip link.
- **Safety:** all text is HTML-escaped by Jinja; one test checks a `<script>` title.
