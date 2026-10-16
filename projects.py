"""Функции работы с проектами, представленными списком словарей."""

from data_types import Record, Records
from utils import find_by_id, next_id, require_text


def add_project(
    projects: Records, name: str, specialization: str
) -> Record:
    """Проверить поля и добавить проект с новым числовым ID."""
    project = {
        "id": next_id(projects),
        "name": require_text(name, "название проекта"),
        "specialization": require_text(specialization, "направление"),
    }
    projects.append(project)
    return project


def find_project_by_id(projects: Records, project_id: int) -> Record | None:
    """Найти проект по идентификатору."""
    return find_by_id(projects, project_id)


def find_projects(projects: Records, query: str) -> Records:
    """Найти проекты по подстроке названия без учёта регистра."""
    query = require_text(query, "поисковый запрос").casefold()
    return [item for item in projects if query in item["name"].casefold()]
