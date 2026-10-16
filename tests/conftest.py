"""Независимые учебные данные: тесты не изменяют рабочее хранилище."""

import pytest


@pytest.fixture
def app_data():
    """Создать свежие списки проектов, руководителей и назначений."""
    return {
        "projects": [
            {"id": 1, "name": "Портал", "specialization": "Веб"},
            {"id": 2, "name": "Документы", "specialization": "Веб"},
            {"id": 3, "name": "Кабинет", "specialization": "Веб"},
            {"id": 4, "name": "Продажи", "specialization": "Аналитика"},
        ],
        "managers": [
            {"id": 1, "name": "Анна", "specialization": "Веб",
             "project_limit": 3, "is_active": True},
            {"id": 2, "name": "Иван", "specialization": "Аналитика",
             "project_limit": 2, "is_active": True},
            {"id": 3, "name": "Мария", "specialization": "Веб",
             "project_limit": 1, "is_active": True},
            {"id": 4, "name": "Олег", "specialization": "Веб",
             "project_limit": 2, "is_active": False},
        ],
        "assignments": [
            {"id": 1, "project_id": 2, "manager_id": 1,
             "assigned_on": "2026-09-01", "is_cancelled": False,
             "cancelled_on": None},
            {"id": 2, "project_id": 3, "manager_id": 1,
             "assigned_on": "2026-09-02", "is_cancelled": False,
             "cancelled_on": None},
        ],
    }
