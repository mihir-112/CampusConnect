"""Poster and PDF upload, storage, preview and download. Owner: notice-details."""
import io
import os

import pytest

from backend.core.constants import PDF_MAX_BYTES, POSTER_MAX_BYTES
from conftest import PDF_BYTES, PNG_BYTES


def stored_files(settings):
    return sorted(os.listdir(settings.upload_dir)) if os.path.isdir(settings.upload_dir) else []


def test_upload_poster_and_pdf(client, make_announcement, upload, png_file, pdf_file):
    a = make_announcement()
    first = upload(a["id"], "poster", png_file())
    assert first.status_code == 201
    second = upload(a["id"], "pdf", pdf_file("Exam Rules.pdf"))
    attachments = {x["kind"]: x for x in second.json()["attachments"]}
    assert set(attachments) == {"poster", "pdf"}
    assert attachments["pdf"]["original_filename"] == "Exam Rules.pdf"
    assert attachments["pdf"]["mime_type"] == "application/pdf"
    assert attachments["pdf"]["available"] is True
    assert attachments["pdf"]["download_url"].endswith("/download")


def test_files_are_stored_under_random_names_outside_static(settings, make_announcement, upload, png_file):
    a = make_announcement()
    upload(a["id"], "poster", png_file("my poster.png"))
    (name,) = stored_files(settings)
    assert name.endswith(".png") and "poster" not in name
    assert "static" not in settings.upload_dir


def test_view_serves_the_file_inline(client, make_announcement, upload, pdf_file):
    a = make_announcement()
    att = upload(a["id"], "pdf", pdf_file()).json()["attachments"][0]
    response = client.get(att["url"])
    assert response.status_code == 200
    assert response.content == PDF_BYTES
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"].startswith("inline")
    assert response.headers["x-content-type-options"] == "nosniff"


def test_download_forces_attachment_with_original_name(client, make_announcement, upload, pdf_file):
    a = make_announcement()
    att = upload(a["id"], "pdf", pdf_file("Timetable.pdf")).json()["attachments"][0]
    header = client.get(att["download_url"]).headers["content-disposition"]
    assert header.startswith("attachment") and "Timetable.pdf" in header


def test_poster_is_served_as_an_image(client, make_announcement, upload, png_file):
    a = make_announcement()
    att = upload(a["id"], "poster", png_file()).json()["attachments"][0]
    assert client.get(att["url"]).headers["content-type"] == "image/png"


def test_replacing_a_file_removes_the_old_one(settings, make_announcement, upload, png_file):
    a = make_announcement()
    upload(a["id"], "poster", png_file("one.png"))
    (old,) = stored_files(settings)
    upload(a["id"], "poster", png_file("two.png"))
    (new,) = stored_files(settings)
    assert new != old


def test_only_one_attachment_per_kind(client, make_announcement, upload, png_file):
    a = make_announcement()
    upload(a["id"], "poster", png_file())
    body = upload(a["id"], "poster", png_file()).json()
    assert len(body["attachments"]) == 1


@pytest.mark.parametrize("kind, name", [("poster", "evil.exe"), ("poster", "doc.pdf"), ("pdf", "pic.png"), ("pdf", "noextension"), ("poster", "x.svg")])
def test_wrong_extension_is_rejected(make_announcement, upload, kind, name):
    a = make_announcement()
    response = upload(a["id"], kind, (name, io.BytesIO(PNG_BYTES), "application/octet-stream"))
    assert response.status_code == 422
    assert "file" in response.json()["error"]["fields"]


def test_file_contents_must_match_the_extension(settings, make_announcement, upload):
    a = make_announcement()
    response = upload(a["id"], "poster", ("fake.png", io.BytesIO(b"MZ\x90\x00 this is an executable"), "image/png"))
    assert response.status_code == 422
    assert "not a valid PNG" in response.json()["error"]["fields"]["file"]
    assert stored_files(settings) == []


def test_empty_file_is_rejected(make_announcement, upload):
    a = make_announcement()
    assert upload(a["id"], "pdf", ("empty.pdf", io.BytesIO(b""), "application/pdf")).status_code == 422


def test_poster_over_the_limit_is_rejected(settings, make_announcement, upload):
    a = make_announcement()
    big = PNG_BYTES + b"0" * POSTER_MAX_BYTES
    response = upload(a["id"], "poster", ("big.png", io.BytesIO(big), "image/png"))
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "file_too_large"
    assert stored_files(settings) == []


