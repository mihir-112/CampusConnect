# Nayeem: Notice Details and Document Management

**Branch:** `feature/notice-details`

## What I own
| File | Purpose |
|---|---|
| `app/models/attachment.py` | Attachment table (poster and PDF) |
| `app/services/attachment_service.py` | Validation, storage, replacement, deletion |
| `app/routes/notices.py` | Detail page, poster and PDF serving |
| `app/templates/notice_detail.html`, `app/static/css/notice.css` | Detail screen |
| `Dockerfile`, `docker-compose.yml`, `.dockerignore` | Docker setup |

## Tests
`members/nayeem/tests/test_attachments.py`. Run: `python -m pytest members/nayeem`.

## How it connects to the others
Mihir's admin form calls `check_file` then `save_attachment`; Mihir's delete calls `delete_all_for`. Moksh's cards and Mridul's bell link to `notices.detail`.
See [implementation.md](implementation.md) and [file-management.md](file-management.md).
