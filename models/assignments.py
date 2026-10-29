"""Назначение связывает экземпляры проекта и руководителя."""

from dataclasses import dataclass
from datetime import date

from data_types import Record
from .managers import Manager
from .projects import Project


@dataclass(frozen=True)
class Assignment:
    """Неизменяемый снимок назначения, включая историю отмены."""

    id: int
    project: Project
    manager: Manager
    assigned_on: date
    is_cancelled: bool = False
    cancelled_on: date | None = None

    @property
    def status(self) -> str:
        """Получить понятное пользователю название статуса."""
        return "Отменено" if self.is_cancelled else "Действует"

    def to_dict(self) -> Record:
        """Сериализовать связи через ID, даты через ISO 8601."""
        return {
            "id": self.id,
            "project_id": self.project.id,
            "manager_id": self.manager.id,
            "assigned_on": self.assigned_on.isoformat(),
            "is_cancelled": self.is_cancelled,
            "cancelled_on": (
                self.cancelled_on.isoformat() if self.cancelled_on else None
            ),
        }
