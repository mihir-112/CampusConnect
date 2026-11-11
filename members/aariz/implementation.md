# Implementation notes (Aariz)

- **Publisher model:** `set_password` stores a Werkzeug hash; `check_password` verifies it. Plain passwords are never stored.
- **Login:** `LoginForm` (username, password, CSRF). The route looks up the publisher, calls `login_user`, clears the old session first, and marks the session permanent (2 hours).
- **Invalid credentials:** one message, "Invalid username or password.", for both wrong password and unknown user.
- **Logout:** POST only, CSRF-protected, clears the session.
- **Protected routes:** `@login_required` on every admin route; anonymous users go to `/auth/login?next=...`. `_safe_next` only follows paths on this site.
- **Authorisation:** the admin routes return 403 when a publisher touches another publisher's announcement.
- **CSRF:** `CSRFProtect` is on for the whole app. Forms include `csrf_token`; the notification JavaScript sends `X-CSRFToken`.
- **Creating accounts:** there is no public registration. `flask --app run create-publisher` asks for username, email and a password (8+ characters, typed twice).
- **CI:** `.github/workflows/ci.yml` checks out the code, sets up Python 3.12, installs `requirements.txt`, runs `python -m pytest -v`. I have not seen it run on GitHub yet; check the Actions tab after the first push.
