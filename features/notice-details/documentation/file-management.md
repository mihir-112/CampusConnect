# File management

## Rules
| Type | Extensions | Max size | Checked content |
|---|---|---|---|
| Poster | png, jpg, jpeg, webp | 3 MB | PNG / JPEG / WebP signature bytes |
| PDF | pdf | 5 MB | starts with `%PDF-` |

An announcement has at most one poster and one PDF. Uploading again replaces the old file.

## Why these checks
- **Extension** blocks obvious wrong files.
- **File signature** catches an `.exe` renamed to `.png`. The server reads the first bytes; the browser's claimed type is ignored.
- **Size** is read with a limit (`limit + 1` bytes) so a huge upload cannot fill memory.
- **Random stored name** (`uuid4`) means a visitor cannot guess a file path and a name can never contain `../`.
- **Display name** is cleaned (folders and odd characters removed) before it is shown or used in a download header.
- **Outside static folders:** files sit in `UPLOAD_DIR` (`instance/uploads`, or `/data/uploads` in Docker). They are only served by `/api/attachments/{id}`, which first checks that the announcement is published.
- `X-Content-Type-Options: nosniff` stops browsers from guessing a different type.

## Error handling
| Situation | Result |
|---|---|
| Wrong type or content | 422 with a message on `file` |
| Too big | 413 `file_too_large` |
| File missing on disk | announcement shows `available: false`; page says the file is unavailable; endpoint returns 404 |
| Draft or unpublished | 404 for everyone except its owner |
| Save to database fails after file write | the new file is removed again |

## Preview and download
The detail page shows the poster with `<img>`, and offers a PDF **Preview** (a frame), **View** (new tab) and **Download** (`Content-Disposition: attachment` with the original name). Phones that cannot show a PDF inside a frame can still use View and Download.
