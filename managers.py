"""Функции работы с руководителями, представленными словарями."""

from data_types import Record, Records
from utils import find_by_id, next_id, require_text


def add_manager(
    managers: Records,
    name: str,
    specialization: str,
    project_limit: int,
    is_active: bool = True,
) -> Record:
    """Добавить руководителя с положительным индивидуальным лимитом."""
    if type(project_limit) is not int or project_limit <= 0:
        raise ValueError("Лимит проектов должен быть положительным целым.")
    if type(is_active) is not bool:
        raise ValueError("Доступность руководителя должна быть bool.")
    manager = {
        "id": next_id(managers),
        "name": require_text(name, "имя руководителя"),
        "specialization": require_text(specialization, "специализация"),
        "project_limit": project_limit,
        "is_active": is_active,
    }
    managers.append(manager)
    return manager


def find_manager_by_id(managers: Records, manager_id: int) -> Record | None:
    """Найти руководителя по числовому ID."""
    return find_by_id(managers, manager_id)


def find_managers(managers: Records, query: str) -> Records:
    """Найти руководителей по подстроке имени без учёта регистра."""
    query = require_text(query, "поисковый запрос").casefold()
    return [item for item in managers if query in item["name"].casefold()]
