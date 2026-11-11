"""Whole-journey tests across every member's module. They call the API exactly as the React app does."""
import os

from conftest import CLIENT_A, PASSWORD


def test_publisher_to_student_journey(client, make_publisher, settings, png_file, pdf_file):
    make_publisher("editor")
    token = client.post("/api/auth/login", json={"username": "editor", "password": PASSWORD}).json()["access_token"]
    auth = {"Authorization": f"Bearer {token}"}

    # Publisher saves a draft with files: students cannot see it anywhere.
    draft = client.post(
        "/api/announcements",
        json={"title": "Tech Fest 2026", "description": "Three days of talks.", "category": "Events", "venue": "Main Hall", "event_date": "2026-12-05", "event_time": "10:00", "registration_link": "https://example.com/fest"},
        headers=auth,
    ).json()
    poster = client.post(f"/api/announcements/{draft['id']}/attachments", data={"kind": "poster"}, files={"file": png_file()}, headers=auth).json()
    attachment = poster["attachments"][0]
    assert client.get("/api/search?q=tech").json()["total"] == 0
    assert client.get(f"/api/announcements/{draft['id']}").status_code == 404
    assert client.get(attachment["url"]).status_code == 404
    assert client.get("/api/notifications").json()["items"] == []

    # Publishing makes it visible everywhere, and notifies.
    client.patch(f"/api/announcements/{draft['id']}/publish", headers=auth)
    assert client.get("/api/search?q=tech&category=Events").json()["total"] == 1
    assert client.get("/api/dashboard").json()["total"] == 1
    detail = client.get(f"/api/announcements/{draft['id']}").json()
    assert detail["venue"] == "Main Hall" and detail["attachments"][0]["available"] is True
    assert client.get(attachment["url"]).status_code == 200
    notifications = client.get("/api/notifications", headers={"X-Client-Id": CLIENT_A}).json()
    assert notifications["unread"] == 1

    # A student opens the notification: unread drops to zero for that browser only.
    client.patch(f"/api/notifications/{notifications['items'][0]['id']}/read", headers={"X-Client-Id": CLIENT_A})
    assert client.get("/api/notifications", headers={"X-Client-Id": CLIENT_A}).json()["unread"] == 0

    # Unpublish hides it again; delete removes the files.
    client.patch(f"/api/announcements/{draft['id']}/unpublish", headers=auth)
    assert client.get("/api/search?q=tech").json()["total"] == 0
    client.delete(f"/api/announcements/{draft['id']}", headers=auth)
    assert os.listdir(settings.upload_dir) == []

    # Logging out ends the session.
    client.post("/api/auth/logout", headers=auth)
    assert client.get("/api/publisher/announcements", headers=auth).status_code == 401


def test_two_publishers_cannot_touch_each_others_work(client, make_publisher, make_announcement, upload, png_file):
    auth_one = make_publisher("one")
    auth_two = make_publisher("two")
    a = make_announcement("Owned by one", headers=auth_one)
    attachment = upload(a["id"], "poster", png_file(), headers=auth_one).json()["attachments"][0]
    assert client.put(f"/api/announcements/{a['id']}", json={"title": "x", "description": "x", "category": "General"}, headers=auth_two).status_code == 403
    assert client.delete(f"/api/attachments/{attachment['id']}", headers=auth_two).status_code == 403
    assert upload(a["id"], "pdf", ("x.pdf", __import__("io").BytesIO(b"%PDF-1"), "application/pdf"), headers=auth_two).status_code == 403
    assert client.get("/api/publisher/announcements", headers=auth_two).json()["stats"]["total"] == 0


def test_the_api_matches_what_the_react_app_reads(client, make_announcement, upload, pdf_file):
    """If one of these keys is renamed, the frontend breaks. Keep them in step with docs/api-documentation.md."""
    a = make_announcement(category="Events", venue="Hall", event_date="2026-12-05", event_time="09:30")
    upload(a["id"], "pdf", pdf_file())
    card_keys = {"id", "title", "description", "category", "venue", "event_date", "event_time", "registration_link", "is_published", "created_at", "updated_at", "published_at", "attachments"}
    attachment_keys = {"id", "kind", "original_filename", "mime_type", "size_bytes", "available", "url", "download_url"}

    search = client.get("/api/search").json()
    assert set(search) == {"items", "page", "per_page", "pages", "total", "q", "category"}
    assert card_keys <= set(search["items"][0])
    assert set(search["items"][0]["attachments"][0]) == attachment_keys
    assert set(client.get("/api/notifications").json()) == {"unread", "items"}
    assert set(client.get("/api/dashboard").json()) == {"total", "categories"}
    error = client.get("/api/announcements/999").json()
    assert set(error["error"]) == {"code", "message", "fields"}
