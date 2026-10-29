"""Связанный снимок данных и адаптер существующих бизнес-правил ПР2."""

from dataclasses import dataclass
from datetime import date

from assignments import (
    check_assignment, find_suitable_managers, get_manager_load,
)
from data_types import AppData
from validation import validate_data
from .assignments import Assignment
from .managers import Manager
from .projects import Project


@dataclass(frozen=True)
class Catalog:
    """Объекты одного чтения JSON; связанные записи используют одни объекты."""

    projects: tuple[Project, ...]
    managers: tuple[Manager, ...]
    assignments: tuple[Assignment, ...]

    @classmethod
    def from_data(cls, data: AppData) -> "Catalog":
        """Проверить данные и восстановить ссылки назначений на объекты."""
        validate_data(data)
        projects = {
            item["id"]: Project(
                item["id"], item["name"], item["specialization"]
            ) for item in data["projects"]
        }
        managers = {
            item["id"]: Manager(
                item["id"], item["name"], item["specialization"],
                item["project_limit"], item["is_active"],
            ) for item in data["managers"]
        }
        assignments = tuple(
            Assignment(
                id=item["id"],
                project=projects[item["project_id"]],
                manager=managers[item["manager_id"]],
                assigned_on=date.fromisoformat(item["assigned_on"]),
                is_cancelled=item["is_cancelled"],
                cancelled_on=(
                    date.fromisoformat(item["cancelled_on"])
                    if item.get("cancelled_on") else None
                ),
            ) for item in data["assignments"]
        )
        return cls(tuple(projects.values()), tuple(managers.values()),
                   assignments)

    def to_data(self) -> AppData:
        """Создать независимые записи для общих функций правил и хранилища."""
        return {
            "projects": [item.to_dict() for item in self.projects],
            "managers": [item.to_dict() for item in self.managers],
            "assignments": [item.to_dict() for item in self.assignments],
        }

    def find_project(self, project_id: int) -> Project | None:
        """Найти проект по ID или вернуть None."""
        return next((p for p in self.projects if p.id == project_id), None)

    def find_manager(self, manager_id: int) -> Manager | None:
        """Найти руководителя по ID или вернуть None."""
        return next((m for m in self.managers if m.id == manager_id), None)

    def find_assignment(self, assignment_id: int) -> Assignment | None:
        """Найти назначение по ID или вернуть None."""
        return next(
            (a for a in self.assignments if a.id == assignment_id), None
        )

    def active_assignment(self, project_id: int) -> Assignment | None:
        """Получить действующее назначение проекта."""
        return next((a for a in self.assignments
                     if a.project.id == project_id and not a.is_cancelled),
                    None)

    def manager_load(self, manager_id: int) -> int:
        """Использовать тот же расчёт нагрузки, что и консольная версия."""
        records = [item.to_dict() for item in self.assignments]
        return get_manager_load(records, manager_id)

    def rejection_reason(self, project_id: int, manager_id: int) -> str:
        """Проверить возможность назначения по общим правилам проекта."""
        data = self.to_data()
        return check_assignment(
            data["projects"], data["managers"], data["assignments"],
            project_id, manager_id,
        )

    def suitable_managers(self, project_id: int) -> tuple[Manager, ...]:
        """Подобрать кандидатов и отсортировать по текущей нагрузке."""
        data = self.to_data()
        records = find_suitable_managers(
            data["projects"], data["managers"], data["assignments"],
            project_id,
        )
        ids = {item["id"] for item in records}
        return tuple(sorted(
            (manager for manager in self.managers if manager.id in ids),
            key=lambda manager: (
                self.manager_load(manager.id), manager.name.casefold(),
                manager.id,
            ),
        ))
