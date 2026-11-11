# Aariz: Publisher Authentication and Security

**Branch:** `feature/publisher-auth`

## What I own
| File | Purpose |
|---|---|
| `app/models/publisher.py` | Publisher model with password hashing |
| `app/routes/auth.py`, `app/forms/auth_forms.py` | Login, logout, safe redirects |
| `app/templates/login.html`, `app/static/css/auth.css` | Login screen |
| `app/cli.py` | `flask --app run create-publisher` |
| `app/extensions.py` (login manager and CSRF settings), `config.py` (session settings) | Session security |
| `.github/workflows/ci.yml` | GitHub Actions: install, run pytest on pushes and pull requests to `main` |

## Tests
`members/aariz/tests/test_auth.py`. Run: `python -m pytest members/aariz`.

## How it connects to the others
Mihir's admin routes use `@login_required` and `current_user.id` for ownership. The navbar in Moksh's `base.html` switches between "Publisher login" and "Manage / Log out".
See [implementation.md](implementation.md) and [security-documentation.md](security-documentation.md).
