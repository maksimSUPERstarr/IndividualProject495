"""Проверка структуры JSON и связей между записями предметной области."""

from datetime import date

from assignments import get_manager_load
from data_types import AppData, Records
from rules import specializations_match


def _validate_records(records: Records, collection: str) -> None:
    """Проверить словари, положительные ID и отсутствие дубликатов."""
    seen = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError(f"В коллекции {collection} ожидаются словари.")
        record_id = record.get("id")
        if type(record_id) is not int or record_id <= 0:
            raise ValueError(f"В коллекции {collection} некорректный ID.")
        if record_id in seen:
            raise ValueError(f"В коллекции {collection} повторяется ID.")
        seen.add(record_id)


def validate_data(data: AppData) -> None:
    """Проверить данные перед загрузкой или сохранением, не изменяя их."""
    collections = ("projects", "managers", "assignments")
    if not isinstance(data, dict) or set(data) != set(collections):
        raise ValueError(
            "JSON должен содержать projects, managers, assignments."
        )
    for name in collections:
        if not isinstance(data[name], list):
            raise ValueError(f"Коллекция {name} должна быть списком.")
        _validate_records(data[name], name)
    for record in data["projects"] + data["managers"]:
        for field in ("name", "specialization"):
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Поле {field} должно быть непустой строкой.")
    for manager in data["managers"]:
        limit = manager.get("project_limit")
        if type(limit) is not int or limit <= 0:
            raise ValueError("Лимит должен быть целым числом больше 0.")
        if type(manager.get("is_active")) is not bool:
            raise ValueError("Поле is_active должно быть bool.")

    projects = {item["id"]: item for item in data["projects"]}
    managers = {item["id"]: item for item in data["managers"]}
    active_projects = set()
    for assignment in data["assignments"]:
        project_id = assignment.get("project_id")
        manager_id = assignment.get("manager_id")
        if type(project_id) is not int or project_id not in projects:
            raise ValueError("Назначение ссылается на отсутствующий проект.")
        if type(manager_id) is not int or manager_id not in managers:
            raise ValueError("Руководитель назначения отсутствует.")
        if type(assignment.get("is_cancelled")) is not bool:
            raise ValueError("Поле is_cancelled должно быть bool.")
        assigned_on = assignment.get("assigned_on")
        if not isinstance(assigned_on, str):
            raise ValueError("Дата назначения должна быть строкой ГГГГ-ММ-ДД.")
        try:
            assigned_date = date.fromisoformat(assigned_on)
            cancelled_on = assignment.get("cancelled_on")
            if assignment["is_cancelled"]:
                if not isinstance(cancelled_on, str):
                    raise ValueError
                if date.fromisoformat(cancelled_on) < assigned_date:
                    raise ValueError
            elif cancelled_on is not None:
                raise ValueError
        except ValueError as error:
            raise ValueError("В назначении некорректные даты.") from error
        if not assignment["is_cancelled"]:
            if project_id in active_projects:
                raise ValueError("У проекта два действующих назначения.")
            active_projects.add(project_id)
            if not specializations_match(
                projects[project_id]["specialization"],
                managers[manager_id]["specialization"],
            ):
                raise ValueError("Специализации назначения различны.")
    for manager in data["managers"]:
        if get_manager_load(data["assignments"], manager["id"]) > (
            manager["project_limit"]
        ):
            raise ValueError("Загрузка руководителя превышает его лимит.")