def test_pdf_just_under_the_limit_is_accepted(make_announcement, upload):
    a = make_announcement()
    data = b"%PDF-1.4\n" + b"0" * (PDF_MAX_BYTES - 20)
    assert upload(a["id"], "pdf", ("ok.pdf", io.BytesIO(data), "application/pdf")).status_code == 201


def test_unknown_kind_is_rejected(make_announcement, upload, png_file):
    a = make_announcement()
    assert upload(a["id"], "video", png_file()).status_code == 422


def test_dangerous_file_names_are_cleaned(make_announcement, upload):
    a = make_announcement()
    att = upload(a["id"], "poster", ("../../etc/<script>.png", io.BytesIO(PNG_BYTES), "image/png")).json()["attachments"][0]
    assert "/" not in att["original_filename"] and "<" not in att["original_filename"]


def test_upload_needs_login_and_ownership(client, make_announcement, upload, png_file, other_auth):
    a = make_announcement()
    assert client.post(f"/api/announcements/{a['id']}/attachments", data={"kind": "poster"}, files={"file": png_file()}).status_code == 401
    assert upload(a["id"], "poster", png_file(), headers=other_auth).status_code == 403
    assert upload(9999, "poster", png_file()).status_code == 404


def test_missing_file_field_is_a_validation_error(client, auth, make_announcement):
    a = make_announcement()
    response = client.post(f"/api/announcements/{a['id']}/attachments", data={"kind": "poster"}, headers=auth)
    assert response.status_code == 422
    assert response.json()["error"]["fields"]["file"] == "File is required."


def test_drafts_files_are_private(client, auth, make_announcement, upload, png_file, other_auth):
    a = make_announcement(published=False)
    att = upload(a["id"], "poster", png_file()).json()["attachments"][0]
    assert client.get(att["url"]).status_code == 404
    assert client.get(att["url"], headers=other_auth).status_code == 404
    assert client.get(att["url"], headers=auth).status_code == 200
    client.patch(f"/api/announcements/{a['id']}/publish", headers=auth)
    assert client.get(att["url"]).status_code == 200
    client.patch(f"/api/announcements/{a['id']}/unpublish", headers=auth)
    assert client.get(att["url"]).status_code == 404


def test_missing_file_on_disk_is_handled_gracefully(client, settings, make_announcement, upload, pdf_file):
    a = make_announcement()
    att = upload(a["id"], "pdf", pdf_file()).json()["attachments"][0]
    os.remove(os.path.join(settings.upload_dir, stored_files(settings)[0]))
    detail = client.get(f"/api/announcements/{a['id']}").json()
    assert detail["attachments"][0]["available"] is False
    response = client.get(att["url"])
    assert response.status_code == 404
    assert "unavailable" in response.json()["error"]["message"]


def test_unknown_attachment_is_404(client):
    assert client.get("/api/attachments/12345").status_code == 404
    assert client.get("/api/attachments/12345/download").status_code == 404


def test_delete_attachment_removes_record_and_file(client, auth, settings, make_announcement, upload, png_file, other_auth):
    a = make_announcement()
    att = upload(a["id"], "poster", png_file()).json()["attachments"][0]
    assert client.delete(f"/api/attachments/{att['id']}", headers=other_auth).status_code == 403
    assert client.delete(f"/api/attachments/{att['id']}").status_code == 401
    assert client.delete(f"/api/attachments/{att['id']}", headers=auth).status_code == 204
    assert stored_files(settings) == []
    assert client.get(f"/api/announcements/{a['id']}").json()["attachments"] == []


def test_deleting_an_announcement_deletes_its_files(client, auth, settings, make_announcement, upload, png_file, pdf_file):
    a = make_announcement()
    upload(a["id"], "poster", png_file())
    upload(a["id"], "pdf", pdf_file())
    assert len(stored_files(settings)) == 2
    client.delete(f"/api/announcements/{a['id']}", headers=auth)
    assert stored_files(settings) == []


def test_event_details_come_with_the_announcement(client, make_announcement):
    a = make_announcement(category="Events", venue="Seminar Hall", event_date="2026-11-20", event_time="10:00", registration_link="https://example.com/join")
    body = client.get(f"/api/announcements/{a['id']}").json()
    assert (body["venue"], body["event_date"], body["registration_link"]) == ("Seminar Hall", "2026-11-20", "https://example.com/join")
