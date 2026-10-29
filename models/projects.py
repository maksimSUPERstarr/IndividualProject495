"""Объект проекта из общего JSON-хранилища."""

from dataclasses import asdict, dataclass

from data_types import Record


@dataclass(frozen=True)
class Project:
    """Проект с направлением, определяющим подходящих руководителей."""

    id: int
    name: str
    specialization: str

    def to_dict(self) -> Record:
        """Подготовить запись для существующих функций консольной версии."""
        return asdict(self)
