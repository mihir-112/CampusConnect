# File management (Nayeem)

| Item | Rule |
|---|---|
| Poster types | `png`, `jpg`, `jpeg`, `webp`, up to 3 MB |
| PDF | `pdf`, up to 5 MB |
| Whole request | Capped at 6 MB (HTTP 413 page) |
| Location | `UPLOAD_FOLDER` (default `instance/uploads/`, Docker: volume `campusconnect_data`) |
| Disk name | Random UUID plus extension |
| Access | Only through `/notices/<id>/poster` and `/notices/<id>/pdf`, only when published |

Docker persistence: `docker-compose.yml` mounts the named volume at `/app/instance`, which holds both the database and uploads.
