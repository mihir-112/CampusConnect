# Walkthrough guide (for the expo and evaluation)

## Before you present
1. Start the backend and frontend (see [setup-guide.md](setup-guide.md)) or run `docker compose up --build`.
2. Create a publisher: `py -m backend.cli create-publisher`.
3. Log in and publish 5 or 6 **real** announcements across the four categories, with at least one poster and one PDF. Use real college notices so the home page looks lived-in; the application ships with no pre-filled content.
4. Open the student site in a private window to show the student view.
5. Take your own screenshots into `features/<feature>/evidence/`.

## Integration checklist (run after every merge)
- [ ] `git pull origin main`, then `py -m pytest` and `cd frontend; npm test` pass
- [ ] `/` loads without a login; `/publisher` sends you to login when logged out
- [ ] Publisher can log in; logging out ends the session
- [ ] Creating an announcement with a poster and a PDF works; bad files give a clear message
- [ ] A published announcement appears on the home page, in search, in its category and in the bell
- [ ] A draft appears nowhere public (list, search, detail address, files)
- [ ] Unpublish and delete remove it everywhere, and the files from the upload folder
- [ ] Layout works at phone width (about 375 px) and desktop
- [ ] `docker compose up --build` starts; data survives `docker compose down` then `up`
- [ ] The latest GitHub Actions run on `main` is green

## Suggested 8-minute run-through
1. **Mihir (1.5 min):** the architecture picture; create an announcement; submit an empty title to show validation; show `/docs`.
2. **Aariz (1.5 min):** open `/publisher` logged out (redirect); wrong password, then the right one; mention hashing and expiry; log out.
3. **Nayeem (1.5 min):** attach a poster and PDF; open the notice; preview the PDF; try a renamed `.exe` and show the rejection.
4. **Moksh (1.5 min):** student view, cards, category tabs, phone width, an empty state.
5. **Mridul (1.5 min):** search plus category; publish a new notice and watch the bell count rise; open it and watch it drop; explain per-browser read state.
6. **Everyone (1 min):** merged pull requests, a green CI run, `docker compose up`.

## Questions you may be asked
| Question | Short answer |
|---|---|
| Why FastAPI and React instead of Flask templates? | The API can serve any client; React gives faster, app-like pages; both are common in industry |
| Why JWT? | The React app and API are separate programs, so a signed token in a header is simple and avoids cookie/CSRF issues |
| How do you stop students seeing drafts? | Every public query filters `is_published`; the detail and file endpoints return 404 for drafts |
| Why can't read state sync between devices? | Students have no accounts; we say so openly and store it per browser |
| What if the database is deleted? | Tables are recreated on start; uploads folder is separate |
| How is each member's work separate yet integrated? | Own folder, documented contracts, events and shared components |
