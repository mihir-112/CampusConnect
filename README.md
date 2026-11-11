# CampusConnect: Your campus. One place.

CampusConnect is a college announcement portal built with Flask and SQLite. Students read announcements
without logging in; authorised publishers log in to create, edit, publish and delete them.
It is a five-member Collaborative Development and Deployment (CDD) project.

## Features

| Area | What it does | Owner |
|---|---|---|
| Core engine | App factory, Announcement model, CRUD, validation, JSON API | Mihir |
| Authentication | Publisher login/logout, hashed passwords, protected routes, CSRF | Aariz |
| Notice details | Detail page, poster upload/preview, PDF view/download, file checks | Nayeem |
| Student dashboard | Homepage, cards, category navigation, responsive layout, error pages | Moksh |
| Search and notifications | Keyword search, category filter, notification bell, mark as read | Mridul |

Categories are fixed: **Examinations, Events, Clubs, General**.

## Run it on Windows (PowerShell)

```powershell
git clone <your-repository-url> CampusConnect
cd CampusConnect
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Create the first publisher (you will be asked for a password of 8+ characters)
flask --app run create-publisher

python run.py
```

Open <http://127.0.0.1:5000>. Publisher login is at <http://127.0.0.1:5000/auth/login>.
On macOS or Linux, use `source venv/bin/activate` instead of `venv\Scripts\activate`.

## Run the tests

```powershell
python -m pytest
```

Tests use a temporary SQLite file and upload folder per test, so they never touch your real data.
Each member's tests are in `members/<name>/tests/`; cross-module tests are in `tests/`.

## Run with Docker

```powershell
docker compose up --build -d
docker compose exec web flask create-publisher
```

Open <http://localhost:5000>. Data survives restarts because `/app/instance` (database and uploads)
is a named volume. Set your own secret first: `$env:SECRET_KEY = "a-long-random-string"`.
Stop with `docker compose down` (add `-v` to also delete the data).

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | dev value | Signs sessions and CSRF tokens. Set your own. |
| `DATABASE_URL` | `instance/campusconnect.db` | SQLite location |
| `UPLOAD_FOLDER` | `instance/uploads` | Where posters and PDFs are stored |
| `PORT` / `HOST` | `5000` / `127.0.0.1` | Server address (Docker uses `0.0.0.0`) |

## Project layout

```text
app/            the one shared Flask application
  models/       announcement, publisher, attachment, notification
  services/     business logic (routes call services, services call models)
  routes/       blueprints: dashboard, notices, auth, admin + api, notifications
  forms/  templates/  static/
members/        per-member documentation, tests and evidence (no app copies)
tests/          integration tests          docs/   api, database, git, demo guides
.github/workflows/ci.yml                    Dockerfile, docker-compose.yml
```

Rules: dependencies point `routes -> services -> models`; modules import each other's services or models,
never routes; cross-module links use `url_for("blueprint.endpoint")`. Error pages share one template,
`templates/errors/error.html`.

## More documentation

- [API reference](docs/api.md) · [Database](docs/database.md)
- [Git workflow for all five members](docs/git-workflow.md)
- [Integration checklist and demo guide](docs/demo-guide.md)
- Member folders: [Mihir](members/mihir/README.md), [Aariz](members/aariz/README.md), [Nayeem](members/nayeem/README.md), [Moksh](members/moksh/README.md), [Mridul](members/mridul/README.md)

## Design decisions

- **Read state per browser:** there are no student accounts, so a shared `is_read` column would mark a
  notification read for everyone. Notifications are shared rows; read state lives in the browser session.
- **Private uploads:** files live in `instance/uploads/`, not `static/`, and are served only through
  `notices.poster` / `notices.pdf`, which return 404 for unpublished announcements.
- **`published_at`:** the date students see and the sort order use the publication date, not the draft's creation date.
- **Production note:** `python run.py` uses Flask's development server, which is fine for a college demo.
  For real deployment, set a strong `SECRET_KEY` and serve over HTTPS behind a production WSGI server.
