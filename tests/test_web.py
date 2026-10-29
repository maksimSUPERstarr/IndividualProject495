"""HTTP-проверки ПР5 на независимом JSON без рабочей базы и сети."""

import os

import django
import pytest
from django.test import Client, override_settings
from django.urls import resolve, reverse

from assignments import cancel_assignment
from storage import empty_data, save_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


@pytest.fixture
def web(app_data, tmp_path):
    path = tmp_path / "web.json"
    save_data(app_data, path)
    with override_settings(DATA_FILE=path, DEBUG=False,
                           ALLOWED_HOSTS=["testserver"]):
        yield Client(), path


@pytest.mark.parametrize("url,title", [
    ("/", "Проекты и руководители"),
    ("/projects/", "Проекты"), ("/projects/1/", "Портал"),
    ("/managers/", "Руководители"), ("/managers/1/", "Анна"),
    ("/assignments/", "Назначения"), ("/assignments/1/", "Назначение № 1"),
])
def test_read_pages_share_navigation_and_never_write(web, url, title):
    client, path = web
    before = path.read_bytes()
    response = client.get(url)
    html = response.content.decode()
    assert response.status_code == 200
    assert title in html
    assert '<html lang="ru">' in html
    assert 'bootstrap@5.3.' in html
    for target in ("/", "/projects/", "/managers/", "/assignments/"):
        assert f'href="{target}"' in html
    assert path.read_bytes() == before


@pytest.mark.parametrize("url,title", [
    ("/projects/999/", "Проект не найден"),
    ("/managers/999/", "Руководитель не найден"),
    ("/assignments/999/", "Назначение не найдено"),
    ("/projects/abc/", "Страница не найдена"),
    ("/projects/-1/", "Страница не найдена"),
    ("/nonexistent/", "Страница не найдена"),
])
def test_invalid_ids_and_unknown_routes_return_custom_404(web, url, title):
    response = web[0].get(url)
    assert response.status_code == 404
    assert title in response.content.decode()
    assert 'Using the URLconf' not in response.content.decode()


def test_integer_converter_and_named_routes():
    assert reverse("projects:detail", args=[12]) == "/projects/12/"
    match = resolve("/managers/7/")
    assert match.view_name == "managers:detail"
    assert match.kwargs == {"manager_id": 7}


def test_project_card_excludes_ineligible_managers(web):
    html = web[0].get("/projects/1/").content.decode()
    assert "Анна" in html and "Мария" in html
    assert "Иван" not in html and "Олег" not in html
    assert "2 из 3 проектов" in html
    assigned = web[0].get("/projects/2/").content.decode()
    assert 'href="/managers/1/"' in assigned
    assert "У проекта уже есть руководитель" in assigned


def test_search_and_availability_filters(web):
    client, _ = web
    html = client.get("/projects/", {"q": "ПОРТ"}).content.decode()
    assert "Портал" in html and "Документы" not in html
    html = client.get("/projects/", {"status": "unassigned"}).content.decode()
    assert "Портал" in html and "Документы" not in html
    html = client.get("/managers/", {"q": "АННА"}).content.decode()
    assert "Анна" in html and "Мария" not in html
    html = client.get("/managers/", {"status": "available"}).content.decode()
    assert "Олег" not in html and "Мария" in html


def test_cancelled_history_and_related_links(web, app_data):
    client, path = web
    cancel_assignment(app_data["assignments"], 1)
    save_data(app_data, path)
    response = client.get("/assignments/", {"status": "cancelled"})
    html = response.content.decode()
    assert 'href="/assignments/1/"' in html
    assert 'href="/assignments/2/"' not in html
    response = client.get("/assignments/1/")
    html = response.content.decode()
    assert "Отменено" in html
    assert 'href="/projects/2/"' in html
    assert 'href="/managers/1/"' in html
    assert "1 из 3 проектов" in client.get("/managers/1/").content.decode()


def test_console_file_changes_appear_on_next_request(web, app_data):
    client, path = web
    client.get("/projects/")
    app_data["projects"].append(
        {"id": 9, "name": "Проект из консоли", "specialization": "Веб"}
    )
    save_data(app_data, path)
    assert "Проект из консоли" in client.get("/projects/").content.decode()
    assert client.get("/projects/9/").status_code == 200


@pytest.mark.parametrize("url", ["/", "/projects/", "/projects/1/",
                                 "/managers/", "/managers/1/",
                                 "/assignments/", "/assignments/1/"])
def test_post_is_rejected_and_json_unchanged(web, url):
    client, path = web
    before = path.read_bytes()
    assert client.post(url, {"name": "Попытка записи"}).status_code == 405
    assert path.read_bytes() == before


def test_query_and_json_content_are_escaped(web, app_data):
    client, path = web
    payload = '<script>alert("test")</script>'
    app_data["projects"][0]["name"] = payload
    app_data["managers"][0]["name"] = payload
    save_data(app_data, path)
    for url in ("/projects/1/", "/projects/", "/managers/1/", "/managers/"):
        html = client.get(url, {"q": payload}).content.decode()
        assert payload not in html
        assert "&lt;script&gt;" in html


def test_corrupt_json_returns_503_without_overwrite_or_path_leak(web):
    client, path = web
    path.write_text("{broken", encoding="utf-8")
    response = client.get("/")
    assert response.status_code == 503
    assert "Данные временно недоступны" in response.content.decode()
    assert str(path) not in response.content.decode()
    assert path.read_text(encoding="utf-8") == "{broken"


def test_empty_storage_has_working_lists_and_missing_details(web):
    client, path = web
    save_data(empty_data(), path)
    for url in ("/", "/projects/", "/managers/", "/assignments/"):
        assert client.get(url).status_code == 200
    assert client.get("/projects/1/").status_code == 404


def test_debug_mode_does_not_hide_entity_404(web):
    with override_settings(DEBUG=True):
        response = web[0].get("/projects/999/")
    assert response.status_code == 404
    assert "Проект не найден" in response.content.decode()
