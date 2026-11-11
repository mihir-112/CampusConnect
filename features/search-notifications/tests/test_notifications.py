"""Notifications and per-browser read state. Owner: Mridul."""
from conftest import CLIENT_A, CLIENT_B


def listing(client, browser=CLIENT_A, query=""):
    return client.get("/api/notifications" + query, headers={"X-Client-Id": browser}).json()


def read(client, notification_id, browser=CLIENT_A):
    return client.patch(f"/api/notifications/{notification_id}/read", headers={"X-Client-Id": browser})


def test_publishing_creates_a_notification(client, make_announcement):
    make_announcement("Results out", category="Examinations")
    body = listing(client)
    assert body["unread"] == 1
    assert body["items"][0]["message"] == "New in Examinations: Results out"
    assert body["items"][0]["is_read"] is False


def test_drafts_do_not_notify(client, make_announcement):
    make_announcement("Draft", published=False)
    assert listing(client) == {"unread": 0, "items": []}


def test_publishing_a_draft_later_notifies(client, auth, make_announcement):
    a = make_announcement("Later", published=False)
    client.patch(f"/api/announcements/{a['id']}/publish", headers=auth)
    assert listing(client)["unread"] == 1


def test_publishing_twice_does_not_duplicate(client, auth, make_announcement):
    a = make_announcement()
    client.patch(f"/api/announcements/{a['id']}/publish", headers=auth)
    assert len(listing(client)["items"]) == 1


def test_unpublishing_removes_the_notification(client, auth, make_announcement):
    a = make_announcement()
    client.patch(f"/api/announcements/{a['id']}/unpublish", headers=auth)
    assert listing(client)["items"] == []


def test_republishing_notifies_again(client, auth, make_announcement):
    a = make_announcement()
    read(client, listing(client)["items"][0]["id"])
    client.patch(f"/api/announcements/{a['id']}/unpublish", headers=auth)
    client.patch(f"/api/announcements/{a['id']}/publish", headers=auth)
    assert listing(client)["unread"] == 1


def test_deleting_the_announcement_removes_the_notification(client, auth, make_announcement):
    a = make_announcement()
    read(client, listing(client)["items"][0]["id"])  # a read receipt exists too
    assert client.delete(f"/api/announcements/{a['id']}", headers=auth).status_code == 204
    assert listing(client)["items"] == []


def test_updating_via_put_can_publish_and_notify(client, auth, make_announcement):
    a = make_announcement("Edit me", published=False)
    body = {"title": "Edit me", "description": "d", "category": "General", "is_published": True}
    client.put(f"/api/announcements/{a['id']}", json=body, headers=auth)
    assert listing(client)["unread"] == 1


def test_mark_one_as_read(client, make_announcement):
    make_announcement("One")
    make_announcement("Two")
    first = listing(client)["items"][0]
    response = read(client, first["id"])
    assert response.json() == {"ok": True, "unread": 1}
    after = listing(client)
    assert after["unread"] == 1
    assert [i["is_read"] for i in after["items"]] == [True, False]


def test_marking_read_twice_is_harmless(client, make_announcement):
    make_announcement()
    nid = listing(client)["items"][0]["id"]
    assert read(client, nid).status_code == 200
    assert read(client, nid).json()["unread"] == 0


def test_mark_all_as_read(client, make_announcement):
    for n in range(3):
        make_announcement(f"N{n}")
    response = client.patch("/api/notifications/read-all", headers={"X-Client-Id": CLIENT_A})
    assert response.json() == {"ok": True, "unread": 0}
    assert all(i["is_read"] for i in listing(client)["items"])


def test_read_state_is_per_browser(client, make_announcement):
    make_announcement()
    nid = listing(client)["items"][0]["id"]
    read(client, nid, CLIENT_A)
    assert listing(client, CLIENT_A)["unread"] == 0
    assert listing(client, CLIENT_B)["unread"] == 1


def test_a_browser_without_an_id_sees_everything_unread(client, make_announcement):
    make_announcement()
    assert client.get("/api/notifications").json()["unread"] == 1


def test_marking_read_requires_a_valid_browser_id(client, make_announcement):
    make_announcement()
    nid = listing(client)["items"][0]["id"]
    assert client.patch(f"/api/notifications/{nid}/read").status_code == 400
    assert read(client, nid, "bad id!").status_code == 400
    assert client.patch("/api/notifications/read-all", headers={"X-Client-Id": "x"}).status_code == 400


def test_unknown_notification_is_404(client):
    assert read(client, 4242).status_code == 404


def test_list_limit_and_newest_first(client, make_announcement):
    for n in range(12):
        make_announcement(f"Item {n}")
    assert len(listing(client)["items"]) == 10
    items = listing(client, query="?limit=3")["items"]
    assert [i["message"] for i in items] == ["New in Examinations: Item 11", "New in Examinations: Item 10", "New in Examinations: Item 9"]
    assert client.get("/api/notifications?limit=500").status_code == 422


def test_unread_count_only_covers_visible_notifications(client, make_announcement):
    for n in range(12):
        make_announcement(f"Item {n}")
    assert listing(client)["unread"] == 10  # the bell shows the latest ten
