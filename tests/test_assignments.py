"""Проверки правил назначения, отмены и подбора кандидатов."""

from copy import deepcopy
from datetime import date

import pytest

from assignments import (
    cancel_assignment, create_assignment, find_suitable_managers,
    get_active_assignment, get_manager_load, sort_managers_by_load,
)
from projects import add_project
from rules import has_free_capacity, specializations_match


def assign(data, project_id=1, manager_id=1):
    return create_assignment(
        data["projects"], data["managers"], data["assignments"],
        project_id, manager_id, date(2026, 10, 16),
    )


@pytest.mark.parametrize(
    "load,limit,expected",
    [(0, 1, True), (2, 3, True), (3, 3, False),
     (4, 3, False), (-1, 3, False), (0, 0, False)],
)
def test_pr1_capacity_boundary(load, limit, expected):
    assert has_free_capacity(load, limit) is expected


def test_pr1_specialization_normalization():
    assert specializations_match(" ВЕБ ", "веб")
    assert not specializations_match(" ", "")


def test_assignment_increases_load_and_prevents_duplicate(app_data):
    item = assign(app_data)
    assert item["id"] == 3
    assert item["assigned_on"] == "2026-10-16"
    assert get_manager_load(app_data["assignments"], 1) == 3
    with pytest.raises(ValueError, match="уже есть"):
        assign(app_data, manager_id=3)
    assert len(app_data["assignments"]) == 3


def test_full_manager_cannot_receive_fourth_project(app_data):
    assign(app_data)
    project = add_project(app_data["projects"], "Сайт", "Веб")
    before = deepcopy(app_data)
    with pytest.raises(ValueError, match="лимит"):
        assign(app_data, project["id"])
    assert app_data == before


@pytest.mark.parametrize(
    "project_id,manager_id,message",
    [(999, 1, "Проект"), (1, 999, "Руководитель"),
     (1, 2, "Специализация"), (1, 4, "недоступен")],
)
def test_rejected_assignment_keeps_data(
    app_data, project_id, manager_id, message
):
    before = deepcopy(app_data)
    with pytest.raises(ValueError, match=message):
        assign(app_data, project_id, manager_id)
    assert app_data == before


def test_cancel_releases_capacity_and_allows_reassignment(app_data):
    item = assign(app_data)
    cancel_assignment(app_data["assignments"], item["id"], date(2026, 10, 16))
    assert get_manager_load(app_data["assignments"], 1) == 2
    assert get_active_assignment(app_data["assignments"], 1) is None
    replacement = assign(app_data, manager_id=3)
    assert replacement["id"] == 4
    assert item["is_cancelled"] is True
    assert get_active_assignment(app_data["assignments"], 1) == replacement
    with pytest.raises(ValueError, match="уже отменено"):
        cancel_assignment(app_data["assignments"], item["id"])


def test_invalid_cancellation_does_not_mutate_data(app_data):
    before = deepcopy(app_data)
    with pytest.raises(ValueError, match="не найдено"):
        cancel_assignment(app_data["assignments"], 999)
    with pytest.raises(ValueError, match="раньше"):
        cancel_assignment(app_data["assignments"], 1, date(2020, 1, 1))
    assert app_data == before


def test_filter_excludes_wrong_busy_inactive_and_assigned(app_data):
    def candidates(project_id):
        return find_suitable_managers(
            app_data["projects"], app_data["managers"],
            app_data["assignments"], project_id,
        )

    assert [item["id"] for item in candidates(1)] == [1, 3]
    assert candidates(2) == []
    assign(app_data, manager_id=3)
    add_project(app_data["projects"], "Новый сайт", "Веб")
    assert [item["id"] for item in candidates(5)] == [1]


def test_sort_by_actual_load_does_not_reorder_source(app_data):
    before = deepcopy(app_data["managers"])
    result = sort_managers_by_load(
        app_data["managers"], app_data["assignments"]
    )
    assert [item["id"] for item in result] == [2, 3, 4, 1]
    assert app_data["managers"] == before
