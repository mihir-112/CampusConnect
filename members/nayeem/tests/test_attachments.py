"""Nayeem: file validation, storage and the notice detail page."""
import io
import os

import pytest
from werkzeug.datastructures import FileStorage

from app.constants import PDF_MAX_BYTES, POSTER_MAX_BYTES
from app.errors import ValidationError
from app.extensions import db
from app.models import Attachment
from app.services import attachment_service as svc
from conftest import PDF_BYTES, PNG_BYTES


def upload(data, name):
    return FileStorage(stream=io.BytesIO(data), filename=name)


def stored_files(app):
    return os.listdir(app.config["UPLOAD_FOLDER"])


# ---- service level -------------------------------------------------------

def test_valid_poster_and_pdf_are_saved(app, make_announcement):
    a_id = make_announcement()
    with app.app_context():
        poster = svc.save_attachment(a_id, "poster", upload(PNG_BYTES, "My Poster.png"))
        pdf = svc.save_attachment(a_id, "pdf", upload(PDF_BYTES, "notice.pdf"))
        assert poster.mime_type == "image/png" and pdf.mime_type == "application/pdf"
        assert poster.stored_filename != "My Poster.png"  # random name on disk
        assert poster.original_filename == "My_Poster.png"
        assert svc.file_exists(poster) and svc.file_exists(pdf)
    assert len(stored_files(app)) == 2


@pytest.mark.parametrize(
    "kind,data,name",
    [
        ("poster", PNG_BYTES, "poster.exe"),
        ("poster", PNG_BYTES, "poster"),
        ("pdf", PDF_BYTES, "notice.png"),
        ("poster", b"this is plain text", "poster.png"),
        ("pdf", b"<html>not a pdf</html>", "notice.pdf"),
        ("poster", b"", "poster.png"),
        ("poster", PNG_BYTES + b"0" * POSTER_MAX_BYTES, "big.png"),
        ("pdf", PDF_BYTES + b"0" * PDF_MAX_BYTES, "big.pdf"),
    ],
)
def test_invalid_files_are_rejected(app, make_announcement, kind, data, name):
    a_id = make_announcement()
    with app.app_context():
        with pytest.raises(ValidationError) as excinfo:
            svc.save_attachment(a_id, kind, upload(data, name))
        assert kind in excinfo.value.errors
        assert Attachment.query.count() == 0
    assert stored_files(app) == []


def test_file_with_no_name_is_rejected(app):
    with app.app_context(), pytest.raises(ValidationError):
        svc.check_file("poster", upload(PNG_BYTES, ""))


def test_replacing_an_attachment_removes_the_old_file(app, make_announcement):
    a_id = make_announcement()
    with app.app_context():
        first = svc.save_attachment(a_id, "poster", upload(PNG_BYTES, "a.png")).stored_filename
        second = svc.save_attachment(a_id, "poster", upload(PNG_BYTES, "b.png")).stored_filename
        assert first != second and Attachment.query.count() == 1
    assert stored_files(app) == [second]


def test_delete_attachment_removes_row_and_file(app, make_announcement):
    a_id = make_announcement()
    with app.app_context():
        svc.save_attachment(a_id, "pdf", upload(PDF_BYTES, "a.pdf"))
        svc.delete_attachment(a_id, "pdf")
        assert svc.get_attachment(a_id, "pdf") is None
    assert stored_files(app) == []


# ---- detail page and downloads -------------------------------------------

def test_detail_page_shows_all_notice_information(client, make_announcement):
    a_id = make_announcement(
        "Tech Fest", category="Events", venue="Main Auditorium", event_date="2026-12-05",
        event_time="14:30", registration_link="https://example.com/register",
    )
    html = client.get(f"/notices/{a_id}").get_data(as_text=True)
    for expected in ("Tech Fest", "Full details about Tech Fest.", "Main Auditorium",
                     "05 Dec 2026", "2:30 PM", "https://example.com/register", "Published"):
        assert expected in html


def test_detail_page_without_optional_fields(client, make_announcement):
    html = client.get(f"/notices/{make_announcement('Plain notice')}").get_data(as_text=True)
    assert "Plain notice" in html and "Register for this event" not in html and "Venue" not in html


def test_unpublished_and_missing_notices_are_404(client, make_announcement):
    assert client.get(f"/notices/{make_announcement(published=False)}").status_code == 404
    assert client.get("/notices/9999").status_code == 404


def test_poster_is_previewed_and_pdf_can_be_viewed_or_downloaded(app, client, make_announcement):
    a_id = make_announcement()
    with app.app_context():
        svc.save_attachment(a_id, "poster", upload(PNG_BYTES, "p.png"))
        svc.save_attachment(a_id, "pdf", upload(PDF_BYTES, "Schedule.pdf"))
    html = client.get(f"/notices/{a_id}").get_data(as_text=True)
    assert f"/notices/{a_id}/poster" in html and "View PDF" in html and "Download PDF" in html

    poster = client.get(f"/notices/{a_id}/poster")
    assert poster.status_code == 200 and poster.mimetype == "image/png"
    assert poster.headers["X-Content-Type-Options"] == "nosniff"

    inline = client.get(f"/notices/{a_id}/pdf")
    assert inline.mimetype == "application/pdf" and "attachment" not in inline.headers.get("Content-Disposition", "")
    download = client.get(f"/notices/{a_id}/pdf?download=1")
    assert "attachment" in download.headers["Content-Disposition"] and "Schedule.pdf" in download.headers["Content-Disposition"]


def test_attachments_of_unpublished_notices_are_not_served(app, client, make_announcement):
    a_id = make_announcement(published=False)
    with app.app_context():
        svc.save_attachment(a_id, "pdf", upload(PDF_BYTES, "x.pdf"))
    assert client.get(f"/notices/{a_id}/pdf").status_code == 404


def test_missing_attachment_routes_return_404(client, make_announcement):
    a_id = make_announcement()
    assert client.get(f"/notices/{a_id}/poster").status_code == 404
    assert client.get(f"/notices/{a_id}/pdf").status_code == 404


def test_file_missing_from_disk_is_handled_gracefully(app, client, make_announcement):
    a_id = make_announcement()
    with app.app_context():
        att = svc.save_attachment(a_id, "poster", upload(PNG_BYTES, "p.png"))
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], att.stored_filename))
    page = client.get(f"/notices/{a_id}")
    assert page.status_code == 200 and b"currently unavailable" in page.data
    assert client.get(f"/notices/{a_id}/poster").status_code == 404


def test_deleting_an_announcement_deletes_its_files(app, make_announcement):
    from app.services import announcement_service

    a_id = make_announcement()
    with app.app_context():
        svc.save_attachment(a_id, "poster", upload(PNG_BYTES, "p.png"))
        svc.save_attachment(a_id, "pdf", upload(PDF_BYTES, "p.pdf"))
        announcement_service.delete_announcement(a_id)
        assert Attachment.query.count() == 0
    assert stored_files(app) == []
