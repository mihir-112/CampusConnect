"""Publisher login, tokens, logout and password storage. Owner: publisher-auth."""
import hashlib
import io
import time
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from sqlalchemy import select

from backend.cli import main as cli_main
from backend.core.errors import AppError
from features.publisher_auth.backend.models.publisher import Publisher
from features.publisher_auth.backend.security.passwords import hash_password, verify_password
from features.publisher_auth.backend.security.throttle import LoginThrottle
from features.publisher_auth.backend.services import auth_service


def login(client, username="editor", password="password123"):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def test_login_returns_a_token_and_the_publisher(client, make_publisher):
    make_publisher("editor")
    body = login(client).json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 7200
    assert body["publisher"]["username"] == "editor"
    assert "password" not in str(body["publisher"]).lower()


def test_wrong_password_and_unknown_user_get_the_same_answer(client, make_publisher):
    make_publisher("editor")
    wrong = login(client, password="not-the-password")
    unknown = login(client, username="nobody")
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_login_requires_both_fields(client):
    fields = client.post("/api/auth/login", json={"username": " ", "password": ""}).json()["error"]["fields"]
    assert set(fields) == {"username", "password"}


def test_me_returns_the_logged_in_publisher(client, auth):
    assert client.get("/api/auth/me", headers=auth).json()["username"] == "editor"


def test_me_without_token_is_401(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_garbage_and_forged_tokens_are_rejected(client, make_publisher, settings):
    make_publisher("editor")
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer abc.def.ghi"}).status_code == 401
    forged = jwt.encode({"sub": "1", "jti": "x", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, "another-secret-key-0123456789abcdef", algorithm="HS256")
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer " + forged}).status_code == 401


def test_expired_token_is_rejected(client, make_publisher, settings):
    make_publisher("editor")
    expired = jwt.encode(
        {"sub": "1", "jti": "old", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}, settings.secret_key, algorithm="HS256"
    )
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer " + expired}).status_code == 401


def test_token_without_expiry_is_rejected(client, make_publisher, settings):
    make_publisher("editor")
    token = jwt.encode({"sub": "1", "jti": "forever"}, settings.secret_key, algorithm="HS256")
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer " + token}).status_code == 401


def test_logout_ends_the_session(client, auth):
    assert client.post("/api/auth/logout", headers=auth).json() == {"ok": True}
    assert client.get("/api/auth/me", headers=auth).status_code == 401
    assert client.post("/api/announcements", json={"title": "t", "description": "d", "category": "General"}, headers=auth).status_code == 401


def test_logout_only_ends_that_token(client, make_publisher):
    first = make_publisher("editor")
    second = {"Authorization": "Bearer " + login(client).json()["access_token"]}
    client.post("/api/auth/logout", headers=first)
    assert client.get("/api/auth/me", headers=second).status_code == 200


def test_logout_needs_a_valid_token(client):
    assert client.post("/api/auth/logout").status_code == 401


def test_repeated_failures_lock_the_account_for_a_while(client, make_publisher):
    make_publisher("editor")
    for _ in range(5):
        assert login(client, password="wrong-password").status_code == 401
    locked = login(client)  # even the right password is refused during the lock
    assert locked.status_code == 429
    assert locked.json()["error"]["code"] == "too_many_attempts"


def test_successful_login_clears_earlier_failures(client, make_publisher):
    make_publisher("editor")
    for _ in range(4):
        login(client, password="wrong-password")
    assert login(client).status_code == 200
    for _ in range(4):
        assert login(client, password="wrong-password").status_code == 401


def test_throttle_window_expires():
    throttle = LoginThrottle(max_attempts=2, window_seconds=0.05)
    throttle.record_failure("a")
    throttle.record_failure("a")
    assert throttle.is_locked("a")
    time.sleep(0.08)
    assert not throttle.is_locked("a")


def test_passwords_are_stored_hashed(app, client, make_publisher):
    make_publisher("editor")
    with app.state.db.session_factory() as db:
        stored = db.scalar(select(Publisher)).password_hash
    assert "password123" not in stored
    assert stored.startswith("$argon2")
    assert verify_password(stored, "password123")
    assert not verify_password(stored, "password124")


def test_same_password_gets_different_hashes():
    assert hash_password("password123") != hash_password("password123")


def test_old_flask_scrypt_hash_still_works_and_is_upgraded(app, client):
    salt, n, r, p = "abcDEF123", 16384, 8, 1
    digest = hashlib.scrypt(b"password123", salt=salt.encode(), n=n, r=r, p=p, maxmem=132 * n * r * p).hex()
    with app.state.db.session_factory() as db:
        db.add(Publisher(username="legacy", email="legacy@example.com", password_hash=f"scrypt:{n}:{r}:{p}${salt}${digest}"))
        db.commit()
    assert login(client, "legacy", "wrong-password").status_code == 401
    assert login(client, "legacy").status_code == 200
    with app.state.db.session_factory() as db:
        assert db.scalar(select(Publisher).where(Publisher.username == "legacy")).password_hash.startswith("$argon2")
    assert login(client, "legacy").status_code == 200


def test_old_flask_pbkdf2_hash_still_works(app, client):
    salt = "saltsalt"
    digest = hashlib.pbkdf2_hmac("sha256", b"password123", salt.encode(), 1000).hex()
    with app.state.db.session_factory() as db:
        db.add(Publisher(username="old", email="old@example.com", password_hash=f"pbkdf2:sha256:1000${salt}${digest}"))
        db.commit()
    assert login(client, "old").status_code == 200


@pytest.mark.parametrize("stored", ["", "plain-text", "md5$salt$abc", "scrypt:x:y:z$s$h"])
def test_malformed_stored_hashes_never_verify(stored):
    assert verify_password(stored, "password123") is False


def test_create_publisher_rules(app, client):
    with app.state.db.session_factory() as db:
        with pytest.raises(AppError) as short:
            auth_service.create_publisher(db, "ab", "ab@example.com", "short")
        assert "password" in short.value.fields
        with pytest.raises(AppError) as bad_email:
            auth_service.create_publisher(db, "ab", "not-an-email", "password123")
        assert "email" in bad_email.value.fields
        auth_service.create_publisher(db, "ab", "AB@Example.com", "password123")
        with pytest.raises(AppError) as duplicate:
            auth_service.create_publisher(db, "ab", "other@example.com", "password123")
        assert duplicate.value.status_code == 409


def test_cli_creates_a_publisher_that_can_log_in(monkeypatch, tmp_path, capsys):
    db_url = f"sqlite:///{(tmp_path / 'cli.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    code = cli_main(["create-publisher", "--username", "cliuser", "--email", "cli@example.com", "--password", "password123"])
    assert code == 0
    assert "created" in capsys.readouterr().out
    assert cli_main(["create-publisher", "--username", "cliuser", "--email", "cli@example.com", "--password", "password123"]) == 1


def test_students_never_need_a_token_for_public_pages(client, make_announcement):
    make_announcement()
    assert client.get("/api/announcements").status_code == 200
    assert client.get("/api/search").status_code == 200
    assert client.get("/api/notifications").status_code == 200
    assert client.get("/api/dashboard").status_code == 200


def test_cors_allows_the_frontend_origin_only(client):
    ok = client.options("/api/announcements", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    other = client.options("/api/announcements", headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in other.headers
