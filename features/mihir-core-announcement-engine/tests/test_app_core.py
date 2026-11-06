"""Application startup, database and shared error format. Owner: Mihir."""
from sqlalchemy import inspect

from backend.core.config import Settings
from backend.main import create_app


def test_app_starts_and_reports_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_swagger_docs_are_served(client):
    assert client.get("/docs").status_code == 200
    assert "/api/announcements" in client.get("/openapi.json").json()["paths"]


def test_all_tables_are_created(app, client):
    tables = set(inspect(app.state.db.engine).get_table_names())
    assert {"announcements", "publishers", "attachments", "notifications", "notification_reads", "revoked_tokens"} <= tables


def test_each_app_uses_its_own_database(tmp_path):
    first = create_app(Settings(f"sqlite:///{(tmp_path / 'a.db').as_posix()}", str(tmp_path / "ua"), "k" * 32))
    second = create_app(Settings(f"sqlite:///{(tmp_path / 'b.db').as_posix()}", str(tmp_path / "ub"), "k" * 32))
    assert first.state.db.engine.url != second.state.db.engine.url


def test_unknown_route_uses_shared_error_format(client):
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_wrong_method_uses_shared_error_format(client):
    response = client.put("/api/health")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"


def test_missing_announcement_is_a_clear_404(client):
    body = client.get("/api/announcements/999").json()["error"]
    assert body["code"] == "not_found"
    assert body["fields"] is None


def test_foreign_keys_are_enforced(app, client):
    from sqlalchemy import text

    with app.state.db.engine.connect() as connection:
        assert connection.execute(text("PRAGMA foreign_keys")).scalar() == 1
