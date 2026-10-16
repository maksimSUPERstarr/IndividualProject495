"""Добавление и поиск записей, в том числе некорректные поля."""

import pytest

from managers import add_manager, find_managers
from projects import add_project, find_projects


def test_add_and_search_project_with_normalized_name():
    items = []
    first = add_project(items, "  Портал задач  ", " Веб ")
    second = add_project(items, "Отчёты", "Аналитика")
    assert first == {"id": 1, "name": "Портал задач", "specialization": "Веб"}
    assert second["id"] == 2
    assert find_projects(items, "ПОРТАЛ") == [first]


@pytest.mark.parametrize("name,direction", [("", "Веб"), ("Имя", " ")])
def test_empty_project_fields_are_rejected(name, direction):
    items = []
    with pytest.raises(ValueError):
        add_project(items, name, direction)
    assert items == []


def test_add_and_search_manager_by_name():
    items = []
    manager = add_manager(items, " Анна Смирнова ", "Веб", 3)
    assert manager["id"] == 1
    assert find_managers(items, "СМИРНОВА") == [manager]


@pytest.mark.parametrize("limit", [0, -1, True, 1.5, "3"])
def test_invalid_manager_limit_is_rejected(limit):
    items = []
    with pytest.raises(ValueError):
        add_manager(items, "Анна", "Веб", limit)
    assert items == []
