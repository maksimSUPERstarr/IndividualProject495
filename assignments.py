"""Назначения, отмена, расчёт загрузки и подбор руководителей."""

from datetime import date

from data_types import Record, Records
from managers import find_manager_by_id
from projects import find_project_by_id
from rules import get_assignment_rejection_reason
from utils import find_by_id, next_id


def get_manager_load(assignments: Records, manager_id: int) -> int:
    """Посчитать только действующие назначения выбранного руководителя."""
    return sum(
        1 for item in assignments
        if item["manager_id"] == manager_id and not item["is_cancelled"]
    )


def get_active_assignment(
    assignments: Records, project_id: int
) -> Record | None:
    """Найти действующее назначение проекта, пропуская отменённые записи."""
    return next(
        (item for item in assignments
         if item["project_id"] == project_id and not item["is_cancelled"]),
        None,
    )


def check_assignment(
    projects: Records,
    managers: Records,
    assignments: Records,
    project_id: int,
    manager_id: int,
) -> str:
    """Объяснить отказ, применив к коллекциям правила исходного ПР1."""
    project = find_project_by_id(projects, project_id)
    manager = find_manager_by_id(managers, manager_id)
    if project is None:
        return "Проект с указанным ID не найден."
    if manager is None:
        return "Руководитель с указанным ID не найден."
    active = get_active_assignment(assignments, project_id)
    return get_assignment_rejection_reason(
        project["specialization"],
        manager["specialization"],
        get_manager_load(assignments, manager_id),
        manager["project_limit"],
        manager["is_active"],
        str(active["manager_id"]) if active else "",
    )


def create_assignment(
    projects: Records,
    managers: Records,
    assignments: Records,
    project_id: int,
    manager_id: int,
    assigned_on: date | None = None,
) -> Record:
    """Создать назначение, если все ограничения выполнены."""
    reason = check_assignment(
        projects, managers, assignments, project_id, manager_id
    )
    if reason:
        raise ValueError(reason)
    assignment = {
        "id": next_id(assignments),
        "project_id": project_id,
        "manager_id": manager_id,
        "assigned_on": (assigned_on or date.today()).isoformat(),
        "is_cancelled": False,
        "cancelled_on": None,
    }
    assignments.append(assignment)
    return assignment


def cancel_assignment(
    assignments: Records,
    assignment_id: int,
    cancelled_on: date | None = None,
) -> Record:
    """Отменить назначение, сохранив запись в истории."""
    assignment = find_by_id(assignments, assignment_id)
    if assignment is None:
        raise ValueError("Назначение с указанным ID не найдено.")
    if assignment["is_cancelled"]:
        raise ValueError("Назначение уже отменено.")
    cancellation_date = cancelled_on or date.today()
    if cancellation_date < date.fromisoformat(assignment["assigned_on"]):
        raise ValueError("Дата отмены не может быть раньше назначения.")
    assignment["is_cancelled"] = True
    assignment["cancelled_on"] = cancellation_date.isoformat()
    return assignment


def find_suitable_managers(
    projects: Records,
    managers: Records,
    assignments: Records,
    project_id: int,
) -> Records:
    """Отобрать доступных кандидатов по специализации и свободной загрузке."""
    if find_project_by_id(projects, project_id) is None:
        raise ValueError("Проект с указанным ID не найден.")
    return [
        manager for manager in managers
        if not check_assignment(
            projects, managers, assignments, project_id, manager["id"]
        )
    ]


def sort_managers_by_load(managers: Records, assignments: Records) -> Records:
    """Вернуть новый список, отсортированный lambda-функцией по загрузке."""
    return sorted(
        managers,
        key=lambda manager: (
            get_manager_load(assignments, manager["id"]),
            manager["name"].casefold(),
            manager["id"],
        ),
    )
