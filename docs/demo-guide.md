# Integration checklist and demonstration guide

## Integration checklist (run after every merge)
- [ ] `git pull origin main`, then `python -m pytest` passes with no failures.
- [ ] `python run.py` starts; `/` loads without a login.
- [ ] Publisher can log in; `/admin/` redirects to login when logged out.
- [ ] Creating an announcement with a poster and PDF works; invalid files are rejected with a clear message.
- [ ] A published announcement appears on `/`, in search, in its category, and in the bell.
- [ ] A draft does not appear anywhere public (home, search, API, detail URL, files).
- [ ] Unpublish and delete remove it from public pages, the bell and the uploads folder.
- [ ] Layout works at phone width (~375 px) and desktop.
- [ ] `docker compose up --build` starts; data survives `docker compose down` then `up`.
- [ ] GitHub Actions run on `main` is green.

## Suggested 8-minute demo (all five members)
1. **Mihir** (1 min): architecture slide, show `app/` structure; create an announcement in `/admin/` and explain validation by submitting an empty title.
2. **Aariz** (1.5 min): open `/admin/` logged out (redirect), log in with a wrong then right password, show the hashed value in the database, log out.
3. **Nayeem** (1.5 min): attach a poster and a PDF; open the notice detail; try uploading a `.exe` renamed to `.png` and show the rejection; show the Docker volume.
4. **Moksh** (1.5 min): student view without login, cards, category tabs, resize to mobile width, show an empty state.
5. **Mridul** (1.5 min): search plus category filter, empty results, publish a new notice and show the bell count rising, open it, count drops.
6. **Everyone** (1 min): show the merged pull requests, a green CI run, and `docker compose up`.

## Before the demo
Create a publisher, then publish 5 to 6 real sample announcements across the four categories so the dashboard looks lived-in.
Capture screenshots yourself into `members/<name>/evidence/`; only genuine screenshots belong there.
