"""The student dashboard numbers. Owner: student-dashboard."""


def test_dashboard_lists_all_four_categories_even_when_empty(client):
    body = client.get("/api/dashboard").json()
    assert body["total"] == 0
    assert [c["name"] for c in body["categories"]] == ["Examinations", "Events", "Clubs", "General"]
    assert all(c["count"] == 0 for c in body["categories"])


def test_dashboard_counts_published_announcements_only(client, make_announcement):
    make_announcement("A", category="Events")
    make_announcement("B", category="Events")
    make_announcement("C", category="Clubs")
    make_announcement("Draft", category="General", published=False)
    body = client.get("/api/dashboard").json()
    assert body["total"] == 3
    assert {c["name"]: c["count"] for c in body["categories"]} == {"Examinations": 0, "Events": 2, "Clubs": 1, "General": 0}


def test_dashboard_needs_no_login(client):
    assert client.get("/api/dashboard").status_code == 200
