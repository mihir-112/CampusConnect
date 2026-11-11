# Implementation notes (Nayeem)

- **Detail page:** `notices.detail` loads a published announcement (404 otherwise) and shows title, category, publication date, optional event date/time, venue, a registration button when a link exists, the full description, the poster, and PDF buttons.
- **Attachment model:** at most one poster and one PDF per announcement (`UNIQUE(announcement_id, kind)`); no duplicate of the Announcement model.
- **Validation (`check_file`):** extension allow-list, size limit (poster 3 MB, PDF 5 MB), non-empty, and the first bytes must match the type (PNG, JPEG, WEBP, PDF). A text file renamed `.png` is rejected.
- **Safe storage:** files are saved as `<random uuid>.<ext>` in `UPLOAD_FOLDER`, outside `static/`. The original name is kept only for display and download, passed through `secure_filename`.
- **Replacing and deleting:** uploading again replaces the row and removes the old file; `delete_attachment` and `delete_all_for` remove rows and files.
- **Serving:** `notices.poster` and `notices.pdf` check that the announcement is published, then use `send_from_directory` with the stored MIME type and `X-Content-Type-Options: nosniff`. `?download=1` forces a download.
- **Missing files:** if the database row exists but the file is gone, the detail page says the attachment is unavailable and the download route returns 404.
- **Docker:** see the main README. I have not built the image in my environment, so run `docker compose up --build` once before the demo.
