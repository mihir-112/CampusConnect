"""Keyword search and category filtering. Owner: Mridul."""


def titles(client, query=""):
    return [i["title"] for i in client.get("/api/search" + query).json()["items"]]


def test_search_with_no_filters_lists_everything_newest_first(client, make_announcement):
    make_announcement("First")
    make_announcement("Second")
    assert titles(client) == ["Second", "First"]


def test_keyword_matches_title_description_and_venue(client, make_announcement):
    make_announcement("Library hours", description="Open late during exams.")
    make_announcement("Quiz night", description="Fun evening.", venue="Library lawn")
    make_announcement("Sports day", description="Track and field, library closed.")
    make_announcement("Unrelated", description="Nothing to see.")
    assert sorted(titles(client, "?q=library")) == ["Library hours", "Quiz night", "Sports day"]


def test_search_ignores_case_and_extra_spaces(client, make_announcement):
    make_announcement("Mid-Sem Timetable")
    assert titles(client, "?q=%20%20TIMETABLE%20") == ["Mid-Sem Timetable"]


def test_category_filter(client, make_announcement):
    make_announcement("Exam A", category="Examinations")
    make_announcement("Club B", category="Clubs")
    assert titles(client, "?category=Clubs") == ["Club B"]


def test_keyword_and_category_together(client, make_announcement):
    make_announcement("Robotics club meet", category="Clubs")
    make_announcement("Robotics exam", category="Examinations")
    assert titles(client, "?q=robotics&category=Clubs") == ["Robotics club meet"]


def test_no_results_gives_an_empty_list(client, make_announcement):
    make_announcement("Something")
    body = client.get("/api/search?q=zzzz").json()
    assert (body["items"], body["total"], body["pages"]) == ([], 0, 1)
    assert body["q"] == "zzzz"


def test_drafts_are_never_returned(client, make_announcement):
    make_announcement("Secret draft", published=False)
    assert titles(client, "?q=secret") == []


def test_unpublished_announcements_leave_search(client, auth, make_announcement):
    a = make_announcement("Going away")
    client.patch(f"/api/announcements/{a['id']}/unpublish", headers=auth)
    assert titles(client, "?q=going") == []


def test_percent_and_underscore_match_literally(client, make_announcement):
    make_announcement("Fees: 50% discount")
    make_announcement("Plain notice")
    assert titles(client, "?q=%25") == ["Fees: 50% discount"]
    assert titles(client, "?q=_") == []


def test_invalid_category_is_a_validation_error(client):
    response = client.get("/api/search?category=Sports")
    assert response.status_code == 422
    assert "category" in response.json()["error"]["fields"]


def test_pagination(client, make_announcement):
    for n in range(10):
        make_announcement(f"Notice {n}")
    first = client.get("/api/search?per_page=4").json()
    assert (first["total"], first["pages"], len(first["items"])) == (10, 3, 4)
    last = client.get("/api/search?per_page=4&page=3").json()
    assert len(last["items"]) == 2
    assert client.get("/api/search?page=0").status_code == 422


def test_search_results_include_attachment_flags(client, make_announcement, upload, pdf_file):
    a = make_announcement("With file")
    upload(a["id"], "pdf", pdf_file())
    assert client.get("/api/search?q=with").json()["items"][0]["attachments"][0]["kind"] == "pdf"
