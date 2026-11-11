# Docker guide

Two images and one volume:

| Service | Image | What it does |
|---|---|---|
| `backend` | `Dockerfile` | FastAPI on port 8000, runs as a non-root user |
| `frontend` | `frontend/Dockerfile` | Builds the React app, then serves it with nginx and forwards `/api` to `backend` |
| volume `campusconnect_data` | | `/data/campusconnect.db` and `/data/uploads` survive restarts |

## Start (PowerShell, Docker Desktop running)
```powershell
Copy-Item .env.example .env
py -c "import secrets; print(secrets.token_urlsafe(48))"
```
Paste the printed text after `SECRET_KEY=` in `.env`, then:
```powershell
docker compose up --build
```
Open the app at <http://localhost:8080> and the API documentation at <http://localhost:8000/docs>.

## Create the first publisher
In a second window:
```powershell
docker compose exec backend python -m backend.cli create-publisher
```
Then log in at <http://localhost:8080/publisher/login>.

## Everyday commands
```powershell
docker compose up -d        # run in the background
docker compose logs -f backend
docker compose down         # stop, keep data
docker compose down -v      # stop and DELETE the database and uploads
```

## Notes
- `SECRET_KEY` is required; compose stops with a clear message if it is missing. Never commit `.env`.
- Uploads are limited to 6 MB at nginx and 3 MB (poster) or 5 MB (PDF) in the API.
- For a real deployment put HTTPS in front (for example a college reverse proxy).
