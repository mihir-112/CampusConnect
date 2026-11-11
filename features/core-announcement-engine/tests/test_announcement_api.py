"""Announcement CRUD, validation, publishing and ownership. Owner: Mihir."""
import pytest

VALID = {"title": "Hackathon", "description": "Build something.", "category": "Events"}


def test_create_draft_by_default(client, auth):
    response = client.post("/api/announcements", json=VALID, headers=auth)
    assert response.status_code == 201
    body = response.json()
    assert body["is_published"] is False
    assert body["published_at"] is None
    assert body["created_at"].endswith("Z")


def test_create_and_publish_sets_published_at(client, auth):
    body = client.post("/api/announcements", json={**VALID, "is_published": True}, headers=auth).json()
    assert body["is_published"] is True
    assert body["published_at"] is not None


def test_event_details_are_saved(make_announcement):
    a = make_announcement(category="Events", venue="Main Auditorium", event_date="2026-12-05", event_time="14:30", registration_link="https://example.com/r")
    assert (a["venue"], a["event_date"], a["registration_link"]) == ("Main Auditorium", "2026-12-05", "https://example.com/r")
    assert a["event_time"].startswith("14:30")


def test_title_and_description_are_trimmed(client, auth):
    body = client.post("/api/announcements", json={**VALID, "title": "  Padded  ", "description": " text "}, headers=auth).json()
    assert (body["title"], body["description"]) == ("Padded", "text")


@pytest.mark.parametrize(
    "change, field",
    [
        ({"title": ""}, "title"),
        ({"title": "x" * 151}, "title"),
        ({"description": "   "}, "description"),
        ({"category": "Sports"}, "category"),
        ({"registration_link": "ftp://nope"}, "registration_link"),
        ({"registration_link": "javascript:alert(1)"}, "registration_link"),
        ({"event_date": "05/12/2026"}, "event_date"),
        ({"event_time": "2pm"}, "event_time"),
        ({"venue": "v" * 151}, "venue"),
    ],
)
def test_validation_errors_name_the_field(client, auth, change, field):
    response = client.post("/api/announcements", json={**VALID, **change}, headers=auth)
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert field in error["fields"]
    assert "Value error" not in error["fields"][field]


def test_missing_required_fields_are_reported(client, auth):
    fields = client.post("/api/announcements", json={}, headers=auth).json()["error"]["fields"]
    assert set(fields) == {"title", "description", "category"}
    assert fields["title"] == "Title is required."


def test_blank_optional_fields_become_empty(client, auth):
    body = client.post("/api/announcements", json={**VALID, "venue": " ", "event_date": "", "registration_link": ""}, headers=auth).json()
    assert body["venue"] is None and body["event_date"] is None and body["registration_link"] is None


def test_all_four_categories_are_accepted(client, auth):
    for category in ("Examinations", "Events", "Clubs", "General"):
        assert client.post("/api/announcements", json={**VALID, "category": category}, headers=auth).status_code == 201


def test_update_changes_fields_and_keeps_status(client, auth, make_announcement):
    a = make_announcement(published=True)
    response = client.put(f"/api/announcements/{a['id']}", json={**VALID, "title": "New title"}, headers=auth)
    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["is_published"] is True


def test_update_can_publish_and_unpublish(client, auth, make_announcement):
    a = make_announcement(published=False)
    assert client.put(f"/api/announcements/{a['id']}", json={**VALID, "is_published": True}, headers=auth).json()["is_published"] is True
    assert client.put(f"/api/announcements/{a['id']}", json={**VALID, "is_published": False}, headers=auth).json()["is_published"] is False


def test_update_validates(client, auth, make_announcement):
    a = make_announcement()
    assert client.put(f"/api/announcements/{a['id']}", json={**VALID, "title": ""}, headers=auth).status_code == 422


