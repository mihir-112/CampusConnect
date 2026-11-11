"""Integration: all five modules working together through real HTTP requests."""
import os

from app.extensions import db
from app.models import Announcement, Attachment, Notification
from conftest import csrf_token_from, create_publisher, main_content


def form(**over):
    data = {"title": "Tech Fest 2026", "description": "Two days of talks and demos.", "category": "Events",
            "event_date": "2026-12-05", "event_time": "10:30", "venue": "Main Auditorium",
            "registration_link": "https://example.com/register", "is_published": "y"}
    data.update(over)
    return data


def test_publisher_to_student_journey(app, client, publisher, login, png_file, pdf_file):
    # Aariz: publisher logs in. Mihir: creates a published announcement. Nayeem: attaches files.
    login()
    response = client.post("/admin/announcements/new", data=form(poster=png_file(), pdf=pdf_file()),
                           content_type="multipart/form-data")
    assert response.status_code == 302
    client.post("/auth/logout")

    # Moksh: a student (fresh browser, no login) sees it on the dashboard.
    student = app.test_client()
    home = student.get("/").get_data(as_text=True)
    assert "Tech Fest 2026" in home and "Poster" in home and "PDF" in home

    # Mridul: bell shows one unread notification pointing at the notice; search and filter find it.
    assert student.get("/api/notifications").get_json()["unread"] == 1
    assert "Tech Fest" in student.get("/?q=talks&category=Events").get_data(as_text=True)
    assert "Tech Fest" not in main_content(student.get("/?category=Clubs").get_data(as_text=True))

    # Nayeem: detail page, poster and PDF.
    with app.app_context():
        a_id = Announcement.query.one().id
    detail = student.get(f"/notices/{a_id}").get_data(as_text=True)
    assert "Main Auditorium" in detail and "Register for this event" in detail
    assert student.get(f"/notices/{a_id}/poster").status_code == 200
    assert student.get(f"/notices/{a_id}/pdf?download=1").status_code == 200

    # Opening the notification marks it read.
    nid = student.get("/api/notifications").get_json()["notifications"][0]["id"]
    assert student.post(f"/api/notifications/{nid}/read").get_json()["unread"] == 0


def test_draft_edit_publish_unpublish_delete_lifecycle(app, client, publisher, login, png_file):
    login()
    client.post("/admin/announcements/new", data=form(is_published="", poster=png_file()),
                content_type="multipart/form-data")
    with app.app_context():
        a_id = Announcement.query.one().id
        assert Notification.query.count() == 0
    assert client.get(f"/notices/{a_id}").status_code == 404  # draft is hidden

    client.post(f"/admin/announcements/{a_id}/publish")
    assert client.get(f"/notices/{a_id}").status_code == 200
    with app.app_context():
        assert Notification.query.count() == 1

    edit = client.post(f"/admin/announcements/{a_id}/edit", data=form(title="Renamed Fest", remove_poster="y"))
    assert edit.status_code == 302
    with app.app_context():
        assert db.session.get(Announcement, a_id).title == "Renamed Fest"
        assert Attachment.query.count() == 0
    assert os.listdir(app.config["UPLOAD_FOLDER"]) == []

    client.post(f"/admin/announcements/{a_id}/publish")  # unpublish
    assert client.get(f"/notices/{a_id}").status_code == 404
    client.post(f"/admin/announcements/{a_id}/delete")
    with app.app_context():
        assert Announcement.query.count() == 0


def test_invalid_form_shows_errors_and_saves_nothing(app, logged_in):
    response = logged_in.post("/admin/announcements/new", data=form(title="", category="Sports"))
    assert response.status_code == 400
    with app.app_context():
        assert Announcement.query.count() == 0


def test_bad_attachment_blocks_the_whole_save(app, logged_in):
    import io

    response = logged_in.post(
        "/admin/announcements/new",
        data=form(poster=(io.BytesIO(b"not an image"), "poster.png")),
        content_type="multipart/form-data",
    )
    assert response.status_code == 400 and b"not a valid PNG" in response.data
    with app.app_context():
        assert Announcement.query.count() == 0


def test_oversized_upload_is_refused(app, logged_in):
    import io

    big = (io.BytesIO(b"0" * (7 * 1024 * 1024)), "huge.pdf")
    response = logged_in.post("/admin/announcements/new", data=form(pdf=big), content_type="multipart/form-data")
    assert response.status_code == 413


def test_admin_dashboard_lists_only_own_announcements(app, client, publisher, other_publisher, make_announcement, login):
    make_announcement("My notice")
    make_announcement("Not mine", author_id=other_publisher)
    login()
    html = main_content(client.get("/admin/").get_data(as_text=True))
    assert "My notice" in html and "Not mine" not in html


def test_full_flow_with_csrf_enabled(csrf_app):
    create_publisher(csrf_app)
    c = csrf_app.test_client()
    token = csrf_token_from(c.get("/auth/login").get_data(as_text=True))
    c.post("/auth/login", data={"username": "editor", "password": "password123", "csrf_token": token})

    page = c.get("/admin/announcements/new").get_data(as_text=True)
    bad = c.post("/admin/announcements/new", data=form())
    assert bad.status_code == 400  # missing CSRF token
    ok = c.post("/admin/announcements/new", data=form(csrf_token=csrf_token_from(page)))
    assert ok.status_code == 302

    meta = c.get("/").get_data(as_text=True)
    header_token = meta.split('name="csrf-token" content="')[1].split('"')[0]
    nid = c.get("/api/notifications").get_json()["notifications"][0]["id"]
    assert c.post(f"/api/notifications/{nid}/read").status_code == 400
    assert c.post(f"/api/notifications/{nid}/read", headers={"X-CSRFToken": header_token}).status_code == 200
