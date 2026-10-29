"""Проверки связанных объектов и общих бизнес-правил консоли и веба."""

from datetime import date

from assignments import cancel_assignment, check_assignment, create_assignment
from models import Catalog
from storage import load_catalog, save_data


def test_load_restores_object_identity_dates_and_format(app_data, tmp_path):
    path = tmp_path / "objects.json"
    save_data(app_data, path)
    catalog = load_catalog(path)
    assignment = catalog.find_assignment(1)
    assert assignment.project is catalog.find_project(2)
    assert assignment.manager is catalog.find_manager(1)
    assert assignment.assigned_on == date(2026, 9, 1)
    assert catalog.to_data() == app_data


def test_candidate_selection_reuses_console_rules(app_data):
    catalog = Catalog.from_data(app_data)
    candidates = catalog.suitable_managers(1)
    assert [manager.id for manager in candidates] == [3, 1]
    for project in catalog.projects:
        for manager in catalog.managers:
            assert catalog.rejection_reason(project.id, manager.id) == (
                check_assignment(app_data["projects"], app_data["managers"],
                                 app_data["assignments"],
                                 project.id, manager.id)
            )


def test_cancelled_assignments_free_capacity_but_keep_links(app_data):
    cancel_assignment(app_data["assignments"], 1, date(2026, 10, 29))
    catalog = Catalog.from_data(app_data)
    assert catalog.manager_load(1) == 1
    assert catalog.active_assignment(2) is None
    assignment = catalog.find_assignment(1)
    assert assignment.status == "Отменено"
    assert assignment.cancelled_on == date(2026, 10, 29)
    assert assignment.project is catalog.find_project(2)
    assert catalog.to_data() == app_data


def test_full_quota_excludes_manager(app_data):
    create_assignment(app_data["projects"], app_data["managers"],
                      app_data["assignments"], 1, 1)
    app_data["projects"].append(
        {"id": 5, "name": "Новый", "specialization": "Веб"}
    )
    catalog = Catalog.from_data(app_data)
    assert [m.id for m in catalog.suitable_managers(5)] == [3]


def test_export_is_independent_of_immutable_snapshot(app_data):
    catalog = Catalog.from_data(app_data)
    exported = catalog.to_data()
    exported["projects"][0]["name"] = "Изменено"
    app_data["managers"][0]["name"] = "Изменено"
    assert catalog.find_project(1).name == "Портал"
    assert catalog.find_manager(1).name == "Анна"
    assert catalog.find_project(999) is None
    assert catalog.find_manager(999) is None
    assert catalog.find_assignment(999) is None
