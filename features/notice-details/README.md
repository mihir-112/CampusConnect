# Notice Details: Announcement details and document management

**Branch:** `feature/notice-details`

## What I built
| Area | Files |
|---|---|
| Model | `features/notice-details/backend/models/attachment.py` |
| File rules and storage | `backend/services/attachment_service.py`: extension, size, file signature, random names, safe display names |
| Endpoints | `backend/routes/attachments.py`: upload, delete, view, download |
| Frontend | `features/notice-details/frontend/`: `AnnouncementDetailPage`, `AttachmentSection` (poster, PDF preview, view, download), `AttachmentUploader`, `fileRules.js`, `attachmentsApi.js` |
| Tests | `features/notice-details/tests/test_attachments.py`, `details.test.jsx` |

## Completed tasks
- [x] Upload endpoint for poster and PDF with owner-only access
- [x] Extension, size and real file-content validation
- [x] Files stored outside static folders under random names
- [x] View (inline) and download endpoints; drafts' files stay private
- [x] Detail page: date, time, venue, registration link, poster, PDF preview
- [x] Missing file on disk shows a clear message instead of a broken page
- [x] Old files removed when replaced, and when an announcement is deleted
- [x] Tests and documentation

## How it connects to the others
core-announcement-engine's form uses my `AttachmentUploader`. When core-announcement-engine deletes an announcement it emits an event and my handler deletes the files. My detail page reads core-announcement-engine's `GET /api/announcements/{id}`.

Documentation: [file-management.md](documentation/file-management.md).

## Git history and pull requests
Fill this in from your real GitHub history. Leave a row empty rather than invent one.

| Commit or PR | What it contains | Link |
|---|---|---|
| | | |
| | | |
