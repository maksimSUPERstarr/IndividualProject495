"""Объект руководителя с индивидуальным лимитом нагрузки."""

from dataclasses import asdict, dataclass

from data_types import Record


@dataclass(frozen=True)
class Manager:
    """Руководитель; фактическая нагрузка вычисляется по назначениям."""

    id: int
    name: str
    specialization: str
    project_limit: int
    is_active: bool = True

    def to_dict(self) -> Record:
        """Вернуть запись совместимого с ПР2 формата."""
        return asdict(self)
