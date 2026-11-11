# Security documentation (Aariz)

| Risk | Protection |
|---|---|
| Stolen password database | Passwords hashed with Werkzeug `generate_password_hash` |
| Guessing usernames | Same error message for unknown user and wrong password |
| Cross-site request forgery | Flask-WTF `CSRFProtect` on every POST, including logout and delete |
| Open redirect after login | `next` accepted only if it is a local path |
| Session fixation | Session cleared at login and logout; `strong` session protection |
| Cookie theft by scripts | `HttpOnly` and `SameSite=Lax` cookies, 2 hour lifetime |
| Editing someone else's notices | Author check returns 403 |
| Draft leaks | Public routes and files return 404 for unpublished announcements |

Not covered (out of scope): login rate limiting, two-factor login, password reset. When deployed, serve over HTTPS and set a strong `SECRET_KEY`.