def test_publish_and_unpublish_endpoints(client, auth, make_announcement):
    a = make_announcement(published=False)
    assert client.get(f"/api/announcements/{a['id']}").status_code == 404
    assert client.patch(f"/api/announcements/{a['id']}/publish", headers=auth).json()["is_published"] is True
    assert client.get(f"/api/announcements/{a['id']}").status_code == 200
    assert client.patch(f"/api/announcements/{a['id']}/unpublish", headers=auth).json()["is_published"] is False
    assert client.get(f"/api/announcements/{a['id']}").status_code == 404


def test_published_at_is_kept_when_republished(client, auth, make_announcement):
    a = make_announcement(published=True)
    client.patch(f"/api/announcements/{a['id']}/unpublish", headers=auth)
    again = client.patch(f"/api/announcements/{a['id']}/publish", headers=auth).json()
    assert again["published_at"] == a["published_at"]


def test_delete_announcement(client, auth, make_announcement):
    a = make_announcement()
    assert client.delete(f"/api/announcements/{a['id']}", headers=auth).status_code == 204
    assert client.get(f"/api/announcements/{a['id']}").status_code == 404
    assert client.delete(f"/api/announcements/{a['id']}", headers=auth).status_code == 404


def test_students_see_only_published_newest_first(client, make_announcement):
    make_announcement("Oldest")
    make_announcement("Hidden draft", published=False)
    make_announcement("Newest")
    titles = [i["title"] for i in client.get("/api/announcements").json()["items"]]
    assert titles == ["Newest", "Oldest"]


def test_list_filters_by_category_and_paginates(client, make_announcement):
    for n in range(11):
        make_announcement(f"Club {n}", category="Clubs")
    make_announcement("Exam", category="Examinations")
    page = client.get("/api/announcements?category=Clubs&per_page=9").json()
    assert (page["total"], page["pages"], len(page["items"])) == (11, 2, 9)
    assert len(client.get("/api/announcements?category=Clubs&page=2").json()["items"]) == 2
    assert client.get("/api/announcements?category=Nope").status_code == 422


def test_students_cannot_open_drafts_but_the_owner_can(client, auth, other_auth, make_announcement):
    draft = make_announcement(published=False)
    url = f"/api/announcements/{draft['id']}"
    assert client.get(url).status_code == 404
    assert client.get(url, headers=other_auth).status_code == 404
    assert client.get(url, headers=auth).status_code == 200


def test_write_endpoints_need_login(client, make_announcement):
    a = make_announcement()
    assert client.post("/api/announcements", json=VALID).status_code == 401
    assert client.put(f"/api/announcements/{a['id']}", json=VALID).status_code == 401
    assert client.patch(f"/api/announcements/{a['id']}/publish").status_code == 401
    assert client.delete(f"/api/announcements/{a['id']}").status_code == 401
    assert client.get("/api/publisher/announcements").status_code == 401


def test_only_the_owner_can_change_an_announcement(client, other_auth, make_announcement):
    a = make_announcement()
    url = f"/api/announcements/{a['id']}"
    assert client.put(url, json=VALID, headers=other_auth).status_code == 403
    assert client.patch(url + "/unpublish", headers=other_auth).status_code == 403
    assert client.delete(url, headers=other_auth).status_code == 403
    assert client.get(url).json()["title"] == a["title"]  # unchanged


def test_publisher_list_shows_only_own_announcements_with_stats(client, other_auth, make_announcement):
    make_announcement("Mine published", category="Events")
    make_announcement("Mine draft", category="Clubs", published=False)
    make_announcement("Theirs", headers=other_auth)
    from_mine = client.get("/api/publisher/announcements", headers=other_auth).json()
    assert from_mine["stats"]["total"] == 1

    # Log in again as the first publisher to read their list.
    editor = client.post("/api/auth/login", json={"username": "editor", "password": "password123"}).json()["access_token"]
    body = client.get("/api/publisher/announcements", headers={"Authorization": "Bearer " + editor}).json()
    assert body["stats"] == {"total": 2, "published": 1, "drafts": 1, "by_category": {"Examinations": 0, "Events": 1, "Clubs": 1, "General": 0}}
    assert {i["title"] for i in body["items"]} == {"Mine published", "Mine draft"}
