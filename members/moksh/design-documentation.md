# Design documentation and manual test cases (Moksh)

Figma wireframes are produced separately; add exported images to `evidence/`.

## Manual test cases
| # | Steps | Expected |
|---|---|---|
| 1 | Open `/` with an empty database | "No announcements yet" message |
| 2 | Publish three notices, reload `/` | Three cards, newest first |
| 3 | Click each category tab | Only that category; tab underlined |
| 4 | Search a word, then click a category | Search text stays in the box |
| 5 | Resize the browser to 375 px wide | One column, menu button, no sideways scrolling of the page |
| 6 | Tab through the page with the keyboard | Focus ring visible; skip link works |
| 7 | Open `/missing-page` | Friendly 404 page |
| 8 | Click a card title | Detail page opens |
