"""Aariz: publisher login, logout, protected routes and CSRF."""
from app.extensions import db
from app.models import Announcement, Publisher
from conftest import csrf_token_from, create_publisher


def test_login_page_loads(client):
    assert client.get("/auth/login").status_code == 200


def test_valid_login_redirects_to_admin(client, publisher, login):
    response = login()
    assert response.status_code == 302 and response.headers["Location"].endswith("/admin/")
    assert client.get("/admin/").status_code == 200


def test_wrong_password_is_rejected(client, publisher, login):
    response = login(password="wrong-password")
    assert b"Invalid username or password." in response.data
    assert client.get("/admin/").status_code == 302


def test_unknown_user_gets_the_same_message(client, publisher, login):
    assert b"Invalid username or password." in login(username="nobody").data


def test_empty_form_shows_required_errors(client):
    response = client.post("/auth/login", data={})
    assert response.status_code == 200 and b"This field is required" in response.data


def test_password_is_stored_hashed(app, publisher):
    with app.app_context():
        p = db.session.get(Publisher, publisher)
        assert p.password_hash != "password123"
        assert p.check_password("password123") and not p.check_password("other")


def test_admin_pages_redirect_anonymous_users_to_login(client, make_announcement):
    a_id = make_announcement()
    for url in ("/admin/", "/admin/announcements/new", f"/admin/announcements/{a_id}/edit"):
        response = client.get(url)
        assert response.status_code == 302 and "/auth/login" in response.headers["Location"]


def test_anonymous_post_actions_change_nothing(app, client, make_announcement):
    a_id = make_announcement()
    assert client.post(f"/admin/announcements/{a_id}/delete").status_code == 302
    assert client.post(f"/admin/announcements/{a_id}/publish").status_code == 302
    assert client.post("/admin/announcements/new", data={"title": "x"}).status_code == 302
    with app.app_context():
        assert Announcement.query.count() == 1
        assert db.session.get(Announcement, a_id).is_published is True


def test_logout_needs_post_and_ends_the_session(logged_in):
    assert logged_in.get("/auth/logout").status_code == 405
    assert logged_in.post("/auth/logout").status_code == 302
    assert logged_in.get("/admin/").status_code == 302


def test_login_redirect_ignores_external_next_urls(client, publisher):
    for target in ("//evil.example.com", "https://evil.example.com", "/\\evil.example.com"):
        response = client.post(f"/auth/login?next={target}", data={"username": "editor", "password": "password123"})
        assert response.headers["Location"].endswith("/admin/")
        client.post("/auth/logout")


def test_login_follows_safe_next_url(client, publisher):
    response = client.post("/auth/login?next=/admin/announcements/new",
                           data={"username": "editor", "password": "password123"})
    assert response.headers["Location"].endswith("/admin/announcements/new")


def test_publisher_cannot_edit_or_delete_someone_elses_announcement(client, make_announcement, other_publisher, login):
    a_id = make_announcement()  # written by "editor"
    login("other", "password123")
    assert client.get(f"/admin/announcements/{a_id}/edit").status_code == 403
    assert client.post(f"/admin/announcements/{a_id}/delete").status_code == 403
    assert client.post(f"/admin/announcements/{a_id}/publish").status_code == 403


def test_already_logged_in_user_skips_login_page(logged_in):
    assert logged_in.get("/auth/login").status_code == 302


def test_csrf_blocks_login_without_token(csrf_app):
    create_publisher(csrf_app)
    client = csrf_app.test_client()
    response = client.post("/auth/login", data={"username": "editor", "password": "password123"})
    assert response.status_code == 400


def test_csrf_login_and_logout_work_with_token(csrf_app):
    create_publisher(csrf_app)
    client = csrf_app.test_client()
    token = csrf_token_from(client.get("/auth/login").get_data(as_text=True))
    response = client.post("/auth/login", data={"username": "editor", "password": "password123", "csrf_token": token})
    assert response.status_code == 302
    page = client.get("/admin/").get_data(as_text=True)
    assert client.post("/auth/logout").status_code == 400  # no token
    assert client.post("/auth/logout", data={"csrf_token": csrf_token_from(page)}).status_code == 302
