"""Shared pytest fixtures. Every test gets its own app, its own temporary SQLite file and upload folder,
so the real development database is never touched."""
import io

import pytest
from fastapi.testclient import TestClient

import features  # noqa: F401
from backend.core.config import Settings
from backend.main import create_app
from features.publisher_auth.backend.services import auth_service

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
PDF_BYTES = b"%PDF-1.4\n" + b"0" * 64
PASSWORD = "password123"


@pytest.fixture
def settings(tmp_path):
    return Settings(
        database_url=f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        upload_dir=str(tmp_path / "uploads"),
        secret_key="test-secret-key-for-pytest-only-0123456789",
    )


@pytest.fixture
def app(settings):
    return create_app(settings)


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:  # the `with` runs startup, which creates the tables
        yield test_client


@pytest.fixture
def make_publisher(app, client):
    def _make(username="editor"):
        with app.state.db.session_factory() as db:
            auth_service.create_publisher(db, username, f"{username}@example.com", PASSWORD)
        response = client.post("/api/auth/login", json={"username": username, "password": PASSWORD})
        return {"Authorization": "Bearer " + response.json()["access_token"]}

    return _make


@pytest.fixture
def auth(make_publisher):
    """Authorization header for the publisher 'editor'."""
    return make_publisher("editor")


@pytest.fixture
def other_auth(make_publisher):
    return make_publisher("other")


@pytest.fixture
def make_announcement(client, auth):
    """Create an announcement through the API and return its JSON."""

    def _make(title="Mid-sem timetable", category="Examinations", published=True, headers=None, **extra):
        body = {"title": title, "description": f"Full details about {title}.", "category": category, "is_published": published, **extra}
        response = client.post("/api/announcements", json=body, headers=headers or auth)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


@pytest.fixture
def png_file():
    return lambda name="poster.png": (name, io.BytesIO(PNG_BYTES), "image/png")


@pytest.fixture
def pdf_file():
    return lambda name="notice.pdf": (name, io.BytesIO(PDF_BYTES), "application/pdf")


@pytest.fixture
def upload(client, auth):
    def _upload(announcement_id, kind, file, headers=None):
        return client.post(
            f"/api/announcements/{announcement_id}/attachments", data={"kind": kind}, files={"file": file}, headers=headers or auth
        )

    return _upload


CLIENT_A = "browser-aaaa-1111"
CLIENT_B = "browser-bbbb-2222"
