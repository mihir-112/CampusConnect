"""Moksh: student dashboard, cards, category navigation and states."""
from app.constants import CATEGORIES
from conftest import main_content


def test_dashboard_shows_database_announcements(client, make_announcement):
    make_announcement("Library timing change", category="General")
    html = client.get("/").get_data(as_text=True)
    assert "Library timing change" in html and "General" in html


def test_drafts_are_not_shown_to_students(client, make_announcement):
    make_announcement("Visible one")
    make_announcement("Hidden draft", published=False)
    html = main_content(client.get("/").get_data(as_text=True))
    assert "Visible one" in html and "Hidden draft" not in html


def test_empty_state_when_nothing_is_published(client):
    assert b"No announcements yet" in client.get("/").data


def test_all_four_category_links_are_present(client):
    html = client.get("/").get_data(as_text=True)
    for category in CATEGORIES:
        assert f"category={category}" in html


def test_category_link_filters_cards(client, make_announcement):
    make_announcement("Mid-sem dates", category="Examinations")
    make_announcement("Chess club", category="Clubs")
    html = client.get("/?category=Clubs").get_data(as_text=True)
    body = main_content(html)
    assert "Chess club" in body and "Mid-sem dates" not in body
    assert 'aria-current="page"' in html


def test_card_links_to_the_detail_page(client, make_announcement):
    a_id = make_announcement("Sports day")
    assert f"/notices/{a_id}" in client.get("/").get_data(as_text=True)


def test_long_descriptions_are_summarised(client, make_announcement):
    make_announcement("Long one", description="word " * 200)
    html = client.get("/").get_data(as_text=True)
    assert "word " * 100 not in html


def test_pagination_splits_results_into_pages_of_nine(client, make_announcement):
    for i in range(11):
        make_announcement(f"Notice {i:02d}")
    first = client.get("/").get_data(as_text=True)
    second = client.get("/?page=2").get_data(as_text=True)
    assert first.count('class="card"') == 9 and second.count('class="card"') == 2
    assert "Page 1 of 2" in first and "Page 2 of 2" in second


def test_bad_page_number_does_not_crash(client, make_announcement):
    make_announcement()
    assert client.get("/?page=abc").status_code == 200
    assert client.get("/?page=999").status_code == 200


def test_html_in_titles_is_escaped(client, make_announcement):
    make_announcement("<script>alert(1)</script>")
    assert b"<script>alert(1)</script>" not in client.get("/").data


def test_pages_are_mobile_ready(client):
    html = client.get("/").get_data(as_text=True)
    assert 'name="viewport"' in html and "data-nav-toggle" in html


def test_publisher_links_depend_on_login_state(client, logged_in):
    assert b"Log out" in logged_in.get("/").data
    fresh = logged_in.application.test_client()
    assert b"Publisher login" in fresh.get("/").data
